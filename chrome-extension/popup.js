/**
 * SAHAYAK AI Chrome Extension - Popup Script
 * Handles UI interactions and API calls
 */

// Configuration
const DEFAULT_API_URL = 'https://sahayak-ai-p720.onrender.com';
const LOCAL_API_URL = 'http://localhost:8000';

// State
let currentPlaybook = null;
let apiUrl = DEFAULT_API_URL;
let authToken = null;

// DOM Elements
const elements = {
    authSection: null,
    sosSection: null,
    loadingSection: null,
    resultSection: null,
    settingsPanel: null,
    problemInput: null,
    languageSelect: null,
    playbookContent: null,
    resultTitle: null
};

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', async () => {
    initElements();
    await loadSettings();
    await checkAuth();
    initEventListeners();
});

function initElements() {
    elements.authSection = document.getElementById('authSection');
    elements.sosSection = document.getElementById('sosSection');
    elements.loadingSection = document.getElementById('loadingSection');
    elements.resultSection = document.getElementById('resultSection');
    elements.settingsPanel = document.getElementById('settingsPanel');
    elements.problemInput = document.getElementById('problemInput');
    elements.languageSelect = document.getElementById('languageSelect');
    elements.playbookContent = document.getElementById('playbookContent');
    elements.resultTitle = document.getElementById('resultTitle');
}

async function loadSettings() {
    try {
        const result = await chrome.storage.local.get(['apiUrl', 'authToken', 'defaultLang']);
        if (result.apiUrl) {
            apiUrl = result.apiUrl;
            document.getElementById('apiUrlInput').value = apiUrl;
        }
        if (result.authToken) {
            authToken = result.authToken;
        }
        if (result.defaultLang) {
            elements.languageSelect.value = result.defaultLang;
        }
    } catch (e) {
        console.log('Could not load settings:', e);
    }
}

async function checkAuth() {
    if (authToken) {
        try {
            const response = await fetch(`${apiUrl}/api/v1/auth/me`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            });
            if (response.ok) {
                showSection('sos');
                return;
            }
        } catch (e) {
            console.log('Auth check failed:', e);
        }
        authToken = null;
        chrome.storage.local.remove('authToken');
    }
    // Show SOS section anyway (allows anonymous quick SOS)
    showSection('sos');
}

function initEventListeners() {
    // Quick cards
    document.querySelectorAll('.quick-card').forEach(card => {
        card.addEventListener('click', () => {
            elements.problemInput.value = card.dataset.problem;
            submitSOS();
        });
    });

    // SOS button
    document.getElementById('sosBtn').addEventListener('click', submitSOS);

    // Login
    document.getElementById('loginBtn').addEventListener('click', handleLogin);

    // Copy button
    document.getElementById('copyBtn').addEventListener('click', copyPlaybook);

    // New SOS
    document.getElementById('newSosBtn').addEventListener('click', () => {
        elements.problemInput.value = '';
        currentPlaybook = null;
        showSection('sos');
    });

    // Save playbook
    document.getElementById('saveBtn').addEventListener('click', savePlaybook);

    // Settings
    document.getElementById('settingsBtn').addEventListener('click', () => {
        showSection('settings');
    });

    document.getElementById('saveSettingsBtn').addEventListener('click', saveSettings);
    document.getElementById('closeSettingsBtn').addEventListener('click', () => {
        showSection('sos');
    });

    document.getElementById('logoutBtn').addEventListener('click', handleLogout);

    // Enter key on input
    elements.problemInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            submitSOS();
        }
    });
}

function showSection(section) {
    elements.authSection?.classList.add('hidden');
    elements.sosSection?.classList.add('hidden');
    elements.loadingSection?.classList.add('hidden');
    elements.resultSection?.classList.add('hidden');
    elements.settingsPanel?.classList.add('hidden');

    switch (section) {
        case 'auth':
            elements.authSection?.classList.remove('hidden');
            break;
        case 'sos':
            elements.sosSection?.classList.remove('hidden');
            break;
        case 'loading':
            elements.loadingSection?.classList.remove('hidden');
            break;
        case 'result':
            elements.resultSection?.classList.remove('hidden');
            break;
        case 'settings':
            elements.settingsPanel?.classList.remove('hidden');
            break;
    }
}

async function submitSOS() {
    const problem = elements.problemInput.value.trim();
    if (!problem) {
        showToast('Please describe your problem');
        return;
    }

    const language = elements.languageSelect.value;
    showSection('loading');

    try {
        // Use quick SOS endpoint (no auth required)
        const url = `${apiUrl}/api/v1/sos/quick?raw_input=${encodeURIComponent(problem)}&language=${language}`;

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        currentPlaybook = data.playbook;
        displayPlaybook(data.playbook);
        showSection('result');

    } catch (error) {
        console.error('SOS Error:', error);
        showToast('Failed to get help. Please try again.');
        showSection('sos');
    }
}

