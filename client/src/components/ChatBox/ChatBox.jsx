import ReplyBox from "./ReplyBox";
import { useState } from "react";

const ChatBox = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! Welcome to the chat app.",
      isUser: false,
      timestamp: new Date(),
    },
  ]);

  const handleSendMessage = (messageText) => {
    if (messageText.trim()) {
      const newMessage = {
        id: messages.length + 1,
        text: messageText,
        isUser: true,
        timestamp: new Date(),
      };
      setMessages([...messages, newMessage]);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-chat-background h-full w-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0 w-full">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.isUser ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.isUser
                  ? "bg-message-user text-message-user-foreground"
                  : "bg-message-other text-message-other-foreground"
              }`}
            >
              <p>{message.text}</p>
              <span className="text-xs opacity-70 mt-1 block">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))}
      </div>
      <ReplyBox onSendMessage={handleSendMessage} />
    </div>
  );
};

export default ChatBox;
