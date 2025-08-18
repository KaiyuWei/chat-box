import { useState, useEffect } from "react";
import ChatBox from "@/components/ChatBox/ChatBox";
import ChatSidebar from "@/components/ChatSideBar";
import ChatTopBar from "@/components/ChatTopBar";

const STORAGE_KEY = "selectedConversationId";

const ChatPage = () => {
  const [selectedConversationId, setSelectedConversationId] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      console.warn("Failed to load conversation ID from localStorage:", error);
      return null;
    }
  });
  const [refreshSidebar, setRefreshSidebar] = useState(0);
  const [tempConversation, setTempConversation] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleConversationSelect = (conversation) => {
    setSelectedConversationId(conversation.conversation_id);
  };

  const handleNewConversation = () => {
    const tempConversationId = `temp_${Date.now()}`;
    const newTempConversation = {
      conversation_id: tempConversationId,
      title: "New Conversation",
      created_at: new Date().toISOString(),
      messages: [],
    };

    setTempConversation(newTempConversation);
    setSelectedConversationId(tempConversationId);
  };

  const handleConversationCreated = (newConversationId) => {
    setTempConversation(null);
    setRefreshSidebar((prev) => prev + 1);
    setSelectedConversationId(newConversationId);
  };

  useEffect(() => {
    try {
      if (selectedConversationId !== null) {
        localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify(selectedConversationId)
        );
      } else {
        localStorage.removeItem(STORAGE_KEY);
      }
    } catch (error) {
      console.warn("Failed to save conversation ID to localStorage:", error);
    }
  }, [selectedConversationId]);

  return (
    <div className="h-screen w-full bg-background flex flex-col overflow-hidden">
      <ChatTopBar />
      <div className="flex flex-1 overflow-hidden w-full">
        <ChatSidebar
          selectedConversationId={selectedConversationId}
          onConversationSelect={handleConversationSelect}
          onNewConversation={handleNewConversation}
          refreshTrigger={refreshSidebar}
          tempConversation={tempConversation}
          isProcessing={isProcessing}
        />
        <ChatBox
          selectedConversationId={selectedConversationId}
          onConversationChange={setSelectedConversationId}
          onConversationCreated={handleConversationCreated}
          isProcessing={isProcessing}
          setIsProcessing={setIsProcessing}
        />
      </div>
    </div>
  );
};

export default ChatPage;
