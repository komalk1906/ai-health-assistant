import "./ChatMessage.css";

/**
 * A single chat bubble. sender is "user" or "ai" and controls
 * alignment/coloring. isEmergency highlights the AI reply in red when the
 * backend's emergency detector fired.
 */
function ChatMessage({ sender, text, isEmergency = false }) {
  const isUser = sender === "user";

  return (
    <div className={`chat-row ${isUser ? "chat-row-user" : "chat-row-ai"}`}>
      {!isUser && <div className="chat-avatar" aria-hidden="true">🩺</div>}
      <div
        className={`chat-bubble ${isUser ? "chat-bubble-user" : "chat-bubble-ai"} ${
          isEmergency ? "chat-bubble-emergency" : ""
        }`}
      >
        {text}
      </div>
    </div>
  );
}

export default ChatMessage;
