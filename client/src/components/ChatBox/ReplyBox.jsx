const ReplyBox = () => {
  return (
    <div className="p-4 border-t border-border bg-chat-secondary">
        <div className="flex space-x-2">
          Reply box
          {/* <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a message..."
            className="flex-1 bg-background border-border"
          />
          <Button
            onClick={handleSendMessage}
            size="icon"
            className="bg-primary hover:bg-primary/90"
          >
            <Send className="h-4 w-4" />
          </Button> */}
        </div>
      </div>
  );
};

export default ReplyBox;
