import { useState } from "react";
import ChatBox from "@/components/ChatBox/ChatBox";
import ChatSidebar from "@/components/ChatSideBar";
import ChatTopBar from "@/components/ChatTopBar";

const ChatPage = () => {
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  const [refreshSidebar, setRefreshSidebar] = useState(0);
  const [tempConversation, setTempConversation] = useState(null);

  const handleConversationSelect = (conversation) => {
    console.log("Switching to conversation:", conversation.title);
    setSelectedConversationId(conversation.conversation_id);
  };

  const handleNewConversation = () => {
    console.log("Creating new conversation");
    // Create a temporary conversation ID and object for the new conversation
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
    console.log("New conversation created with ID:", newConversationId);
    // Clear the temporary conversation
    setTempConversation(null);
    // Refresh the sidebar to show the new conversation
    setRefreshSidebar((prev) => prev + 1);
    // Select the new conversation
    setSelectedConversationId(newConversationId);
  };

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
        />
        <ChatBox
          selectedConversationId={selectedConversationId}
          onConversationChange={setSelectedConversationId}
          onConversationCreated={handleConversationCreated}
        />
      </div>
    </div>
  );
};

export default ChatPage;
