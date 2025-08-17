const ChatTopBar = () => {
  return (
    <div className="h-14 bg-chat-secondary border-b border-border flex items-center justify-between px-4">
      <div className="flex items-center space-x-3">
        Top Bar
        <div className="w-8 h-8 bg-muted rounded-lg"></div>
        <div className="w-32 h-4 bg-muted rounded"></div>
      </div>
    </div>
  );
};

export default ChatTopBar;
