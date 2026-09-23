import React, { useEffect, useState } from 'react';
import { UploadWidget } from './UploadWidget';
import type { Document, DocumentStatus } from '../types/document';
import { apiClient } from '../api/client';

export const Dashboard: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDocuments = async () => {
    try {
      const docs = await apiClient.fetch<Document[]>('/documents/');
      setDocuments(docs);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
    // Poll for status updates
    const interval = setInterval(fetchDocuments, 3000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: DocumentStatus) => {
    switch (status) {
      case 'ready': return '#10B981'; // Emerald
      case 'processing': return '#F59E0B'; // Amber
      case 'failed': return '#F43F5E'; // Rose
      default: return '#6366F1'; // Indigo
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await apiClient.fetch(`/documents/${id}`, { method: 'DELETE' });
      fetchDocuments();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', fontFamily: 'Inter, sans-serif' }}>
      <UploadWidget onUploadComplete={fetchDocuments} />
      
      <div style={{ backgroundColor: '#0F172A', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.08)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', color: '#F8FAFC' }}>
          <thead style={{ backgroundColor: '#1E293B', textAlign: 'left' }}>
            <tr>
              <th style={{ padding: '1rem', fontWeight: 600 }}>Filename</th>
              <th style={{ padding: '1rem', fontWeight: 600 }}>Uploaded At</th>
              <th style={{ padding: '1rem', fontWeight: 600 }}>Classification</th>
              <th style={{ padding: '1rem', fontWeight: 600 }}>Status</th>
              <th style={{ padding: '1rem', fontWeight: 600, textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && documents.length === 0 ? (
              <tr><td colSpan={5} style={{ padding: '2rem', textAlign: 'center' }}>Loading...</td></tr>
            ) : documents.length === 0 ? (
              <tr><td colSpan={5} style={{ padding: '2rem', textAlign: 'center', color: '#94A3B8' }}>No documents uploaded yet.</td></tr>
            ) : documents.map((doc) => (
              <tr key={doc.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
                <td style={{ padding: '1rem' }}>{doc.filename}</td>
                <td style={{ padding: '1rem', color: '#94A3B8', fontSize: '14px' }}>
                  {new Date(doc.uploadedAt).toLocaleString()}
                </td>
                <td style={{ padding: '1rem' }}>
                  {doc.classification ? (
                    <span style={{ backgroundColor: 'rgba(6, 182, 212, 0.1)', color: '#06B6D4', padding: '4px 8px', borderRadius: '9999px', fontSize: '12px', fontWeight: 600 }}>
                      {doc.classification}
                    </span>
                  ) : '-'}
                </td>
                <td style={{ padding: '1rem' }}>
                  <span style={{ 
                    backgroundColor: `${getStatusColor(doc.status)}20`, 
                    color: getStatusColor(doc.status), 
                    padding: '4px 8px', 
                    borderRadius: '9999px', 
                    fontSize: '12px', 
                    fontWeight: 600,
                    textTransform: 'uppercase'
                  }}>
                    {doc.status}
                  </span>
                </td>
                <td style={{ padding: '1rem', textAlign: 'right' }}>
                  <button 
                    onClick={() => handleDelete(doc.id)}
                    style={{ background: 'transparent', border: '1px solid rgba(244, 63, 94, 0.3)', color: '#F43F5E', padding: '4px 8px', borderRadius: '4px', cursor: 'pointer' }}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
