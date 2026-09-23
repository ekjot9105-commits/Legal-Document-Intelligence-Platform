import React from 'react';

export const LegalDisclaimer: React.FC = () => {
  return (
    <div
      role="status"
      aria-live="polite"
      style={{
        backgroundColor: '#fef3c7',
        color: '#92400e',
        padding: '0.75rem',
        textAlign: 'center',
        borderBottom: '1px solid #fcd34d',
        fontWeight: 'bold',
        fontSize: '0.875rem'
      }}
    >
      ⚠️ This tool provides legal information, not legal advice. Consult a qualified attorney for legal advice.
    </div>
  );
};
