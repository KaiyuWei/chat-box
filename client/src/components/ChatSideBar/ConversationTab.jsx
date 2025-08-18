const ConversationTab = ({ conversation, onClick, isActive = false, disabled = false }) => {
  return (
    <div
      onClick={() => !disabled && onClick && onClick(conversation)}
      className={`w-full p-3 border rounded-lg shadow-sm transition-shadow ${
        disabled 
          ? "cursor-not-allowed opacity-50" 
          : "cursor-pointer hover:shadow-md"
      } ${
        isActive
          ? "bg-blue-50 border-blue-200 text-blue-800"
          : `bg-white border-gray-200 ${!disabled ? "hover:bg-gray-50" : ""}`
      }`}
    >
      <div className="text-sm font-medium truncate">{conversation.title}</div>
    </div>
  );
};

export default ConversationTab;
