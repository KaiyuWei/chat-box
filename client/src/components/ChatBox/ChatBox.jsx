import ReplyBox from "./ReplyBox";
import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";

const ChatBox = ({
  selectedConversationId,
  onConversationChange,
  onConversationCreated,
}) => {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [userConversations, setUserConversations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isThinking, setIsThinking] = useState(false);

  // Dummy function to get current user id
  // TODO: remove this after an auth system is added
  const getCurrentUserId = () => {
    return 1;
  };

  const fetchUserConversations = async () => {
    try {
      setIsLoading(true);
      const userId = getCurrentUserId();
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

      console.log(`Fetching conversations for user ID: ${userId}`);

      const response = await fetch(
        `${apiBaseUrl}/api/user-conv-with-msg/${userId}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        if (response.status === 404) {
          console.log("No conversations found for user");
          setUserConversations([]);
          setMessages([
            {
              id: "welcome",
              text: "Hello! Welcome to the chat app. Start a new conversation!",
              isUser: false,
              timestamp: new Date(),
            },
          ]);
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const conversations = await response.json();
      console.log("User conversations fetched successfully:", conversations);
      console.log(`Total conversations found: ${conversations.length}`);

      conversations.forEach((conv, index) => {
        console.log(`Conversation ${index + 1}:`, {
          id: conv.conversation_id,
          title: conv.title,
          messageCount: conv.messages.length,
          createdAt: conv.created_at,
        });
      });

      setUserConversations(conversations);

      // Load the latest conversation (last in array)
      if (conversations.length > 0) {
        const latestConversation = conversations[conversations.length - 1];
        loadConversationMessages(latestConversation);

        onConversationChange &&
          onConversationChange(latestConversation.conversation_id);
      } else {
        setMessages([
          {
            id: "welcome",
            text: "Hello! Welcome to the chat app. Start a new conversation!",
            isUser: false,
            timestamp: new Date(),
          },
        ]);
      }
    } catch (error) {
      console.error("Error fetching user conversations:", error);
      setUserConversations([]);
      setMessages([
        {
          id: "error",
          text: "Sorry, there was an error loading your conversations. Please try refreshing the page.",
          isUser: false,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadConversationMessages = (conversation) => {
    setConversationId(conversation.conversation_id);

    const convertedMessages = conversation.messages.map((apiMessage) => ({
      id: apiMessage.id,
      text: apiMessage.content,
      isUser: apiMessage.sender === "user",
      timestamp: new Date(apiMessage.created_at),
    }));

    setMessages(convertedMessages);
  };

  useEffect(() => {
    fetchUserConversations();
  }, []);

  useEffect(() => {
    if (selectedConversationId && userConversations.length > 0) {
      // Check if it's a temporary conversation ID
      if (
        typeof selectedConversationId === "string" &&
        selectedConversationId.startsWith("temp_")
      ) {
        // This is a temporary conversation - show welcome message
        setMessages([
          {
            id: "welcome",
            text: "Hello! Welcome to the chat app. Start a new conversation!",
            isUser: false,
            timestamp: new Date(),
          },
        ]);
        setConversationId(null);
      } else {
        // This is a real conversation - load its messages
        const selectedConversation = userConversations.find(
          (conv) => conv.conversation_id === selectedConversationId
        );
        if (selectedConversation) {
          loadConversationMessages(selectedConversation);
        }
      }
    } else if (selectedConversationId === null) {
      // Start a new conversation - clear messages and reset state
      setMessages([
        {
          id: "welcome",
          text: "Hello! Welcome to the chat app. Start a new conversation!",
          isUser: false,
          timestamp: new Date(),
        },
      ]);
      setConversationId(null);
    } else if (
      selectedConversationId &&
      typeof selectedConversationId === "string" &&
      selectedConversationId.startsWith("temp_")
    ) {
      // Handle temporary conversation when userConversations is empty or not loaded yet
      setMessages([
        {
          id: "welcome",
          text: "Hello! Welcome to the chat app. Start a new conversation!",
          isUser: false,
          timestamp: new Date(),
        },
      ]);
      setConversationId(null);
    }
  }, [selectedConversationId, userConversations]);

  const createMessage = (text, isUser, id = null) => {
    return {
      id: id || `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      text,
      isUser,
      timestamp: new Date(),
    };
  };

  const sendChatRequest = async (messageText) => {
    const chatRequest = {
      messages: [
        {
          role: "user",
          content: messageText,
        },
      ],
    };

    if (
      selectedConversationId &&
      !(
        typeof selectedConversationId === "string" &&
        selectedConversationId.startsWith("temp_")
      )
    ) {
      chatRequest.conversation_id = selectedConversationId;
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

    return response.json();
  };

  const handleNewConversation = (responseConversationId, userMessage) => {
    setConversationId(responseConversationId);
    onConversationChange && onConversationChange(responseConversationId);
    // Notify parent that a new conversation was created
    onConversationCreated && onConversationCreated(responseConversationId);
  };

  const handleAssistantResponse = (chatResponse) => {
    const assistantMessage = createMessage(chatResponse.messages, false);
    setMessages((prevMessages) => [...prevMessages, assistantMessage]);
    return assistantMessage;
  };

  const handleSendMessage = async (messageText) => {
    if (!messageText.trim()) return;

    const userMessage = createMessage(messageText, true);
    setMessages([...messages, userMessage]);

    setIsThinking(true);

    try {
      const chatResponse = await sendChatRequest(messageText);

      const responseConversationId = chatResponse.conversation_id;

      if (
        (!selectedConversationId ||
          (typeof selectedConversationId === "string" &&
            selectedConversationId.startsWith("temp_"))) &&
        responseConversationId
      ) {
        handleNewConversation(responseConversationId, userMessage);
      }

      handleAssistantResponse(chatResponse);
    } catch (error) {
      console.error("Error sending message to backend:", error);
      // TODO: Add user-facing error handling (e.g., show error message in UI)
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-chat-background h-full w-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0 w-full">
        {selectedConversationId && (
          <div className="text-xs text-gray-500 text-center mb-2 bg-gray-100 p-2 rounded">
            Active Conversation ID: {selectedConversationId}
          </div>
        )}
        {isLoading ? (
          <div className="flex justify-center items-center h-32">
            <div className="text-gray-500">Loading conversations...</div>
          </div>
        ) : (
          <>
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
                      ? "bg-message-user text-message-user-foreground text-left"
                      : "bg-message-other text-message-other-foreground text-left"
                  }`}
                >
                  <div className="text-left prose prose-sm max-w-none">
                    <ReactMarkdown>{message.text}</ReactMarkdown>
                  </div>
                  <span className="text-xs opacity-70 mt-1 block text-left">
                    {message.timestamp.toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
            {isThinking && (
              <div className="flex justify-start">
                <div className="max-w-xs lg:max-w-md px-4 py-2 rounded-lg bg-message-other text-message-other-foreground text-left">
                  <div className="text-left prose prose-sm max-w-none">
                    <span className="italic text-gray-500">
                      I'm thinking about it...
                    </span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
      <ReplyBox onSendMessage={handleSendMessage} />
    </div>
  );
};

export default ChatBox;
