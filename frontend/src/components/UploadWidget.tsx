import React, { useCallback, useState } from 'react';
import type { Document } from '../types/document';

interface UploadWidgetProps {
  onUploadComplete: (doc: Document) => void;
}

export const UploadWidget: React.FC<UploadWidgetProps> = ({ onUploadComplete }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  }, []);

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    
    setUploading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/v1/documents/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Upload failed');
      }
      
      const doc = await response.json();
      onUploadComplete(doc);
    } catch (err: any) {
      setError(err.message || 'An error occurred during upload');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div 
      style={{
        border: `2px dashed ${isDragging ? '#06b6d4' : '#475569'}`,
        backgroundColor: isDragging ? 'rgba(6, 182, 212, 0.04)' : '#0F172A',
        borderRadius: '8px',
        padding: '3rem 2rem',
        textAlign: 'center',
        color: '#F8FAFC',
        cursor: 'pointer',
        marginBottom: '2rem',
        transition: 'all 0.2s ease-in-out'
      }}
      onDragEnter={handleDragIn}
      onDragLeave={handleDragOut}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      onClick={() => document.getElementById('file-upload')?.click()}
    >
      <input 
        id="file-upload" 
        type="file" 
        style={{ display: 'none' }} 
        accept=".pdf,.docx,.txt"
        onChange={(e) => handleFiles(e.target.files)}
      />
      
      <div style={{ marginBottom: '1rem', color: '#06b6d4' }}>
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="17 8 12 3 7 8"></polyline>
          <line x1="12" y1="3" x2="12" y2="15"></line>
        </svg>
      </div>
      <h3 style={{ margin: '0 0 0.5rem 0', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>Legal Ingestion Engine</h3>
      <p style={{ color: '#94A3B8', fontSize: '14px', margin: 0 }}>
        Drag and drop contract files here, or Click to Browse<br/>
        (PDF, DOCX, TXT up to 10MB)
      </p>

      {uploading && <div style={{ marginTop: '1rem', color: '#06b6d4' }}>Uploading...</div>}
      {error && <div style={{ marginTop: '1rem', color: '#F43F5E' }}>{error}</div>}
    </div>
  );
};
