import { useState } from "react";

const API_URL = "http://127.0.0.1:5000/chat";

export default function Chat() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userText = input;
        setMessages(prev => [...prev, { sender: "user", text: userText }]);
        setInput("");

        try {
        const res = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userText })
        });

        if (!res.ok) {
            throw new Error("Backend error");
        }

        const data = await res.json();

        setMessages(prev => [
            ...prev,
            { sender: "bot", text: data.reply }
        ]);

        } catch (error) {
        setMessages(prev => [
            ...prev,
            { sender: "bot", text: "Error connecting to backend" }
        ]);
        }
    };

    return (
        <div style={{ maxWidth: "500px", margin: "20px auto" }}>
        <h2>🛒 AI Shopping Chatbot</h2>

        <div style={{ minHeight: "200px", border: "1px solid #ccc", padding: "10px" }}>
            {messages.map((m, i) => (
            <p key={i}>
                <b>{m.sender}:</b> {m.text}
            </p>
            ))}
        </div>

        <input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Type message..."
            style={{ width: "70%" }}
            onKeyDown={e => e.key === "Enter" && sendMessage()}
        />
        <button onClick={sendMessage}>Send</button>
        </div>
    );
}
