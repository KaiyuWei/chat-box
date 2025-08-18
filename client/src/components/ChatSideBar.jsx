import { useState, useEffect } from "react";

const ChatSidebar = () => {
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

      console.log(`Fetching conversations for sidebar, user ID: ${userId}`);

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
      console.log("Sidebar conversations fetched successfully:", userConversations);

      // Sort conversations with latest on top (reverse order)
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

  return (
    <div className="w-64 bg-gray-100 border-r border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800">Conversations</h2>
      </div>
      <div className="flex-1 p-4 overflow-y-auto">
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="w-full h-8 bg-gray-300 rounded animate-pulse"></div>
            ))}
          </div>
        ) : conversations.length > 0 ? (
          <div className="space-y-2">
            {conversations.map((conversation) => (
              <div
                key={conversation.conversation_id}
                className="w-full p-3 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer"
              >
                <div className="text-sm font-medium text-gray-800 truncate">
                  {conversation.title}
                </div>
              </div>
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
