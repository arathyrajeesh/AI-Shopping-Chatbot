import { useState } from "react";

const API_URL = "https://ai-shopping-chatbot-ufc6.onrender.com/chat";

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

        if (!res.ok) throw new Error("Backend error");

        const data = await res.json();
        setMessages(prev => [...prev, { sender: "bot", text: data.reply }]);
        } catch (error) {
        setMessages(prev => [
            ...prev,
            { sender: "bot", text: "Error connecting to backend" }
        ]);
        }
    };

    return (
        <div style={styles.container}>
        <h2 style={styles.title}>AI Shopping Chatbot</h2>

        <div style={styles.chatBox}>
            {messages.map((m, i) => (
            <div
                key={i}
                style={{
                ...styles.message,
                alignSelf: m.sender === "user" ? "flex-end" : "flex-start",
                backgroundColor: m.sender === "user" ? "#DCF8C6" : "#F1F1F1"
                }}
            >
                <b>{m.sender}:</b> {m.text}
            </div>
            ))}
        </div>

        <div style={styles.inputRow}>
            <input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Type a message..."
            style={styles.input}
            onKeyDown={e => e.key === "Enter" && sendMessage()}
            />
            <button onClick={sendMessage} style={styles.button}>
            Send
            </button>
        </div>
        </div>
    );
}


const styles = {
    container: {
        maxWidth: "500px",
        margin: "40px auto",
        padding: "20px",
        borderRadius: "10px",
        boxShadow: "0 4px 10px rgba(0,0,0,0.1)",
        fontFamily: "Arial, sans-serif",
        backgroundColor: "#fff"
    },
    title: {
        textAlign: "center",
        marginBottom: "15px"
    },
    chatBox: {
        height: "300px",
        overflowY: "auto",
        border: "1px solid #ddd",
        padding: "10px",
        marginBottom: "10px",
        display: "flex",
        flexDirection: "column",
        gap: "8px",
        backgroundColor: "#fafafa"
    },
    message: {
        padding: "8px 12px",
        borderRadius: "8px",
        maxWidth: "80%",
        fontSize: "14px"
    },
    inputRow: {
        display: "flex",
        gap: "10px"
    },
    input: {
        flex: 1,
        padding: "8px",
        borderRadius: "6px",
        border: "1px solid #ccc",
        fontSize: "14px"
    },
    button: {
        padding: "8px 16px",
        borderRadius: "6px",
        border: "none",
        backgroundColor: "#4CAF50",
        color: "#fff",
        cursor: "pointer",
        fontSize: "14px"
    }
};
