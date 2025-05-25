// Initialize storage when extension is installed
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({ 
    'autoCrawlEnabled': true
  });
});

// List of confidential domains to block
const BLOCKED_DOMAINS = [
  'gmail.com',
  'mail.google.com',
  'web.whatsapp.com',
  'web.telegram.org',
  'telegram.org',
  'facebook.com',
  'messenger.com',
  'linkedin.com',
  'outlook.com',
  'office.com',
  'microsoft.com',
  'bankofamerica.com',
  'chase.com',
  'wellsfargo.com',
  'paypal.com'
];

// Function to check if URL should be blocked
function isBlockedUrl(url) {
  try {
    const domain = new URL(url).hostname;
    return BLOCKED_DOMAINS.some(blockedDomain => 
      domain === blockedDomain || domain.endsWith('.' + blockedDomain)
    );
  } catch {
    return true; // Block invalid URLs
  }
}

// Listen for navigation events
chrome.webNavigation.onCompleted.addListener((details) => {
  // Only crawl main frame navigation
  if (details.frameId === 0) {
    chrome.storage.local.get(['autoCrawlEnabled'], (result) => {
      if (result.autoCrawlEnabled && !isBlockedUrl(details.url)) {
        // Wait for page to fully load
        setTimeout(() => {
          chrome.tabs.sendMessage(details.tabId, { action: 'crawl' });
        }, 2000);
      }
    });
  }
}, { url: [{ schemes: ['http', 'https'] }] });

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'processContent') {
    // Check if URL is blocked before sending to backend
    if (!isBlockedUrl(request.data.url)) {
      // Send URL to backend server
      fetch('http://localhost:5000/index', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request.data)
      })
      .then(response => response.json())
      .then(data => {
        console.log('Backend indexing response:', data);
      })
      .catch(error => {
        console.error('Error sending to backend:', error);
      });
    } else {
      console.log('Blocked crawling of confidential site:', request.data.url);
    }
  }
}); 