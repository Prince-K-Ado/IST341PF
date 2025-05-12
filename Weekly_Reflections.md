# Weekly Progress Update

This week marked significant progress in developing the Automated Email Assistant. Initial exploration of API integrations went smoothly, and I successfully connected the system to the Notion API, OpenAI’s GPT-4 API, and the Gmail API. I managed to design and implement a full three-step workflow—Draft, Refine, and Approve & Send—within a responsive web application using Flask, Vanilla JavaScript, and a modern CSS interface. Email drafts are now being generated using GPT-4 with clean, professional language, and users can interactively refine drafts via a chat interface before approving and sending emails directly through Gmail. Sent emails are logged and tracked in both the Notion database and within the application’s “Sent Logs” section.

However, the Gmail API presented more friction than expected, particularly around authentication and OAuth token management. After some exploration, I realized that improper handling of the refresh token and sender email domain authentication led to emails being flagged as spam or phishing attempts. Addressing this required deeper configuration of SPF, DKIM, and DMARC settings, which added some unexpected time to the process. Additionally, I had to upgrade my usage of the OpenAI API client to the latest version to avoid deprecated method calls, which initially caused compatibility issues.

# System Overview

The system is currently functional and covers the full email lifecycle:

Fetching draft entries from Notion based on status.

Using GPT-4 to generate and refine email drafts with user-provided prompts.

Approving and sending finalized emails through Gmail using OAuth.

Logging sent emails back to Notion and displaying a history in the web app.

The current UI offers a smooth workflow through dropdown selection, draft visualization, a refinement chat box, and a final approval step. Sent logs are displayed in a clean, searchable table.

Work that remains includes automating follow-up reminders for emails without a response after two days and improving the anti-spam characteristics of sent emails. While the core logic is stable, I plan to add better error handling for edge cases (e.g., expired Gmail tokens or malformed prompts).

# Proposal & Next Steps

This week’s experience refined my project goals to focus more heavily on real-world deliverability and user experience. While I initially focused mostly on API integration, I now realize that ensuring emails are not flagged as spam is equally critical for success.

For the coming week, I plan to:

- Implement automated follow-up reminders using scheduled background tasks.

- Improve email deliverability through verified domain configurations.

- Add filtering and search functionality to the Sent Logs UI.

- Start working on a basic analytics dashboard to track email success rates and interactions.

If I could re-run this week, I would have tackled email deliverability earlier and allocated more time for testing authentication flows. Overall, the process has been very insightful, and while the technical hurdles were sometimes frustrating, they led to a much deeper understanding of production-grade email systems. The project is on track, and I’m excited to enhance the app’s robustness and polish over the next development cycle.
