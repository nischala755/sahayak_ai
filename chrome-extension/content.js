/**
 * SAHAYAK AI Chrome Extension - Content Script
 * Injects floating button and displays playbooks on page
 */

// Create floating SOS button
function createFloatingButton() {
    // Check if button already exists
    if (document.getElementById('sahayak-fab')) return;

    const fab = document.createElement('button');
    fab.id = 'sahayak-fab';
    fab.innerHTML = '🆘';
    fab.title = 'SAHAYAK AI - Get Teaching Help';

    fab.addEventListener('click', () => {
        // Open extension popup
        chrome.runtime.sendMessage({ type: 'OPEN_POPUP' });
    });

    document.body.appendChild(fab);
}

// Create playbook overlay
function createPlaybookOverlay(playbook) {
    // Remove existing overlay
    const existing = document.getElementById('sahayak-overlay');
    if (existing) existing.remove();

    const overlay = document.createElement('div');
    overlay.id = 'sahayak-overlay';
    overlay.className = 'sahayak-overlay';

    overlay.innerHTML = `
    <div class="sahayak-modal">
      <div class="sahayak-modal-header">
        <span class="sahayak-logo">🎓 SAHAYAK AI</span>
        <button class="sahayak-close" id="sahayak-close">&times;</button>
      </div>
      <div class="sahayak-modal-content">
        <h3>${playbook.title || 'Teaching Rescue Playbook'}</h3>
        
        ${playbook.summary ? `
          <div class="sahayak-section">
            <h4>📋 Summary</h4>
            <p>${playbook.summary}</p>
          </div>
        ` : ''}
        
        ${playbook.immediate_actions?.length > 0 ? `
          <div class="sahayak-section">
            <h4>⚡ Do Right Now</h4>
            <ul>
              ${playbook.immediate_actions.map(a => `<li>${a}</li>`).join('')}
            </ul>
          </div>
        ` : ''}
        
        ${playbook.recovery_steps?.length > 0 ? `
          <div class="sahayak-section">
            <h4>📈 Recovery Steps</h4>
            <ul>
              ${playbook.recovery_steps.map(s => `<li>${s}</li>`).join('')}
            </ul>
          </div>
        ` : ''}
      </div>
      <div class="sahayak-modal-footer">
        <button class="sahayak-btn" id="sahayak-copy">📋 Copy</button>
        <button class="sahayak-btn sahayak-btn-primary" id="sahayak-open-app">Open Full App</button>
      </div>
    </div>
  `;

    document.body.appendChild(overlay);

    // Event listeners
    document.getElementById('sahayak-close').addEventListener('click', () => {
        overlay.remove();
    });

    document.getElementById('sahayak-copy').addEventListener('click', () => {
        copyPlaybookText(playbook);
    });

    document.getElementById('sahayak-open-app').addEventListener('click', () => {
        window.open('https://sahayak-ai-xi.vercel.app/sos', '_blank');
    });

    // Close on overlay click
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.remove();
        }
    });
}

function copyPlaybookText(playbook) {
    let text = `🎓 ${playbook.title || 'Teaching Rescue Playbook'}\n\n`;

    if (playbook.summary) {
        text += `📋 Summary:\n${playbook.summary}\n\n`;
    }

    if (playbook.immediate_actions?.length > 0) {
        text += `⚡ Do Right Now:\n`;
        playbook.immediate_actions.forEach((a, i) => {
            text += `${i + 1}. ${a}\n`;
        });
    }

    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!');
    });
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'sahayak-toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => toast.remove(), 3000);
}

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'SHOW_PLAYBOOK') {
        createPlaybookOverlay(message.playbook);
    }
});

// Initialize - only create FAB on education-related sites (optional)
// For demo, we always create it
// createFloatingButton();
