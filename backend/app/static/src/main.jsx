import React from 'react';
import ReactDOM from 'react-dom';
import MarkdownViewer from './MarkdownViewer';
import MarkdownEditor from './MarkdownEditor';

/**
 * Initialize the markdown viewer on any page that has a #markdown-viewer element
 * The markdown content and dark mode preference are passed via data attributes
 */
export function initializeMarkdownViewer(selector = '#markdown-viewer') {
  const container = typeof selector === 'string' ? document.querySelector(selector) : selector;

  if (!container) {
    return; // No viewer on this page
  }

  // Get markdown content from data attribute or script tag
  let markdown = container.dataset.markdown || '';

  // Prefer the JSON payload (preserves code fences and special characters)
  const markdownData = container.querySelector('[data-markdown-json]') || document.getElementById('markdown-data');
  if (markdownData?.textContent) {
    try {
      markdown = JSON.parse(markdownData.textContent);
    } catch (err) {
      console.warn('Failed to parse markdown JSON payload, falling back to data attribute', err);
    }
  }
  const dark = container.dataset.dark === 'true' || document.documentElement.classList.contains('dark');

  const renderViewer = (isDark) => {
    ReactDOM.render(
      <React.StrictMode>
        <MarkdownViewer markdown={markdown} dark={isDark} />
      </React.StrictMode>,
      container
    );
  };

  // Initial render
  renderViewer(dark);

  // Listen for dark mode changes
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.attributeName === 'class') {
        const isDark = document.documentElement.classList.contains('dark');
        renderViewer(isDark);
      }
    });
  });

  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['class']
  });
}

/**
 * Initialize the markdown editor on pages with #markdown-editor
 */
function initializeMarkdownEditor() {
  const container = document.getElementById('markdown-editor');
  if (!container) {
    return; // No editor on this page
  }

  const hiddenInputId = container.dataset.inputId || 'markdown-input';
  const hiddenInput = document.getElementById(hiddenInputId);

  let initialMarkdown = hiddenInput?.value || '';
  const markdownData = document.getElementById('markdown-data');
  if (markdownData?.textContent) {
    try {
      initialMarkdown = JSON.parse(markdownData.textContent);
    } catch (err) {
      console.warn('Failed to parse markdown JSON payload, falling back to hidden input', err);
    }
  }

  const renderEditor = (isDark) => {
    ReactDOM.render(
      <React.StrictMode>
        <MarkdownEditor
          initialMarkdown={initialMarkdown}
          dark={isDark}
          onChange={(val) => {
            if (hiddenInput) {
              hiddenInput.value = val;
            }
          }}
        />
      </React.StrictMode>,
      container
    );
  };

  const dark = document.documentElement.classList.contains('dark');
  renderEditor(dark);

  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.attributeName === 'class') {
        const isDark = document.documentElement.classList.contains('dark');
        renderEditor(isDark);
      }
    });
  });

  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['class']
  });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initializeMarkdownViewer();
    initializeMarkdownEditor();
  });
} else {
  initializeMarkdownViewer();
  initializeMarkdownEditor();
}

// Expose globally for ad-hoc mounts (e.g., version preview modal)
window.initializeMarkdownViewer = initializeMarkdownViewer;
