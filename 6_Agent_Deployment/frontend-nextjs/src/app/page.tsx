"use client";

import { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/hooks/use-toast';
import { Message } from '@/types/database.types';
import { ChatLayout } from '@/components/chat/ChatLayout';
import { useConversationManagement } from '@/components/chat/ConversationManagement';
import { useMessageHandling } from '@/components/chat/MessageHandling';
import { useIsMobile } from '@/hooks/use-mobile';
import { redirect } from 'next/navigation';

export default function Chat() {
  const { user, session, loading } = useAuth();
  const { toast } = useToast();
  const isMobile = useIsMobile();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(isMobile);
  const [messages, setMessages] = useState<Message[]>([]);
  const [messageLoading, setMessageLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newConversationId, setNewConversationId] = useState<string | null>(null);
  
  // Update sidebar collapsed state when mobile status changes
  useEffect(() => {
    setIsSidebarCollapsed(isMobile);
  }, [isMobile]);
  
  // Ref to track if component is mounted
  const isMounted = useRef(true);
  
  useEffect(() => {
    return () => {
      // When component unmounts
      isMounted.current = false;
    };
  }, []);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!loading && !user) {
      redirect('/login');
    }
  }, [user, loading]);
  
  // Use our extracted conversation management hook
  const {
    conversations,
    selectedConversation,
    setSelectedConversation,
    setConversations,
    loadConversations,
    handleNewChat,
    handleSelectConversation
  } = useConversationManagement({ user, isMounted });
  
  // Use our extracted message handling hook
  const { 
    handleSendMessage,
    loadMessages
  } = useMessageHandling({ 
    user, 
    session,
    selectedConversation,
    setMessages, 
    setLoading: setMessageLoading,
    setError, 
    isMounted,
    setSelectedConversation,
    setConversations,
    loadConversations,
    setNewConversationId
  });

  // Show loading state
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="animate-pulse">Loading...</div>
      </div>
    );
  }

  // Don't render if not authenticated (will redirect)
  if (!user) {
    return null;
  }

  return (
    <ChatLayout
      conversations={conversations}
      selectedConversation={selectedConversation}
      onSelectConversation={handleSelectConversation}
      onNewChat={handleNewChat}
      messages={messages}
      onSendMessage={handleSendMessage}
      loading={messageLoading}
      error={error}
      isSidebarCollapsed={isSidebarCollapsed}
      onToggleSidebar={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      newConversationId={newConversationId}
    />
  );
}
