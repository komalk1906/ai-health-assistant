import { useState, useRef, useEffect } from "react";
import ChatMessage from "../components/ChatMessage";
import LoadingSpinner from "../components/LoadingSpinner";
import Alert from "../components/Alert";
import { sendChatMessage } from "../services/api";
import "./Chat.css";

const INITIAL_MESSAGE = {
  sender: "ai",
  text: "Hello! I'm your AI Health Assistant. How can I help you today?",
};

function Chat() {
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  async function handleSend(e) {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    setMessages((prev) => [...prev, { sender: "user", text: trimmed }]);
    setInput("");
    setIsLoading(true);

    try {
      // POST /api/chat - the backend runs the emergency check first, then
      // the AI model (or the built-in knowledge base) and saves the chat.
      const data = await sendChatMessage(trimmed);
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: data.ai_response, isEmergency: data.is_emergency },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: `Sorry, I couldn't get a response. ${err.message}` },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="chat-page">
      <div className="chat-header">
        <div className="chat-header-icon" aria-hidden="true">🩺</div>
        <div>
          <h1 className="chat-header-title">AI Health Assistant</h1>
          <p className="chat-header-subtitle">General health information, available anytime</p>
        </div>
      </div>

      <Alert variant="warning">
        This assistant provides general health information and is not a doctor. It is not a
        substitute for professional medical advice, diagnosis, or treatment.
      </Alert>

      <div className="chat-window">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <p>Start the conversation by sending a message below.</p>
          </div>
        ) : (
          <>
            {messages.map((msg, index) => (
              <ChatMessage
                key={index}
                sender={msg.sender}
                text={msg.text}
                isEmergency={msg.isEmergency}
              />
            ))}
            {isLoading && (
              <div className="chat-loading">
                <LoadingSpinner label="AI Assistant is typing..." />
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-row" onSubmit={handleSend}>
        <label htmlFor="chat-input" className="visually-hidden">
          Type your health question
        </label>
        <input
          id="chat-input"
          type="text"
          className="chat-input"
          placeholder="Type your health question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          maxLength={1000}
        />
        <button type="submit" className="chat-send-btn" disabled={!input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

export default Chat;
