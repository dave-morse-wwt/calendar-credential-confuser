import { useQuery } from '@tanstack/react-query';
import React from 'react';

interface CredentialLoaderProps {
    children: React.ReactNode;
}

export const CredentialLoader: React.FC<CredentialLoaderProps> = ({ children }) => {
  // const { isPending, error, data } = useQuery({
  //   queryKey: ['repoData'],
  //   queryFn: () =>
  //     fetch('http://localhost:8000').then((res) =>
  //       res.json(),
  //     ),
  // })
  // if (isPending) return 'Loading...'
  // if (error) return 'An error has occurred: ' + error.message
  return (
    <div>
      <br />
      <a href="http://localhost:8000/start-auth">Connect Google Calendar</a>
      <br />
      {children}
    </div>
  )
};