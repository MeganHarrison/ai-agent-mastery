
'use client';

import { useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { Loader } from 'lucide-react';

// This component serves as a redirect from the index route to the appropriate destination
const Index = () => {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Wait for auth to be checked
    if (!loading) {
      if (user) {
        // If logged in, go to chat
        router.push('/');
      } else {
        // If not logged in, go to login page
        router.push('/login');
      }
    }
  }, [user, loading, router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="text-center">
        <Loader className="h-8 w-8 animate-spin mx-auto mb-4" />
        <p className="text-muted-foreground">Loading application...</p>
      </div>
    </div>
  );
};

export default Index;
