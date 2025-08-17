import ReplyBox from "./ReplyBox";
import { useState, useEffect } from "react";
import { conversationStorage } from "../../utils/conversationStorage";

const ChatBox = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! Welcome to the chat app.",
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [conversationId, setConversationId] = useState(null);

  useEffect(() => {
    const currentConversation = conversationStorage.getCurrentConversation();

    if (currentConversation) {
      setConversationId(currentConversation.id);

      if (
        currentConversation.messages &&
        currentConversation.messages.length > 0
      ) {
        
        const messagesWithDates = currentConversation.messages.map(message => ({
          ...message,
          timestamp: new Date(message.timestamp)
        }));
        setMessages(messagesWithDates);
      }
      console.log("Loaded conversation:", currentConversation.id);
    }
  }, []);

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

        if (conversationId) {
          chatRequest.conversation_id = conversationId;
        }

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

        const responseConversationId = chatResponse.conversation_id;

        if (!conversationId && responseConversationId) {
          setConversationId(responseConversationId);

          const newConversation = {
            id: responseConversationId,
            messages: [newMessage],
            createdAt: new Date().toISOString(),
          };

          conversationStorage.saveCurrentConversation(newConversation);
          console.log("Created new conversation:", responseConversationId);
        } else if (conversationId) {
          conversationStorage.addMessage(newMessage);
        }

        const assistantMessage = {
          id: messages.length + 2,
          text: chatResponse.messages,
          isUser: false,
          timestamp: new Date(),
        };
        setMessages((prevMessages) => [...prevMessages, assistantMessage]);

        conversationStorage.addMessage(assistantMessage);
      } catch (error) {
        console.error("Error sending message to backend:", error);
      }
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-chat-background h-full w-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0 w-full">
        {conversationId && (
          <div className="text-xs text-gray-500 text-center mb-2 bg-gray-100 p-2 rounded">
            Active Conversation ID: {conversationId}
            <button
              onClick={() => {
                conversationStorage.clearConversation();
                setConversationId(null);
                setMessages([
                  {
                    id: 1,
                    text: "Hello! Welcome to the chat app.",
                    isUser: false,
                    timestamp: new Date(),
                  },
                ]);
              }}
              className="ml-2 px-2 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600"
            >
              Clear Conversation
            </button>
          </div>
        )}
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
