const ConversationTab = ({ conversation, onClick, isActive = false }) => {
  return (
    <div
      onClick={() => onClick && onClick(conversation)}
      className={`w-full p-3 border rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer ${
        isActive
          ? "bg-blue-50 border-blue-200 text-blue-800"
          : "bg-white border-gray-200 hover:bg-gray-50"
      }`}
    >
      <div className="text-sm font-medium truncate">{conversation.title}</div>
    </div>
  );
};

export default ConversationTab;
