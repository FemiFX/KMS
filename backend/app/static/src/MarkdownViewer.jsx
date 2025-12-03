import React from 'react';
import Editor from 'rich-markdown-editor';

/**
 * Read-only markdown viewer component using rich-markdown-editor
 * This component displays markdown content with all the rich formatting
 * capabilities of the Outline editor
 */
const MarkdownViewer = ({ markdown, dark = false }) => {
  return (
    <div className="markdown-viewer">
      <Editor
        value={markdown}
        readOnly={true}
        dark={dark}
        autoFocus={false}
        disableExtensions={[
          'container_notice',  // We don't need notices in read-only
        ]}
      />
    </div>
  );
};

export default MarkdownViewer;
