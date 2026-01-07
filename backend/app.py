from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
import json, os

load_dotenv()

app = Flask(__name__)
CORS(app)

# Global state
cart = []
last_order = None

# Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Load product data
with open("products.json") as f:
    products = json.load(f)

@app.route("/chat", methods=["POST"])
def chat():
    global last_order
    user_msg = request.json.get("message", "").lower()

    # 1️⃣ Show cart
    if "show cart" in user_msg or user_msg == "cart":
        if not cart:
            return jsonify({"reply": "🛒 Your cart is empty."})

        reply = "🛒 Your Cart:\n"
        total = 0
        for i, p in enumerate(cart, start=1):
            reply += f"{i}. {p['name']} - ₹{p['price']}\n"
            total += p["price"]

        reply += f"\nTotal items: {len(cart)}"
        reply += f"\nTotal price: ₹{total}"
        return jsonify({"reply": reply})

    # 2️⃣ Show last order
    # Show last order summary
    if "last order" in user_msg or user_msg == "show order" or "order summary" in user_msg:
        if not last_order:
            return jsonify({"reply": "You have not placed any orders yet."})

        reply = (
            "🧾 Last Order Summary\n"
            f"Products: {last_order['products']}\n"
            f"Quantity: {last_order['quantity']}\n"
            f"Total: ₹{last_order['total']}\n"
            f"Status: {last_order['status']}"
        )

        return jsonify({"reply": reply})


    # 3️⃣ Show products
    if "show" in user_msg or "products" in user_msg:
        reply = "🛍 Available products:\n"
        for p in products:
            reply += f"{p['name']} - ₹{p['price']}\n"
        return jsonify({"reply": reply})

    # 4️⃣ Price query
    if "price" in user_msg:
        for p in products:
            if p["name"].lower() in user_msg:
                return jsonify({
                    "reply": f"The price of {p['name']} is ₹{p['price']}"
                })

    # 5️⃣ Under budget
    if "under" in user_msg:
        price = int("".join(filter(str.isdigit, user_msg)))
        filtered = [p for p in products if p["price"] <= price]

        if not filtered:
            return jsonify({"reply": "No products found in this range."})

        reply = f"Products under ₹{price}:\n"
        for p in filtered:
            reply += f"{p['name']} - ₹{p['price']}\n"
        return jsonify({"reply": reply})

    # 6️⃣ Add to cart
    if "add" in user_msg:
        for p in products:
            if p["name"].lower() in user_msg:
                cart.append(p)
                return jsonify({
                    "reply": f"{p['name']} added to cart. Anything else?"
                })

    # 7️⃣ Yes / No handling
    if user_msg in ["no", "nope", "nothing", "nothing else"]:
        return jsonify({"reply": "Okay 🙂 Type 'checkout' to confirm your order."})

    if user_msg in ["yes", "yeah", "yep", "sure"]:
        return jsonify({
            "reply": "Great! 😊 You can add another product or type 'show available products'."
        })

    # 8️⃣ Checkout (ONLY ONE BLOCK)
    if "checkout" in user_msg:
        if not cart:
            return jsonify({"reply": "Your cart is empty."})

        total = sum(p["price"] for p in cart)

        last_order = {
            "products": [p["name"] for p in cart],
            "quantity": len(cart),
            "total": total,
            "status": "Confirmed"
        }

        reply = (
            "✅ Order Confirmed\n"
            f"Products: {last_order['products']}\n"
            f"Quantity: {last_order['quantity']}\n"
            f"Total: ₹{last_order['total']}\n"
            f"Status: {last_order['status']}"
        )

        cart.clear()
        return jsonify({"reply": reply})

    # 9️⃣ Gemini fallback (LAST)
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=user_msg
    )

    return jsonify({"reply": response.text})

if __name__ == "__main__":
    app.run(debug=True)
