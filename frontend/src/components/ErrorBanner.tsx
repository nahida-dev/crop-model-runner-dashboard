import React from 'react'

export default function ErrorBanner({ message }: { message: string }) {
  if (!message) return null;
  return (
    <div style={{
      background:'#d32f2f',
      color:'white',
      padding:'0.5rem 1rem',
      borderRadius:'4px',
      marginBottom:'1rem',
      fontSize:'0.9rem'
    }}>
      {message}
    </div>
  );
}
