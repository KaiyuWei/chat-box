import { XIcon } from "../ui/icons";

const ConversationTab = ({
  conversation,
  onClick,
  onClose,
  isActive = false,
  disabled = false,
  showCloseButton = false,
}) => {
  const isTemporary =
    typeof conversation.conversation_id === "string" &&
    conversation.conversation_id.startsWith("temp_");

  const handleCloseClick = (e) => {
    e.stopPropagation(); // Prevent triggering the main onClick
    onClose && onClose(conversation);
  };

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
      <div className="flex items-center justify-between">
        <div className="text-sm font-medium truncate flex-1">
          {conversation.title}
        </div>
        {(showCloseButton || isTemporary) && (
          <button
            onClick={handleCloseClick}
            className="ml-2 p-1 rounded hover:bg-gray-200 text-gray-500 hover:text-gray-700 flex-shrink-0"
            disabled={disabled}
          >
            <XIcon size={12} />
          </button>
        )}
      </div>
    </div>
  );
};

export default ConversationTab;
