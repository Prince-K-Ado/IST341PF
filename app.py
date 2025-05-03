import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from chatgpt_service import generate_email, refine_email
from google_service import send_email
from notion_service import get_new_entries, get_sent_entries, update_notion_after_send

# Load .env
load_dotenv()

app = Flask(__name__)

# In‐memory store for drafts awaiting approval
draft_emails = {}


@app.route('/')
def index():
    """
    Server‐render the main page with the list of new (To-do) entries.
    We’ll fetch 'sent' logs via JS from /logs.
    """
    entries = get_new_entries()
    return render_template('index.html', entries=entries)


@app.route('/entries')
def entries_api():
    """
    Return JSON of new (To-do) entries for client‐side refresh.
    """
    rows = get_new_entries()
    return jsonify([
        {
            'page_id':         r['page_id'],
            'recipient_email': r['recipient_email'],
            'category':        r['category'],
            'job_description': r['job_description']
        }
        for r in rows
    ])


@app.route('/draft_email', methods=['POST'])
def draft_email():
    """
    Generate a GPT draft for the selected entry.
    Stores (subject, body, recipient) in memory for later approval.
    """
    data            = request.json or {}
    page_id         = data.get('page_id', '').strip()
    category        = data.get('category', '')
    job_description = data.get('job_description', '')
    recipient_email = data.get('recipient_email', '')
    custom_prompt   = data.get('prompt', '')

    try:
        subject, body = generate_email(category, custom_prompt, job_description)
    except Exception as e:
        return jsonify({'error': f'Generation failed: {e}'}), 500

    draft_emails[page_id] = {
        'recipient': recipient_email,
        'subject':   subject,
        'body':      body
    }

    return jsonify({'subject': subject, 'email_body': body})


@app.route('/refine_draft', methods=['POST'])
def refine_draft():
    """
    Refine an existing draft with a user instruction.
    Updates the in‐memory draft body.
    """
    data       = request.json or {}
    page_id    = data.get('page_id', '').strip()
    original   = data.get('body', '')
    refinement = data.get('refinement', '')

    if page_id not in draft_emails:
        return jsonify({'error': 'Draft not found'}), 404

    try:
        new_body = refine_email(original, refinement)
        draft_emails[page_id]['body'] = new_body
        return jsonify({'email_body': new_body})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/approve_email', methods=['POST'])
def approve_email():
    """
    Send the approved draft via Gmail and update Notion.
    """
    data    = request.json or {}
    page_id = data.get('page_id', '').strip()
    draft   = draft_emails.get(page_id)

    if not draft:
        return jsonify({'error': 'Draft not found'}), 404

    to      = draft['recipient']
    subject = draft['subject']
    body    = draft['body']

    try:
        # 1) Send email
        send_email(to=to, subject=subject, body=body)
        # 2) Update Notion
        update_notion_after_send(page_id, subject, body)
    except Exception as e:
        return jsonify({'error': f'Send/update failed: {e}'}), 500

    # 3) Clean up
    del draft_emails[page_id]
    return jsonify({'message': 'Email sent & Notion updated!'})


@app.route('/logs')
def logs_api():
    """
    Return JSON of sent entries from Notion for the Sent Logs table.
    """
    rows = get_sent_entries()
    return jsonify(rows)


if __name__ == '__main__':
    app.run(debug=True)
