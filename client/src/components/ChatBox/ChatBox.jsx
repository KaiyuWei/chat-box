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

  const handleSendMessage = async (messageText) => {
    if (messageText.trim()) {
      const newMessage = {
        id: messages.length + 1,
        text: messageText,
        isUser: true,
        timestamp: new Date(),
      };
      setMessages([...messages, newMessage]);

      try {
        const chatRequest = {
          messages: [
            {
              role: "user",
              content: messageText,
            },
          ],
        };

        const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
        const response = await fetch(`${apiBaseUrl}/api/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(chatRequest),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const chatResponse = await response.json();
        console.log("Backend response:", chatResponse);

        const assistantMessage = {
          id: messages.length + 2,
          text: chatResponse.messages,
          isUser: false,
          timestamp: new Date(),
        };
        setMessages((prevMessages) => [...prevMessages, assistantMessage]);
      } catch (error) {
        console.error("Error sending message to backend:", error);
      }
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
