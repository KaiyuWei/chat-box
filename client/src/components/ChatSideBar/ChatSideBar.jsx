import { useState, useEffect } from "react";
import ConversationTab from "./ConversationTab";
import IconButton from "../ui/icon-button";
import { PlusIcon } from "../ui/icons";

const ChatSidebar = ({
  selectedConversationId,
  onConversationSelect,
  onNewConversation,
  onCloseTempConversation,
  refreshTrigger,
  tempConversation,
  isProcessing,
}) => {
  const [conversations, setConversations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

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
          console.log("No conversations found for user in sidebar");
          setConversations([]);
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const userConversations = await response.json();

      // IMPROVE: sort the array by timestamp descending order. We should not assume the conversations are sorted by timestamp.
      const sortedConversations = [...userConversations].reverse();
      setConversations(sortedConversations);
    } catch (error) {
      console.error("Error fetching conversations for sidebar:", error);
      setConversations([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUserConversations();
  }, []);

  useEffect(() => {
    if (refreshTrigger) {
      fetchUserConversations();
    }
  }, [refreshTrigger]);

  return (
    <div className="w-64 bg-gray-100 border-r border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">Conversations</h2>
        <IconButton
          variant="default"
          size="sm"
          disabled={isProcessing}
          onClick={() => {
            if (!isProcessing) {
              onNewConversation && onNewConversation();
            }
          }}
        >
          <PlusIcon size={14} />
        </IconButton>
      </div>
      <div className="flex-1 p-4 overflow-y-auto">
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className="w-full h-8 bg-gray-300 rounded animate-pulse"
              ></div>
            ))}
          </div>
        ) : conversations.length > 0 || tempConversation ? (
          <div className="space-y-2">
            {/* Show temporary conversation at the top if it exists */}
            {tempConversation && (
              <ConversationTab
                key={tempConversation.conversation_id}
                conversation={tempConversation}
                isActive={
                  tempConversation.conversation_id === selectedConversationId
                }
                onClick={isProcessing ? null : onConversationSelect}
                onClose={onCloseTempConversation}
                disabled={isProcessing}
              />
            )}
            {/* Show regular conversations */}
            {conversations.map((conversation) => (
              <ConversationTab
                key={conversation.conversation_id}
                conversation={conversation}
                isActive={
                  conversation.conversation_id === selectedConversationId
                }
                onClick={
                  isProcessing || tempConversation ? null : onConversationSelect
                }
                disabled={isProcessing || !!tempConversation}
              />
            ))}
          </div>
        ) : (
          <div className="text-gray-500 text-sm text-center mt-8">
            No conversations yet
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatSidebar;
