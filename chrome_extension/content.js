// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'crawl') {
    try {
      // Only send URL data
      const pageData = {
        url: window.location.href,
        timestamp: new Date().toISOString()
      };

      // Send data to background script
      chrome.runtime.sendMessage({
        action: 'processContent',
        data: pageData
      }, response => {
        sendResponse({ success: true });
      });

      return true; // Required for async sendResponse
    } catch (error) {
      sendResponse({ success: false, error: error.message });
    }
  }
}); 