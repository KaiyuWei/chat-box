import logo from "../assets/my_logo.png";

const ChatTopBar = () => {
  return (
    <div className="h-14 bg-chat-secondary border-b border-border flex items-center justify-between px-4">
      <div className="flex items-center space-x-3">
        <img 
          src={logo} 
          alt="Logo" 
          className="h-8 w-auto"
        />
      </div>
    </div>
  );
};

export default ChatTopBar;
