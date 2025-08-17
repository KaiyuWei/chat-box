import ChatBox from "@/components/ChatBox/ChatBox";
import ChatSidebar from "@/components/ChatSideBar";
import ChatTopBar from "@/components/ChatTopBar";

const ChatPage = () => {
  return (
    <div className="h-screen w-screen bg-background flex flex-col overflow-hidden">
      <ChatTopBar />
      <div className="flex flex-1 overflow-hidden">
        <ChatSidebar />
        <ChatBox />
      </div>
    </div>
  );
};

export default ChatPage;
