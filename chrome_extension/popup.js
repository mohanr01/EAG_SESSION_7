document.addEventListener('DOMContentLoaded', function() {
  const crawlButton = document.getElementById('crawlButton');
  const searchButton = document.getElementById('searchButton');
  const searchInput = document.getElementById('searchInput');
  const statusDiv = document.getElementById('status');
  const autoCrawlToggle = document.getElementById('autoCrawlToggle');

  // Load initial state of auto-crawl toggle
  chrome.storage.local.get(['autoCrawlEnabled'], (result) => {
    autoCrawlToggle.checked = result.autoCrawlEnabled !== false;
  });

  // Handle auto-crawl toggle
  autoCrawlToggle.addEventListener('change', (e) => {
    chrome.storage.local.set({ 'autoCrawlEnabled': e.target.checked });
    statusDiv.textContent = e.target.checked ? 'Auto-crawl enabled' : 'Auto-crawl disabled';
  });

  crawlButton.addEventListener('click', async () => {
    statusDiv.textContent = 'Crawling current page...';
    
    // Get the active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // Send message to content script
    chrome.tabs.sendMessage(tab.id, { action: 'crawl' }, response => {
      if (response && response.success) {
        statusDiv.textContent = 'Content indexed successfully!';
      } else {
        statusDiv.textContent = 'Error: ' + (response ? response.error : 'Unknown error');
      }
    });
  });

  searchButton.addEventListener('click', async () => {
    const query = searchInput.value.trim();
    if (!query) {
      statusDiv.textContent = 'Please enter a search query';
      return;
    }

    statusDiv.textContent = 'Searching...';
    
    try {
      const response = await fetch('http://localhost:5000/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query })
      });

      const data = await response.json();
      
      if (data.success) {
        // Display the search results
        const results = data.results;
        if (Array.isArray(results) && results.length > 0) {
          console.log(results[0]+"-"+results[1])
          statusDiv.innerHTML = 
            `
              <div style="margin: 5px 0; padding: 5px; border-bottom: 1px solid #eee;">
                <div style="margin-bottom: 5px;">${results[0]}</div>
                <a href="${results[1]}" target="_blank" style="color: blue; text-decoration: underline;">
                  Open Source
                </a>
              </div>
            `
          
          // Add click handler to highlight content in the page
          const links = statusDiv.getElementsByTagName('a');
          Array.from(links).forEach(link => {
            link.addEventListener('click', (e) => {
              e.preventDefault();
              const url = link.href;
              chrome.tabs.create({ url: url }, (tab) => {
                // Wait for the page to load then send message to highlight content
                chrome.tabs.onUpdated.addListener(function listener(tabId, info) {
                  if (tabId === tab.id && info.status === 'complete') {
                    chrome.tabs.sendMessage(tab.id, { 
                      action: 'highlight',
                      content: content
                    });
                    chrome.tabs.onUpdated.removeListener(listener);
                  }
                });
              });
            });
          });
        } else {
          statusDiv.textContent = 'No results found';
        }
      } else {
        statusDiv.textContent = 'Error: ' + (data.error || 'Search failed');
      }
    } catch (error) {
      statusDiv.textContent = 'Error: Could not connect to search server';
      console.error('Search error:', error);
    }
  });

  // Allow search on Enter key press
  searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      searchButton.click();
    }
  });
}); 