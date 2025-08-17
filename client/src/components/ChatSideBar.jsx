const ChatSidebar = () => {
  return (
    <div className="w-64 bg-chat-background border-r border-border flex flex-col">
      <div className="p-4 border-b border-border">
        <div className="w-24 h-6 bg-muted rounded"></div>
      </div>
      <div className="flex-1 p-4">
        Side bar
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="w-full h-8 bg-muted rounded"></div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ChatSidebar;
