import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';

async function signInUser(formData: { email: string; password: string }) {
  const formBody = new URLSearchParams();
  formBody.append('username', formData.email); // must use "username" because that's what OAuth2PasswordRequestForm expects
  formBody.append('password', formData.password);

  const response = await fetch('http://localhost:8000/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formBody.toString(),
  });

  if (!response.ok) {
    throw new Error('Failed to sign in');
  }

  return response.json();
}

export const SignIn: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const mutation = useMutation({
    mutationFn: signInUser,
    onSuccess: (data) => {
      console.log('User signed in successfully:', data);
      // TODO: You could redirect, show a success message, etc.
    },
    onError: (error) => {
      console.error('Sign in error:', error);
      // TODO: Show error message to user
    },
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  ///// CURRENT PLAN:
  ///// Hot-Circuit the email/username form problem by just hooking up to our existing real db

  return (
    <form onSubmit={handleSubmit}>
      <h1>Sign In</h1>
      <label htmlFor="email">Email:</label>
      <input type="email" id="email" name="email" value={formData.email} onChange={handleChange} required />
      <br />
      <label htmlFor="password">Password:</label>
      <input type="password" id="password" name="password" value={formData.password} onChange={handleChange} required />
      <br />
      <button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? 'Signing In...' : 'Sign In'}
      </button>
      {mutation.isError && <p style={{ color: 'red' }}>Error: {mutation.error.message}</p>}
      {mutation.isSuccess && <p style={{ color: 'green' }}>Sign-in successful!</p>}
    </form>
  );
};
