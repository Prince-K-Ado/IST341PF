import os
import re
import openai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_email(
    category: str,
    custom_prompt: str,
    job_description: str = ""
) -> tuple[str, str]:
    """
    Ask GPT to draft an email, returning (subject, body).
    Falls back gracefully if the model output doesn't match the exact format.
    """
    prompt = f"""
You are drafting a professional email.

- Category: {category}
- Job Description: {job_description}

Use this custom instruction: {custom_prompt}

Please output exactly in this format:

Subject: <a one-line subject>
Body:
<a polite, well-written email body>
"""
    # Call the Chat Completions endpoint
    resp = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert email writer."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )
    text = resp.choices[0].message.content.strip()

    # Default fallback values
    subject = category
    body = text

    # Try to parse out the subject/body using regex
    try:
        # Extract "Subject: ..." from its own line
        m_sub = re.search(
            r"^[ \t]*Subject\s*:\s*(.+)$",
            text,
            re.IGNORECASE | re.MULTILINE
        )
        if m_sub:
            subject = m_sub.group(1).strip()

        # Extract everything after "Body:"
        m_body = re.search(
            r"Body\s*:\s*(.*)$",
            text,
            re.IGNORECASE | re.DOTALL
        )
        if m_body:
            body = m_body.group(1).strip()
    except Exception as e:
        # If parsing fails, we keep the defaults
        print("⚠️ generate_email parse fallback:", e)

    return subject, body


def refine_email(original_body: str, refinement: str) -> str:
    """
    Given an existing email body and a refinement instruction,
    returns the updated email body from ChatGPT.
    """
    prompt = f"""
You are an expert email writer. Here is the current draft:

{original_body}

Please refine this draft based on the following instruction:
{refinement}

Return only the full, revised email body.
"""
    resp = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system",  "content": "You are an expert email writer."},
            {"role": "user",    "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )
    return resp.choices[0].message.content.strip()
