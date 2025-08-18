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

  const handleCloseTempConversation = async () => {
    setTempConversation(null);

    // Activate the first regular conversation if available
    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
      const userId = 1; // TODO: replace with actual user ID when auth system is added
      const response = await fetch(
        `${apiBaseUrl}/api/user-conv-with-msg/${userId}`
      );
      if (response.ok) {
        const conversations = await response.json();
        if (conversations.length > 0) {
          const firstConversation = conversations[conversations.length - 1]; // Latest conversation
          setSelectedConversationId(firstConversation.conversation_id);
          // Trigger sidebar refresh to ensure it has the latest conversations
          setRefreshSidebar((prev) => prev + 1);
        } else {
          setSelectedConversationId(null);
        }
      }
    } catch (error) {
      console.error("Error fetching conversations after closing temp:", error);
      setSelectedConversationId(null);
    }
  };

  const handleNoConversationsFound = () => {
    // Clear localStorage when user has no conversations
    // This handles cases where the user was deleted/reset but localStorage still has old data
    console.log("No conversations found for user, clearing localStorage");
    try {
      localStorage.removeItem(STORAGE_KEY);

      const tempConversationId = `temp_welcome_${Date.now()}`;
      const welcomeConversation = {
        conversation_id: tempConversationId,
        title: "New Conversation",
        created_at: new Date().toISOString(),
        messages: [],
      };

      setTempConversation(welcomeConversation);
      setSelectedConversationId(tempConversationId);
    } catch (error) {
      console.warn("Failed to clear conversation ID from localStorage:", error);
    }
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
          onCloseTempConversation={handleCloseTempConversation}
          refreshTrigger={refreshSidebar}
          tempConversation={tempConversation}
          isProcessing={isProcessing}
        />
        <ChatBox
          selectedConversationId={selectedConversationId}
          onConversationChange={setSelectedConversationId}
          onConversationCreated={handleConversationCreated}
          onNoConversationsFound={handleNoConversationsFound}
          isProcessing={isProcessing}
          setIsProcessing={setIsProcessing}
        />
      </div>
    </div>
  );
};

export default ChatPage;
