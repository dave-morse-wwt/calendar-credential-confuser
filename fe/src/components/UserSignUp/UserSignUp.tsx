import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';

async function signUpUser(formData: { name: string; email: string; password: string }) {
  const response = await fetch('http://localhost:8000/signup', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(formData),
  });

  if (!response.ok) {
    throw new Error('Failed to sign up');
  }

  return response.json();
}

export const UserSignUp: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
  });

  const mutation = useMutation({
    mutationFn: signUpUser,
    onSuccess: (data) => {
      console.log('User signed up successfully:', data);
      // TODO: You could redirect, show a success message, etc.
    },
    onError: (error) => {
      console.error('Sign up error:', error);
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

  return (
    <form onSubmit={handleSubmit}>
      <h1>Sign Up</h1>
      <label htmlFor="name">Name:</label>
      <input type="text" id="name" name="name" value={formData.name} onChange={handleChange} required />
      <br />
      <label htmlFor="email">Email:</label>
      <input type="email" id="email" name="email" value={formData.email} onChange={handleChange} required />
      <br />
      <label htmlFor="password">Password:</label>
      <input type="password" id="password" name="password" value={formData.password} onChange={handleChange} required />
      <br />
      <button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? 'Signing Up...' : 'Sign Up'}
      </button>
      {mutation.isError && <p style={{ color: 'red' }}>Error: {mutation.error.message}</p>}
      {mutation.isSuccess && <p style={{ color: 'green' }}>Sign-up successful!</p>}
    </form>
  );
};
