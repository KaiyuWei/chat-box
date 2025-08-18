import { useState } from "react";
import ChatBox from "@/components/ChatBox/ChatBox";
import ChatSidebar from "@/components/ChatSideBar";
import ChatTopBar from "@/components/ChatTopBar";

const ChatPage = () => {
  const [selectedConversationId, setSelectedConversationId] = useState(null);

  const handleConversationSelect = (conversation) => {
    console.log("Switching to conversation:", conversation.title);
    setSelectedConversationId(conversation.conversation_id);
  };

  return (
    <div className="h-screen w-full bg-background flex flex-col overflow-hidden">
      <ChatTopBar />
      <div className="flex flex-1 overflow-hidden w-full">
        <ChatSidebar
          selectedConversationId={selectedConversationId}
          onConversationSelect={handleConversationSelect}
        />
        <ChatBox
          selectedConversationId={selectedConversationId}
          onConversationChange={setSelectedConversationId}
        />
      </div>
    </div>
  );
};

export default ChatPage;
