const ChatSidebar = () => {
  return (
    <div className="w-64 bg-gray-100 border-r border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <div className="w-24 h-6 bg-gray-300 rounded"></div>
      </div>
      <div className="flex-1 p-4">
        <div className="text-gray-700 mb-4"></div>
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="w-full h-8 bg-gray-300 rounded"></div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ChatSidebar;
