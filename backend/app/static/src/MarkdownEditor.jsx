import React, { useState } from 'react';
import Editor from 'rich-markdown-editor';
import { embedDescriptors } from './embeds';

const MarkdownEditor = ({ initialMarkdown = '', dark = false, onChange }) => {
  const [isUploading, setIsUploading] = useState(false);

  const handleChange = (getValue) => {
    if (onChange) {
      onChange(getValue());
    }
  };

  /**
   * Handle image uploads
   */
  const handleImageUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/uploads/image', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Upload failed');
      }

      const data = await response.json();
      return data.url;
    } catch (error) {
      console.error('Image upload failed:', error);
      alert('Fehler beim Hochladen des Bildes: ' + error.message);
      throw error;
    }
  };

  /**
   * Handle link clicks
   */
  const handleClickLink = (href, event) => {
    // Open external links in new tab
    if (href.startsWith('http://') || href.startsWith('https://')) {
      event.preventDefault();
      window.open(href, '_blank', 'noopener,noreferrer');
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
        uploadImage={handleImageUpload}
        onImageUploadStart={() => setIsUploading(true)}
        onImageUploadStop={() => setIsUploading(false)}
        embeds={embedDescriptors}
        onClickLink={handleClickLink}
        onShowToast={(message, type) => {
          // Simple toast notification (you can enhance this)
          console.log(`[${type}] ${message}`);
          if (type === 'error') {
            alert(message);
          }
        }}
      />
      {isUploading && (
        <div style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          background: 'rgba(0, 0, 0, 0.7)',
          color: 'white',
          padding: '8px 12px',
          borderRadius: '4px',
          fontSize: '14px',
        }}>
          Bild wird hochgeladen...
        </div>
      )}
    </div>
  );
};

export default MarkdownEditor;
