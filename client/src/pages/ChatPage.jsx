import ChatBox from "@/components/ChatBox";
import ChatSidebar from "@/components/ChatSideBar";
import ChatTopBar from "@/components/ChatTopBar";

const ChatPage = () => {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <ChatTopBar />
      <div className="flex flex-1">
        <ChatSidebar />
        <ChatBox />
      </div>
    </div>
  );
};

export default ChatPage;
