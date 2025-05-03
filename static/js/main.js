// static/js/main.js

console.log("✅ main.js loaded");

// Holds the current draft for refinement & approval
let currentDraft = null;

// Wire up event listeners on page load
window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('draft-button')
          .addEventListener('click', handleGenerateDraft);

  document.getElementById('chat-send-button')
          .addEventListener('click', handleChatSend);

  document.getElementById('approve-button')
          .addEventListener('click', approveEmail);

  // Optional: refresh dropdown & logs if entries/logs endpoints exist
  loadEntries();
  loadLogs();
});


/** Load new entries into the <select> dropdown */
async function loadEntries() {
  try {
    const res = await fetch('/entries');
    const entries = await res.json();
    const selectEl = document.getElementById('entry-select');
    selectEl.innerHTML = entries.map(e => `
      <option value="${e.page_id}"
              data-recipient="${e.recipient_email}"
              data-category="${e.category}"
              data-job="${e.job_description.replace(/"/g,'&quot;')}">
        ${e.recipient_email} — ${e.category}
      </option>
    `).join('');
  } catch (err) {
    console.error('❌ loadEntries error:', err);
  }
}


/** 1) Generate a draft from ChatGPT */
async function handleGenerateDraft() {
  const selectEl = document.getElementById('entry-select');
  const opt      = selectEl.selectedOptions[0];
  if (!opt) {
    alert('Please select an entry first.');
    return;
  }

  const page_id         = opt.value;
  const recipient_email = opt.dataset.recipient;
  const category        = opt.dataset.category;
  const job_description = opt.dataset.job;

  const customPrompt = prompt('Enter your custom prompt:');
  if (!customPrompt) return;

  try {
    console.log('➡️ POST /draft_email', {
      page_id, recipient_email, category, job_description, prompt: customPrompt
    });

    const res  = await fetch('/draft_email', {
      method: 'POST',
      headers: { 'Content-Type':'application/json' },
      body: JSON.stringify({
        page_id,
        recipient_email,
        category,
        job_description,
        prompt: customPrompt
      })
    });

    const data = await res.json();
    console.log('⬅️ /draft_email response', res.status, data);

    if (!res.ok) {
      throw new Error(data.error || `HTTP ${res.status}`);
    }

    // Show the generated draft
    const draftEl = document.getElementById('draft-body');
    if (!draftEl) throw new Error('No #draft-body element found');
    draftEl.value = data.email_body;

    // Save for refinement & approval
    currentDraft = {
      page_id,
      recipient: recipient_email,
      category,
      job_description,
      subject: data.subject || category,
      body: data.email_body,
    };

    // Clear any previous chat messages
    document.getElementById('chat-output').innerHTML = '';
  } catch (err) {
    console.error('❌ handleGenerateDraft error:', err);
    alert(`Draft generation failed:\n${err.message}`);
  }
}


/** 2) Refine the draft via ChatGPT */
async function handleChatSend() {
  if (!currentDraft) {
    alert('Generate a draft first.');
    return;
  }

  const userText = document.getElementById('chat-input').value.trim();
  if (!userText) return;

  try {
    const res  = await fetch('/refine_draft', {
      method: 'POST',
      headers: { 'Content-Type':'application/json' },
      body: JSON.stringify({
        page_id:    currentDraft.page_id,
        body:       currentDraft.body,
        refinement: userText
      })
    });

    const data = await res.json();
    console.log('⬅️ /refine_draft response', res.status, data);

    if (!res.ok) {
      throw new Error(data.error || `HTTP ${res.status}`);
    }

    // Append the chat exchange
    const chatOut = document.getElementById('chat-output');
    chatOut.innerHTML += `
      <p><strong>You:</strong> ${userText}</p>
      <p><strong>GPT:</strong> ${data.email_body.replace(/\n/g,'<br>')}</p>
    `;

    // Update the draft body
    currentDraft.body = data.email_body;
    document.getElementById('chat-input').value = '';
  } catch (err) {
    console.error('❌ handleChatSend error:', err);
    alert(`Refinement failed:\n${err.message}`);
  }
}


/** 3) Approve & send the current draft */
async function approveEmail() {
  if (!currentDraft) {
    alert('Nothing to approve.');
    return;
  }

  try {
    console.log('🔔 POST /approve_email', { page_id: currentDraft.page_id });

    const res  = await fetch('/approve_email', {
      method: 'POST',
      headers: { 'Content-Type':'application/json' },
      body: JSON.stringify({ page_id: currentDraft.page_id })
    });

    const data = await res.json();
    console.log('📬 /approve_email response', res.status, data);

    if (!res.ok) {
      throw new Error(data.error || `HTTP ${res.status}`);
    }

    alert(data.message);

    // Clear UI & reload data
    document.getElementById('draft-body').value = '';
    document.getElementById('chat-output').innerHTML = '';
    currentDraft = null;

    loadEntries();
    loadLogs();
  } catch (err) {
    console.error('❌ approveEmail error:', err);
    alert(`Send failed:\n${err.message}`);
  }
}


/** 4) Load “Sent Logs” from Notion */
async function loadLogs() {
  try {
    const res  = await fetch('/logs');
    const logs = await res.json();
    const c    = document.getElementById('logs-container');

    if (!logs.length) {
      c.innerHTML = '<p>No emails sent yet.</p>';
      return;
    }

    c.innerHTML = `
      <table class="table">
        <thead>
          <tr>
            <th>Date Sent</th>
            <th>Recipient</th>
            <th>Subject</th>
            <th>Final Draft</th>
          </tr>
        </thead>
        <tbody>
          ${logs.map(l => `
            <tr>
              <td>${l.date_sent}</td>
              <td>${l.recipient}</td>
              <td>${l.subject}</td>
              <td>${l.final_body.replace(/\n/g,'<br>')}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  } catch (err) {
    console.error('❌ loadLogs error:', err);
    document.getElementById('logs-container')
            .innerHTML = '<p>Failed to load logs.</p>';
  }
}
