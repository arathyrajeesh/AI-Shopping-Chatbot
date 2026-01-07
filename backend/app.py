from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Gemini setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

# Load products
with open("products.json") as f:
    products = json.load(f)

cart = []

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").lower()

    # 1️⃣ Show products
    if "show" in user_msg or "products" in user_msg:
        reply = "🛍 Available products:\n"
        for p in products:
            reply += f"{p['name']} - ₹{p['price']}\n"
        return jsonify({"reply": reply})

    # 2️⃣ Filter by price
    if "under" in user_msg:
        price = int("".join(filter(str.isdigit, user_msg)))
        filtered = [p for p in products if p["price"] <= price]
        reply = f"Products under ₹{price}:\n"
        for p in filtered:
            reply += f"{p['name']} - ₹{p['price']}\n"
        return jsonify({"reply": reply})

    # 3️⃣ Add to cart
    if "add" in user_msg:
        for p in products:
            if p["name"].lower() in user_msg:
                cart.append(p)
                return jsonify({"reply": f"✅ {p['name']} added to cart"})

    # 4️⃣ Checkout
    if "checkout" in user_msg:
        total = sum(p["price"] for p in cart)
        return jsonify({
            "reply": f"🎉 Order Confirmed\nItems: {len(cart)}\nTotal: ₹{total}"
        })

    # 5️⃣ Gemini fallback
    ai_reply = model.generate_content(user_msg)
    return jsonify({"reply": ai_reply.text})

if __name__ == "__main__":
    app.run(debug=True)
