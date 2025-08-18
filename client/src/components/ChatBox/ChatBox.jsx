import ReplyBox from "./ReplyBox";
import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { ERROR_MESSAGES } from "../../utils/errorMessages";

const ChatBox = ({
  selectedConversationId,
  onConversationChange,
  onConversationCreated,
  onNoConversationsFound,
  isProcessing,
  setIsProcessing,
}) => {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [userConversations, setUserConversations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isThinking, setIsThinking] = useState(false);
  const messagesEndRef = useRef(null);

  // Dummy function to get current user id
  // TODO: remove this after an auth system is added
  const getCurrentUserId = () => {
    return 1;
  };

  // Function to scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchUserConversations = async () => {
    try {
      setIsLoading(true);
      const userId = getCurrentUserId();
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

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
          // Notify parent that user has no conversations (should clear localStorage)
          onNoConversationsFound && onNoConversationsFound();
          setMessages([
            {
              id: "welcome",
              text: ERROR_MESSAGES.WELCOME,
              isUser: false,
              timestamp: new Date(),
            },
          ]);
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const conversations = await response.json();

      setUserConversations(conversations);

      if (conversations.length > 0) {
        let conversationToLoad = null;

        if (
          selectedConversationId &&
          typeof selectedConversationId === "number"
        ) {
          conversationToLoad = conversations.find(
            (conv) => conv.conversation_id === selectedConversationId
          );
        }

        if (!conversationToLoad) {
          conversationToLoad = conversations[conversations.length - 1];
          onConversationChange &&
            onConversationChange(conversationToLoad.conversation_id);
        }

        loadConversationMessages(conversationToLoad);
      } else {
        onNoConversationsFound && onNoConversationsFound();
        setMessages([
          {
            id: "welcome",
            text: ERROR_MESSAGES.WELCOME,
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
          text: ERROR_MESSAGES.SERVER_LOADING,
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
    if (selectedConversationId) {
      if (
        typeof selectedConversationId === "string" &&
        selectedConversationId.startsWith("temp_")
      ) {
        setMessages([
          {
            id: "welcome",
            text: ERROR_MESSAGES.WELCOME,
            isUser: false,
            timestamp: new Date(),
          },
        ]);
        setConversationId(null);
      } else if (userConversations.length > 0) {
        // Handle real conversations
        const selectedConversation = userConversations.find(
          (conv) => conv.conversation_id === selectedConversationId
        );
        if (selectedConversation) {
          loadConversationMessages(selectedConversation);
        }
      }
    } else if (selectedConversationId === null) {
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

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
    onConversationCreated && onConversationCreated(responseConversationId);
    fetchUserConversations();
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
    setIsProcessing(true);

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
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-chat-background h-full w-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0 w-full">
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
                    {message.timestamp.toLocaleString()}
                  </span>
                </div>
              </div>
            ))}
            {isThinking && (
              <div className="flex justify-start">
                <div className="max-w-xs lg:max-w-md px-4 py-2 rounded-lg bg-message-other text-message-other-foreground text-left animate-pulse">
                  <div className="text-left prose prose-sm max-w-none">
                    <span className="italic text-gray-500 flex items-center">
                      I'm thinking about it
                      <span className="ml-1 flex">
                        <span
                          className="animate-bounce"
                          style={{ animationDelay: "0ms" }}
                        >
                          .
                        </span>
                        <span
                          className="animate-bounce"
                          style={{ animationDelay: "150ms" }}
                        >
                          .
                        </span>
                        <span
                          className="animate-bounce"
                          style={{ animationDelay: "300ms" }}
                        >
                          .
                        </span>
                      </span>
                    </span>
                  </div>
                </div>
              </div>
            )}
            {/* Element to scroll to */}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>
      <ReplyBox onSendMessage={handleSendMessage} isProcessing={isProcessing} />
    </div>
  );
};

export default ChatBox;
