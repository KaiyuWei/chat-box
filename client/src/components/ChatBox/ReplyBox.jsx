import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send } from "lucide-react";

const ReplyBox = ({ onSendMessage, isProcessing = false }) => {
  const [inputValue, setInputValue] = useState("");

  const handleSendMessage = () => {
    if (inputValue.trim() && !isProcessing) {
      onSendMessage(inputValue);
      setInputValue("");
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !isProcessing) {
      handleSendMessage();
    }
  };

  return (
    <div className="p-4 border-t border-gray-200 bg-gray-50">
      <div className="flex space-x-2">
        <Input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={isProcessing ? "Processing..." : "Type a message..."}
          className="flex-1 bg-white border-gray-300"
          disabled={isProcessing}
        />
        <Button
          onClick={handleSendMessage}
          size="icon"
          className="bg-blue-600 hover:bg-blue-700 text-white"
          disabled={isProcessing}
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};

export default ReplyBox;
