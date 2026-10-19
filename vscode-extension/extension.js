const vscode = require('vscode');

class SageViewProvider {
  static viewType = 'sage.chatView';

  resolveWebviewView(webviewView) {
    webviewView.webview.options = { enableScripts: true };
    webviewView.webview.html = `<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="UTF-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; connect-src http://127.0.0.1:5001; script-src 'unsafe-inline'; style-src 'unsafe-inline';">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--vscode-editor-background);
    color: var(--vscode-editor-foreground);
    height: 100vh;
    display: flex;
    flex-direction: column;
    border-right: 1px solid var(--vscode-focusBorder);
  }
  #header {
    padding: 8px 12px;
    background: var(--vscode-sideBarSectionHeader-background);
    border-bottom: 1px solid var(--vscode-panel-border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--vscode-sideBarSectionHeader-foreground);
  }
  #reset-btn {
    background: none;
    border: 1px solid var(--vscode-button-border, #555);
    color: var(--vscode-descriptionForeground);
    padding: 2px 8px;
    border-radius: 3px;
    cursor: pointer;
    font-size: 11px;
    text-transform: none;
    letter-spacing: 0;
  }
  #reset-btn:hover { opacity: 0.8; }
  #messages {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .msg {
    padding: 7px 10px;
    border-radius: 5px;
    font-size: 12px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-word;
  }
  .msg.user {
    align-self: flex-end;
    background: var(--vscode-button-background);
    color: var(--vscode-button-foreground);
    max-width: 85%;
  }
  .msg.assistant {
    align-self: flex-start;
    background: var(--vscode-input-background);
    border: 1px solid var(--vscode-panel-border);
    max-width: 95%;
  }
  .msg.thinking {
    align-self: flex-start;
    color: var(--vscode-descriptionForeground);
    font-style: italic;
    font-size: 11px;
  }
  #offline {
    display: none;
    margin: 12px;
    padding: 8px 12px;
    background: var(--vscode-inputValidation-warningBackground);
    border: 1px solid var(--vscode-inputValidation-warningBorder);
    border-radius: 4px;
    font-size: 12px;
  }
  #input-area {
    padding: 8px 12px;
    background: var(--vscode-sideBar-background);
    border-top: 1px solid var(--vscode-panel-border);
    display: flex;
    gap: 6px;
  }
  #input {
    flex: 1;
    background: var(--vscode-input-background);
    border: 1px solid var(--vscode-input-border, #555);
    color: var(--vscode-input-foreground);
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 12px;
    resize: none;
    height: 34px;
    max-height: 100px;
    font-family: inherit;
    outline: none;
  }
  #input:focus { border-color: var(--vscode-focusBorder); }
  #send-btn {
    background: var(--vscode-button-background);
    border: none;
    color: var(--vscode-button-foreground);
    padding: 0 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
  }
  #send-btn:hover { background: var(--vscode-button-hoverBackground); }
  #send-btn:disabled { opacity: 0.5; cursor: default; }
</style>
</head>
<body>
<div id="header">
  <span>Sage</span>
  <button id="reset-btn" onclick="resetChat()">Ny chatt</button>
</div>
<div id="offline">Sage är offline — starta servern: <code>python chat_ui.py</code></div>
<div id="messages"></div>
<div id="input-area">
  <textarea id="input" placeholder="Fråga Sage..."></textarea>
  <button id="send-btn" onclick="sendMessage()">&#9650;</button>
</div>
<script>
  const BASE = 'http://127.0.0.1:5001';
  const messagesEl = document.getElementById('messages');
  const inputEl = document.getElementById('input');
  const sendBtn = document.getElementById('send-btn');
  const offlineEl = document.getElementById('offline');

  function addMessage(text, role) {
    const div = document.createElement('div');
    div.className = 'msg ' + role;
    div.textContent = text;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return div;
  }

  async function sendMessage() {
    const text = inputEl.value.trim();
    if (!text || sendBtn.disabled) return;
    inputEl.value = '';
    inputEl.style.height = '34px';
    addMessage(text, 'user');
    sendBtn.disabled = true;
    const thinking = addMessage('Tänker...', 'thinking');
    try {
      const res = await fetch(BASE + '/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      thinking.remove();
      offlineEl.style.display = 'none';
      addMessage(data.response, 'assistant');
    } catch {
      thinking.remove();
      offlineEl.style.display = 'block';
    } finally {
      sendBtn.disabled = false;
      inputEl.focus();
    }
  }

  async function resetChat() {
    await fetch(BASE + '/reset', { method: 'POST' }).catch(() => {});
    messagesEl.innerHTML = '';
    addMessage('Ny chatt startad!', 'assistant');
  }

  inputEl.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });
  inputEl.addEventListener('input', () => {
    inputEl.style.height = '34px';
    inputEl.style.height = Math.min(inputEl.scrollHeight, 100) + 'px';
  });

  addMessage('Hej! Jag är Sage. Hur kan jag hjälpa dig?', 'assistant');
</script>
</body>
</html>`;
  }
}

function activate(context) {
  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider('sage.chatView', new SageViewProvider())
  );
}

function deactivate() {}

module.exports = { activate, deactivate };
