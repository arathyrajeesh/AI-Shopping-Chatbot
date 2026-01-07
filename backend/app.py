from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
import json, os

load_dotenv()

app = Flask(__name__)
CORS(app)

# Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Load product data
with open("products.json") as f:
    products = json.load(f)

# In-memory cart
cart = []

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").lower()

    # 1️⃣ List available products
    if "show" in user_msg or "products" in user_msg:
        reply = "🛍 Available products:\n"
        for p in products:
            reply += f"{p['name']} - ₹{p['price']}\n"
        return jsonify({"reply": reply})

    # 2️⃣ Price of a specific product
    if "price" in user_msg:
        for p in products:
            if p["name"].lower() in user_msg:
                return jsonify({
                    "reply": f"The price of {p['name']} is ₹{p['price']}"
                })

    # 3️⃣ Products under a budget
    if "under" in user_msg:
        price = int("".join(filter(str.isdigit, user_msg)))
        filtered = [p for p in products if p["price"] <= price]

        if not filtered:
            return jsonify({"reply": "No products found in this range."})

        reply = f"Products under ₹{price}:\n"
        for p in filtered:
            reply += f"{p['name']} - ₹{p['price']}\n"
        return jsonify({"reply": reply})

    # 4️⃣ Add product to cart
    if "add" in user_msg:
        for p in products:
            if p["name"].lower() in user_msg:
                cart.append(p)
                return jsonify({
                    "reply": f"{p['name']} added to cart. Anything else?"
                })

    # 5️⃣ Checkout & confirm order
    if "checkout" in user_msg:
        if not cart:
            return jsonify({"reply": "Your cart is empty."})

        total = sum(p["price"] for p in cart)
        quantity = len(cart)

        order = {
            "products": [p["name"] for p in cart],
            "quantity": quantity,
            "total_price": total,
            "status": "Confirmed"
        }

        return jsonify({
            "reply": (
                "✅ Order Confirmed\n"
                f"Products: {order['products']}\n"
                f"Quantity: {order['quantity']}\n"
                f"Total: ₹{order['total_price']}\n"
                f"Status: {order['status']}"
            )
        })

    # 6️⃣ Gemini AI fallback
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=user_msg
    )

    return jsonify({"reply": response.text})

if __name__ == "__main__":
    app.run(debug=True)
