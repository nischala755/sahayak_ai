/**
 * SAHAYAK AI Chrome Extension - Background Service Worker
 * Handles background tasks and context menu
 */

// Create context menu on install
chrome.runtime.onInstalled.addListener(() => {
    // Create context menu for selected text
    chrome.contextMenus.create({
        id: 'sahayak-sos',
        title: 'Get SAHAYAK AI Help for: "%s"',
        contexts: ['selection']
    });

    console.log('SAHAYAK AI Extension installed');
});

// Handle context menu click
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    if (info.menuItemId === 'sahayak-sos' && info.selectionText) {
        // Get API URL from storage
        const { apiUrl = 'https://sahayak-ai-p720.onrender.com' } =
            await chrome.storage.local.get('apiUrl');

        try {
            // Call quick SOS API
            const response = await fetch(
                `${apiUrl}/api/v1/sos/quick?raw_input=${encodeURIComponent(info.selectionText)}`,
                { method: 'POST' }
            );

            if (response.ok) {
                const data = await response.json();

                // Send playbook to content script
                chrome.tabs.sendMessage(tab.id, {
                    type: 'SHOW_PLAYBOOK',
                    playbook: data.playbook
                });
            }
        } catch (error) {
            console.error('SOS Error:', error);
        }
    }
});

// Handle messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'GET_CURRENT_TAB_INFO') {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0]) {
                sendResponse({
                    url: tabs[0].url,
                    title: tabs[0].title
                });
            }
        });
        return true; // Async response
    }
});

// Handle keyboard shortcuts
chrome.commands.onCommand.addListener((command) => {
    if (command === 'open-popup') {
        chrome.action.openPopup();
    }
});
