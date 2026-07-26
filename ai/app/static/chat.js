/**
 * Outback-Safe USB — Offline AI Assistant Chat Client
 * Zero external dependencies. Safari 15+ compatible.
 * SSE streaming, localStorage persistence, keyboard shortcuts.
 */
(function () {
  'use strict';

  // =========================================================================
  // DOM REFERENCES
  // =========================================================================
  const chatMessages = document.getElementById('chatMessages');
  const chatInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const stopBtn = document.getElementById('stopBtn');
  const regenerateBtn = document.getElementById('regenerateBtn');
  const clearChatBtn = document.getElementById('clearChatBtn');
  const kbToggleBtn = document.getElementById('kbToggleBtn');
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const printBtn = document.getElementById('printBtn');
  const sidebar = document.getElementById('sidebar');
  const sidebarCloseBtn = document.getElementById('sidebarCloseBtn');
  const modelStatus = document.getElementById('modelStatusText');
  const modelStatusDot = document.querySelector('#modelStatus .status-dot');
  const pageCountEl = document.getElementById('pageCount');

  // =========================================================================
  // STATE
  // =========================================================================
  const STORAGE_KEY = 'shtf_chat_history';
  const MAX_HISTORY = 20;
  const STATUS_POLL_MS = 2000;

  let conversationHistory = [];
  let modelReady = false;
  let currentAbortController = null;
  let isGenerating = false;

  // =========================================================================
  // CONVERSATION HISTORY (localStorage)
  // =========================================================================
  function loadHistory() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        conversationHistory = JSON.parse(raw);
        if (!Array.isArray(conversationHistory)) conversationHistory = [];
        // Trim to MAX_HISTORY exchanges (each exchange = user + ai pair)
        if (conversationHistory.length > MAX_HISTORY * 2) {
          conversationHistory = conversationHistory.slice(-MAX_HISTORY * 2);
        }
      }
    } catch (e) {
      conversationHistory = [];
    }
  }

  function saveHistory() {
    try {
      const trimmed = conversationHistory.slice(-MAX_HISTORY * 2);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
    } catch (e) {
      // localStorage full or unavailable — silently fail
    }
  }

  function restoreHistoryToDOM() {
    conversationHistory.forEach(function (entry) {
      renderMessage(entry.role, entry.text);
    });
  }

  // =========================================================================
  // RENDERING
  // =========================================================================
  function escapeHTML(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function renderMarkdown(text) {
    // Escape HTML first
    var escaped = escapeHTML(text);

    // Source citations: [source: Title|url]
    escaped = escaped.replace(
      /\[source:\s*(.+?)\|(.+?)\]/g,
      function (match, title, url) {
        return '<span class="source-citation">📄 <a href="/outback-safe/' +
          escapeHTML(url.trim()) +
          '" target="_blank" rel="noopener">' +
          escapeHTML(title.trim()) +
          '</a></span>';
      }
    );

    // Bold: **text**
    escaped = escaped.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Inline code: `text`
    escaped = escaped.replace(/`(.+?)`/g, '<code>$1</code>');

    // Line breaks
    escaped = escaped.replace(/\n/g, '<br>');

    return escaped;
  }

  function renderMessage(role, text) {
    var msgDiv = document.createElement('div');
    msgDiv.className = 'message ' + role;

    var bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    if (role === 'ai') {
      bubble.innerHTML = '<div class="procedure">' + renderMarkdown(text) + '</div>';
    } else {
      bubble.textContent = text;
    }

    msgDiv.appendChild(bubble);
    chatMessages.appendChild(msgDiv);
    scrollToBottom();
  }

  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // =========================================================================
  // SSE STREAMING
  // =========================================================================
  function sendMessage(question) {
    if (!modelReady || isGenerating) return;
    if (!question || !question.trim()) return;

    var text = question.trim();

    // Add user message to DOM
    renderMessage('user', text);

    // Add to history
    conversationHistory.push({ role: 'user', text: text });

    // Create AI message placeholder
    var aiMsgDiv = document.createElement('div');
    aiMsgDiv.className = 'message ai';
    var aiBubble = document.createElement('div');
    aiBubble.className = 'message-bubble';
    aiBubble.innerHTML = '<div class="procedure"></div>';
    aiMsgDiv.appendChild(aiBubble);
    chatMessages.appendChild(aiMsgDiv);

    var aiContentDiv = aiBubble.querySelector('.procedure');
    var fullResponse = '';

    // Disable UI during generation
    isGenerating = true;
    updateInputState();

    currentAbortController = new AbortController();
    var signal = currentAbortController.signal;

    fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text,
        history: conversationHistory.slice(0, -1), // exclude the just-added user message
        units: unitPref  // 'metric' or 'imperial'
      }),
      signal: signal
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error('Server responded with ' + response.status);
        }

        var reader = response.body.getReader();
        var decoder = new TextDecoder();
        var buffer = '';

        function readStream() {
          reader.read().then(function (result) {
            if (result.done) {
              // Stream complete
              finishResponse(aiBubble, aiContentDiv, fullResponse, aiMsgDiv);
              return;
            }

            buffer += decoder.decode(result.value, { stream: true });
            var lines = buffer.split('\n');
            // Keep the last partial line in the buffer
            buffer = lines.pop();

            for (var i = 0; i < lines.length; i++) {
              var line = lines[i].trim();
              if (line.startsWith('data: ')) {
                var chunk = line.slice(6);
                if (chunk === '[DONE]') {
                  finishResponse(aiBubble, aiContentDiv, fullResponse, aiMsgDiv);
                  return;
                }
                // Handle JSON-encoded chunks
                try {
                  var parsed = JSON.parse(chunk);
                  if (parsed.text) {
                    fullResponse += parsed.text;
                    aiContentDiv.innerHTML = renderMarkdown(fullResponse);
                    scrollToBottom();
                  }
                } catch (e) {
                  // Plain text chunk
                  fullResponse += chunk;
                  aiContentDiv.innerHTML = renderMarkdown(fullResponse);
                  scrollToBottom();
                }
              }
            }

            readStream();
          }).catch(function (err) {
            if (err.name === 'AbortError') {
              finishResponse(aiBubble, aiContentDiv, fullResponse, aiMsgDiv, true);
              return;
            }
            handleStreamError(aiBubble, aiContentDiv, err, aiMsgDiv);
          });
        }

        readStream();
      })
      .catch(function (err) {
        if (err.name === 'AbortError') {
          finishResponse(aiBubble, aiContentDiv, fullResponse, aiMsgDiv, true);
          return;
        }
        handleStreamError(aiBubble, aiContentDiv, err, aiMsgDiv);
      });
  }

  function finishResponse(bubble, contentDiv, fullResponse, msgDiv, wasStopped) {
    if (fullResponse) {
      conversationHistory.push({ role: 'ai', text: fullResponse });
      saveHistory();
    } else if (!wasStopped) {
      contentDiv.innerHTML = '<em>No response generated.</em>';
    }

    if (wasStopped && fullResponse) {
      // Show a subtle indicator that generation was stopped
      var note = document.createElement('div');
      note.style.cssText = 'font-size:0.75em;color:var(--text-muted);margin-top:6px;font-style:italic;';
      note.textContent = '⏹ Generation stopped.';
      bubble.appendChild(note);
    }

    isGenerating = false;
    currentAbortController = null;
    updateInputState();
    scrollToBottom();
  }

  function handleStreamError(bubble, contentDiv, err, msgDiv) {
    contentDiv.innerHTML = '<em style="color:var(--danger);">Error: ' +
      escapeHTML(err.message || 'Connection failed') + '</em>';
    isGenerating = false;
    currentAbortController = null;
    updateInputState();
    scrollToBottom();
  }

  function stopGeneration() {
    if (currentAbortController) {
      currentAbortController.abort();
      currentAbortController = null;
    }
  }

  function regenerateLast() {
    if (isGenerating || !modelReady) return;

    // Find the last user message in history
    var lastUserMsg = null;
    for (var i = conversationHistory.length - 1; i >= 0; i--) {
      if (conversationHistory[i].role === 'user') {
        lastUserMsg = conversationHistory[i].text;
        break;
      }
    }

    if (!lastUserMsg) return;

    // Remove the last AI response from history if it exists
    if (conversationHistory.length > 0 &&
        conversationHistory[conversationHistory.length - 1].role === 'ai') {
      conversationHistory.pop();
    }

    // Remove the last AI message from DOM
    var messages = chatMessages.querySelectorAll('.message.ai');
    if (messages.length > 0) {
      messages[messages.length - 1].remove();
    }

    // Re-send
    sendMessage(lastUserMsg);
  }

  function clearChat() {
    stopGeneration();
    chatMessages.innerHTML = '';

    // Add welcome message back
    var welcomeDiv = document.createElement('div');
    welcomeDiv.className = 'message ai';
    var welcomeBubble = document.createElement('div');
    welcomeBubble.className = 'message-bubble';
    welcomeBubble.innerHTML =
      '<p>Welcome to Outback-Safe USB Assistant. I can answer questions from the offline knowledge base.</p>' +
      '<p>Ask about first aid, survival skills, emergency procedures, or any topic in the library.</p>';
    welcomeDiv.appendChild(welcomeBubble);
    chatMessages.appendChild(welcomeDiv);

    conversationHistory = [];
    saveHistory();
    chatInput.value = '';
    chatInput.focus();
  }

  function updateInputState() {
    if (modelReady && !isGenerating) {
      chatInput.disabled = false;
      chatInput.placeholder = 'Ask a question…';
      sendBtn.disabled = false;
      chatInput.focus();
    } else if (!modelReady) {
      chatInput.disabled = true;
      chatInput.placeholder = '⏳ AI is loading… (~2\u20133 min first start)';
      sendBtn.disabled = true;
    } else if (isGenerating) {
      chatInput.disabled = false;
      chatInput.placeholder = 'AI is responding…';
      sendBtn.disabled = true;
    }
  }

  // =========================================================================
  // MODEL STATUS POLLING
  // =========================================================================
  function pollModelStatus() {
    fetch('/api/status')
      .then(function (response) {
        if (!response.ok) throw new Error('Status check failed');
        return response.json();
      })
      .then(function (data) {
        if (data.model_loaded) {
          setModelReady(data);
        } else {
          setModelLoading(data);
          setTimeout(pollModelStatus, STATUS_POLL_MS);
        }
      })
      .catch(function () {
        // Server not reachable yet — keep polling
        setModelLoading(null);
        setTimeout(pollModelStatus, STATUS_POLL_MS);
      });
  }

  function setModelReady(data) {
    modelReady = true;
    if (modelStatusDot) {
      modelStatusDot.classList.remove('loading');
      modelStatusDot.classList.add('ready');
    }
    if (modelStatus) {
      var modelName = (data && data.model) ? data.model : 'Model';
      modelStatus.textContent = '🟢 ' + modelName + ' ready';
    }
    if (pageCountEl && data && data.page_count !== undefined) {
      pageCountEl.textContent = '📚 ' + data.page_count + ' pages indexed';
    } else if (pageCountEl && data === null) {
      pageCountEl.textContent = '📚 — pages indexed';
    }
    updateInputState();
  }

  function setModelLoading(data) {
    modelReady = false;
    if (modelStatusDot) {
      modelStatusDot.classList.add('loading');
      modelStatusDot.classList.remove('ready');
    }
    if (modelStatus) {
      modelStatus.textContent = '🟡 Loading model…';
    }
    if (pageCountEl && data && data.page_count !== undefined) {
      pageCountEl.textContent = '📚 ' + data.page_count + ' pages indexed';
    }
    updateInputState();
  }

  // =========================================================================
  // KEYBOARD SHORTCUTS
  // =========================================================================
  document.addEventListener('keydown', function (e) {
    // Emergency tiles: 1-6 (only when not typing in textarea or other input)
    if (!e.ctrlKey && !e.metaKey && !e.altKey) {
      var tag = document.activeElement ? document.activeElement.tagName : '';
      var isInput = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT';

      if (!isInput && e.key >= '1' && e.key <= '6') {
        e.preventDefault();
        var tile = document.getElementById('tile' + e.key);
        if (tile) {
          window.location.href = tile.href;
        }
        return;
      }

      // Escape: Stop generation
      if (e.key === 'Escape') {
        e.preventDefault();
        stopGeneration();
        chatInput.focus();
        return;
      }
    }

    // Enter: Send (Ctrl+Enter for newline)
    if (e.key === 'Enter' && document.activeElement === chatInput) {
      if (e.ctrlKey || e.metaKey) {
        // Allow newline
        return;
      }
      e.preventDefault();
      var text = chatInput.value;
      if (text.trim()) {
        sendMessage(text);
        chatInput.value = '';
      }
    }
  });

  // =========================================================================
  // BUTTON EVENT HANDLERS
  // =========================================================================

  // Send button
  sendBtn.addEventListener('click', function () {
    var text = chatInput.value;
    if (text.trim() && modelReady && !isGenerating) {
      sendMessage(text);
      chatInput.value = '';
    }
  });

  // Stop button
  stopBtn.addEventListener('click', function () {
    stopGeneration();
  });

  // Regenerate button
  regenerateBtn.addEventListener('click', function () {
    regenerateLast();
  });

  // Clear Chat button
  clearChatBtn.addEventListener('click', function () {
    clearChat();
  });

  // Knowledge Base toggle
  kbToggleBtn.addEventListener('click', function () {
    sidebar.classList.toggle('hidden');
    // Update button text
    if (sidebar.classList.contains('hidden')) {
      kbToggleBtn.innerHTML = '📁 Knowledge Base';
    } else {
      kbToggleBtn.innerHTML = '📁 Hide Sidebar';
    }
  });

  // Sidebar close button
  if (sidebarCloseBtn) {
    sidebarCloseBtn.addEventListener('click', function () {
      sidebar.classList.add('hidden');
      kbToggleBtn.innerHTML = '📁 Knowledge Base';
    });
  }

  // Theme toggle
  themeToggleBtn.addEventListener('click', function () {
    var html = document.documentElement;
    var currentTheme = html.getAttribute('data-theme');
    if (currentTheme === 'high-contrast') {
      html.setAttribute('data-theme', 'dark');
      themeToggleBtn.innerHTML = '☀️ High Contrast';
      try { localStorage.setItem('shtf_theme', 'dark'); } catch (e) {}
    } else {
      html.setAttribute('data-theme', 'high-contrast');
      themeToggleBtn.innerHTML = '🌙 Dark Mode';
      try { localStorage.setItem('shtf_theme', 'high-contrast'); } catch (e) {}
    }
  });

  // Units toggle
  var unitPref = 'metric';
  try { unitPref = localStorage.getItem('shtf_units') || 'metric'; } catch (e) {}
  var unitsBtn = document.getElementById('unitsToggleBtn');
  if (!unitsBtn) return;  // Guard: button may not exist yet
  function updateUnitsBtn() {
    unitsBtn.innerHTML = unitPref === 'metric' ? '📏 Metric' : '📏 Imperial';
  }
  updateUnitsBtn();
  unitsBtn.addEventListener('click', function () {
    unitPref = unitPref === 'metric' ? 'imperial' : 'metric';
    try { localStorage.setItem('shtf_units', unitPref); } catch (e) {}
    updateUnitsBtn();
  });

  // Print button
  printBtn.addEventListener('click', function () {
    window.print();
  });

  // =========================================================================
  // INITIALIZATION
  // =========================================================================
  function init() {
    // Restore theme preference
    try {
      var savedTheme = localStorage.getItem('shtf_theme');
      if (savedTheme === 'high-contrast') {
        document.documentElement.setAttribute('data-theme', 'high-contrast');
        themeToggleBtn.innerHTML = '🌙 Dark Mode';
      }
    } catch (e) {}

    // Load conversation history from localStorage
    loadHistory();
    restoreHistoryToDOM();

    // Set initial input state
    updateInputState();

    // Focus input
    chatInput.focus();

    // Start polling model status
    pollModelStatus();
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
