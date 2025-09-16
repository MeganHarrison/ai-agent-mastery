"use client";

import { useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { redirect } from 'next/navigation';
import Login from '@/components/pages/Login';

export default function LoginPage() {
  const { user, loading } = useAuth();
  
  // Redirect to chat if already authenticated
  useEffect(() => {
    if (!loading && user) {
      redirect('/');
    }
  }, [user, loading]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="animate-pulse">Loading...</div>
      </div>
    );
  }

  if (user) {
    return null; // Will redirect
  }

  return <Login />;
}