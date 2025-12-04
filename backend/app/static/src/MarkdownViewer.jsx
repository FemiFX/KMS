import React from 'react';
import Editor from 'rich-markdown-editor';
import { embedDescriptors } from './embeds';

/**
 * Read-only markdown viewer component using rich-markdown-editor
 * This component displays markdown content with all the rich formatting
 * capabilities of the Outline editor, including embedded content
 */
const MarkdownViewer = ({ markdown, dark = false }) => {
  /**
   * Handle link clicks in read-only mode
   */
  const handleClickLink = (href, event) => {
    // Open external links in new tab
    if (href.startsWith('http://') || href.startsWith('https://')) {
      event.preventDefault();
      window.open(href, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div className="markdown-viewer">
      <Editor
        value={markdown}
        readOnly={true}
        dark={dark}
        autoFocus={false}
        embeds={embedDescriptors}
        onClickLink={handleClickLink}
        disableExtensions={[
          'container_notice',  // We don't need notices in read-only
        ]}
      />
    </div>
  );
};

export default MarkdownViewer;
