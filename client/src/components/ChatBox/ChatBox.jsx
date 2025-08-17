import ReplyBox from "./ReplyBox";

const ChatBox = () => {
  return (
    <div className="flex-1 flex flex-col bg-chat-background h-full">
      {/* Chat messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
        <div>Conversation here</div>
        <div>Conversation 2</div>
        <div>More conversation...</div>
        <div>More conversation...</div>
        <div>More conversation...</div>
        <div>More conversation...</div>
      </div>
      
      {/* Reply box at the bottom */}
      <ReplyBox />
    </div>
  );
};

export default ChatBox;
