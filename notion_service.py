# notion_service.py

import os
from datetime import datetime, timedelta
from notion_client import Client
from notion_client.errors import APIResponseError
from dotenv import load_dotenv

load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID  = os.getenv("NOTION_DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)


def get_new_entries() -> list[dict]:
    """
    Return all pages whose Status is NOT 'Sent'.
    This covers both 'To-do', 'In progress', etc.
    """
    try:
        resp = notion.databases.query(
            database_id=DATABASE_ID,
            filter={
                "property": "Status",
                # does_not_equal picks up anything except 'Sent'
                "status": {"does_not_equal": "Sent"}
            },
            sorts=[{"property": "Date", "direction": "ascending"}]
        )
    except APIResponseError as e:
        print("❌ Notion (get_new_entries) failed:", e)
        return []

    entries = []
    for page in resp.get("results", []):
        props = page.get("properties", {})

        recipient = props.get("Recipient Email", {}).get("email") or ""
        sel_cat   = props.get("Category", {}).get("select")
        category  = sel_cat.get("name") if sel_cat else ""
        jd_list   = props.get("Job Description", {}).get("rich_text", [])
        job_desc  = jd_list[0].get("plain_text") if jd_list else ""

        # only include fully-filled rows
        if recipient and category:
            entries.append({
                "page_id":         page["id"],
                "recipient_email": recipient,
                "category":        category,
                "job_description": job_desc
            })

    return entries


def get_sent_entries() -> list[dict]:
    """
    Return all pages whose Status is 'Sent'.
    """
    try:
        resp = notion.databases.query(
            database_id=DATABASE_ID,
            filter={
                "property": "Status",
                "status":   {"equals": "Sent"}
            },
            sorts=[{"property": "Date", "direction": "descending"}]
        )
    except APIResponseError as e:
        print("❌ Notion (get_sent_entries) failed:", e)
        return []

    logs = []
    for page in resp.get("results", []):
        props = page.get("properties", {})

        date_sent = props.get("Date", {}).get("date", {}).get("start") or ""
        recipient = props.get("Recipient Email", {}).get("email") or ""

        rt_subj = props.get("Email Subject", {}).get("rich_text", [])
        subject = rt_subj[0].get("text", {}).get("content") if rt_subj else ""

        rt_body = props.get("Email Body", {}).get("rich_text", [])
        body    = rt_body[0].get("text", {}).get("content") if rt_body else ""

        logs.append({
            "date_sent":  date_sent,
            "recipient":  recipient,
            "subject":    subject,
            "final_body": body
        })

    return logs


def update_notion_after_send(page_id: str, subject: str, body: str) -> None:
    """
    After sending, update the page:
      - Email Subject, Email Body, Date, Follow-up Date,
      - Status → Sent, Follow-up Status → Pending
    """
    today     = datetime.now().strftime("%Y-%m-%d")
    follow_up = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")

    props = {
        "Email Subject": {
            "rich_text": [{"text": {"content": subject or ""}}]
        },
        "Email Body": {
            "rich_text": [{"text": {"content": body or ""}}]
        },
        "Date": {
            "date": {"start": today}
        },
        "Follow-up Date": {
            "date": {"start": follow_up}
        },
        "Status": {
            "status": {"name": "Sent"}
        },
        "Follow-up Status": {
            "select": {"name": "Pending"}
        }
    }

    try:
        notion.pages.update(page_id=page_id, properties=props)
        print(f"✅ Notion updated for page {page_id}")
    except APIResponseError as e:
        print(f"❌ Notion update failed for page {page_id}:", e)
        if hasattr(e, "body"):
            print("Error body:", e.body)
