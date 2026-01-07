import { useState } from "react";

const API_URL = "http://127.0.0.1:5000/chat";

export default function Chat() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");

    const sendMessage = async () => {
        if (!input.trim()) return;

        setMessages([...messages, { sender: "user", text: input }]);

        const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input })
        });

        const data = await res.json();
        setMessages(prev => [...prev, { sender: "bot", text: data.reply }]);
        setInput("");
    };

    return (
        <div className="chat">
        <h2>🛒 AI Shopping Chatbot</h2>

        <div className="box">
            {messages.map((m, i) => (
            <div key={i} className={m.sender}>
                {m.text}
            </div>
            ))}
        </div>

        <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && sendMessage()}
            placeholder="Type message..."
        />
        <button onClick={sendMessage}>Send</button>
        </div>
  );
}
