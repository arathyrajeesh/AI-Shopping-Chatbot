from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import json, os

load_dotenv()

app = Flask(__name__)
CORS(app)

cart = []
last_order = None

# ✅ Correct Gemini setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

with open("products.json") as f:
    products = json.load(f)

@app.route("/chat", methods=["POST"])
def chat():
    global last_order
    user_msg = request.json.get("message", "").lower()

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

    if "last order" in user_msg or "show order" in user_msg or "order summary" in user_msg:
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

    if "show" in user_msg or "products" in user_msg:
        reply = "🛍 Available products:\n"
        for p in products:
            reply += f"{p['name']} - ₹{p['price']}\n"
        return jsonify({"reply": reply})

    if "price" in user_msg:
        for p in products:
            if p["name"].lower() in user_msg:
                return jsonify({"reply": f"The price of {p['name']} is ₹{p['price']}"})

    if "under" in user_msg:
        price = int("".join(filter(str.isdigit, user_msg)))
        filtered = [p for p in products if p["price"] <= price]

        if not filtered:
            return jsonify({"reply": "No products found in this range."})

        reply = f"Products under ₹{price}:\n"
        for p in filtered:
            reply += f"{p['name']} - ₹{p['price']}\n"
        return jsonify({"reply": reply})

    if "add" in user_msg:
        for p in products:
            if p["name"].lower() in user_msg:
                cart.append(p)
                return jsonify({"reply": f"{p['name']} added to cart. Anything else?"})

    if user_msg in ["no", "nope", "nothing", "nothing else"]:
        return jsonify({"reply": "Okay 🙂 Type 'checkout' to confirm your order."})

    if user_msg in ["yes", "yeah", "yep", "sure"]:
        return jsonify({"reply": "Great! 😊 You can add another product or type 'show available products'."})

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

    # ✅ Gemini fallback
    response = model.generate_content(user_msg)
    return jsonify({"reply": response.text})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
