import React from 'react';
import Editor from 'rich-markdown-editor';

const MarkdownEditor = ({ initialMarkdown = '', dark = false, onChange }) => {
  const handleChange = (getValue) => {
    if (onChange) {
      onChange(getValue());
    }
  };

  return (
    <div className="markdown-editor">
      <Editor
        defaultValue={initialMarkdown}
        readOnly={false}
        dark={dark}
        autoFocus={true}
        onChange={handleChange}
      />
    </div>
  );
};

export default MarkdownEditor;
