import { useState } from "react";

const API_URL = "http://127.0.0.1:5000/chat";

export default function Chat() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMsg = { sender: "user", text: input };
        setMessages(prev => [...prev, userMsg]);

        try {
            const res = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: input })
            });

            const data = await res.json();

            const botMsg = { sender: "bot", text: data.reply };
            setMessages(prev => [...prev, botMsg]);
        } catch (err) {
            setMessages(prev => [...prev, {
            sender: "bot",
            text: "❌ Error connecting to backend"
            }]);
        }

        setInput("");
        };


    return (
        <div>
        <h2>🛒 AI Shopping Chatbot</h2>

        {messages.map((m, i) => (
            <p key={i}><b>{m.sender}:</b> {m.text}</p>
        ))}

        <input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Type message..."
        />
        <button onClick={sendMessage}>Send</button>
        </div>
    );
}
