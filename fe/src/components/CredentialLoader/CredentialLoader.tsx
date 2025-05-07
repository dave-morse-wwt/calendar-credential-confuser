import React from 'react';

interface CredentialLoaderProps {
    children: React.ReactNode;
}

export const CredentialLoader: React.FC<CredentialLoaderProps> = ({ children }) => {
  return (
    <div>
      <br />
      <a href="/api/v1/start-auth">Connect Google Calendar</a>
      <br />
      {children}
    </div>
  )
};