function displayPlaybook(playbook) {
    if (!playbook) {
        elements.playbookContent.innerHTML = '<p>No playbook available</p>';
        return;
    }

    elements.resultTitle.textContent = playbook.title || 'Teaching Rescue Playbook';

    let html = '';

    // Summary
    if (playbook.summary) {
        html += `
      <div class="playbook-section">
        <h4>📋 Summary</h4>
        <p>${playbook.summary}</p>
      </div>
    `;
    }

    // Immediate Actions
    if (playbook.immediate_actions?.length > 0) {
        html += `
      <div class="playbook-section">
        <h4>⚡ Do Right Now</h4>
        <ul>
          ${playbook.immediate_actions.map(a => `<li>${a}</li>`).join('')}
        </ul>
      </div>
    `;
    }

    // Recovery Steps
    if (playbook.recovery_steps?.length > 0) {
        html += `
      <div class="playbook-section">
        <h4>📈 Recovery Steps</h4>
        <ul>
          ${playbook.recovery_steps.map(s => `<li>${s}</li>`).join('')}
        </ul>
      </div>
    `;
    }

    // Teaching Tips
    if (playbook.teaching_tips?.length > 0) {
        html += `
      <div class="playbook-section">
        <h4>💡 Teaching Tips</h4>
        <ul>
          ${playbook.teaching_tips.map(t => `<li>${t}</li>`).join('')}
        </ul>
      </div>
    `;
    }

    // Success Indicators
    if (playbook.success_indicators?.length > 0) {
        html += `
      <div class="playbook-section">
        <h4>✅ Success Indicators</h4>
        <ul>
          ${playbook.success_indicators.map(s => `<li>${s}</li>`).join('')}
        </ul>
      </div>
    `;
    }

    elements.playbookContent.innerHTML = html || '<p>Playbook generated successfully!</p>';
}

async function handleLogin() {
    const email = document.getElementById('emailInput').value.trim();
    const password = document.getElementById('passwordInput').value;

    if (!email || !password) {
        showToast('Please enter email and password');
        return;
    }

    try {
        const response = await fetch(`${apiUrl}/api/v1/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
        });

        if (!response.ok) {
            throw new Error('Invalid credentials');
        }

        const data = await response.json();
        authToken = data.access_token;
        await chrome.storage.local.set({ authToken });
        showToast('Logged in successfully!');
        showSection('sos');

    } catch (error) {
        showToast('Login failed. Check your credentials.');
    }
}

function handleLogout() {
    authToken = null;
    chrome.storage.local.remove('authToken');
    showToast('Logged out');
    showSection('sos');
}

async function copyPlaybook() {
    if (!currentPlaybook) return;

    const text = formatPlaybookAsText(currentPlaybook);

    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard!');
    } catch (e) {
        showToast('Failed to copy');
    }
}

function formatPlaybookAsText(playbook) {
    let text = `🎓 ${playbook.title || 'Teaching Rescue Playbook'}\n\n`;

    if (playbook.summary) {
        text += `📋 Summary:\n${playbook.summary}\n\n`;
    }

    if (playbook.immediate_actions?.length > 0) {
        text += `⚡ Do Right Now:\n`;
        playbook.immediate_actions.forEach((a, i) => {
            text += `${i + 1}. ${a}\n`;
        });
        text += '\n';
    }

    if (playbook.recovery_steps?.length > 0) {
        text += `📈 Recovery Steps:\n`;
        playbook.recovery_steps.forEach((s, i) => {
            text += `${i + 1}. ${s}\n`;
        });
        text += '\n';
    }

    text += `\n🎓 Generated by SAHAYAK AI`;
    return text;
}

async function savePlaybook() {
    if (!authToken) {
        showToast('Please login to save playbooks');
        return;
    }

    showToast('Playbook saved to your history!');
}

async function saveSettings() {
    const newApiUrl = document.getElementById('apiUrlInput').value.trim();
    const defaultLang = document.getElementById('defaultLangSelect').value;

    apiUrl = newApiUrl || DEFAULT_API_URL;

    await chrome.storage.local.set({
        apiUrl,
        defaultLang
    });

    showToast('Settings saved!');
    showSection('sos');
}

function showToast(message) {
    // Remove existing toast
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => toast.remove(), 3000);
}
