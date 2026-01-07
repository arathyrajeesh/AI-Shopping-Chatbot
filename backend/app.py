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

    # 1️⃣ Show cart items (MUST BE FIRST)
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

    # 2️⃣ List available products
    if "show" in user_msg or "products" in user_msg:
        reply = "🛍 Available products:\n"
        for p in products:
            reply += f"{p['name']} - ₹{p['price']}\n"
        return jsonify({"reply": reply})

    # 3️⃣ Price of a specific product
    if "price" in user_msg:
        for p in products:
            if p["name"].lower() in user_msg:
                return jsonify({
                    "reply": f"The price of {p['name']} is ₹{p['price']}"
                })

    # 4️⃣ Products under a budget
    if "under" in user_msg:
        price = int("".join(filter(str.isdigit, user_msg)))
        filtered = [p for p in products if p["price"] <= price]

        if not filtered:
            return jsonify({"reply": "No products found in this range."})

        reply = f"Products under ₹{price}:\n"
        for p in filtered:
            reply += f"{p['name']} - ₹{p['price']}\n"
        return jsonify({"reply": reply})

    # 5️⃣ Add product to cart
    if "add" in user_msg:
        for p in products:
            if p["name"].lower() in user_msg:
                cart.append(p)
                return jsonify({
                    "reply": f"{p['name']} added to cart. Anything else?"
                })

    # 6️⃣ Yes / No handling
    if user_msg in ["no", "nope", "nothing", "nothing else"]:
        return jsonify({
            "reply": "Okay 🙂 Type 'checkout' to confirm your order."
        })

    if user_msg in ["yes", "yeah", "yep", "sure"]:
        return jsonify({
            "reply": "Great! 😊 You can add another product or type 'show available products'."
        })

    # 7️⃣ Checkout
    if "checkout" in user_msg:
        if not cart:
            return jsonify({"reply": "Your cart is empty."})

        total = sum(p["price"] for p in cart)

        reply = (
            "✅ Order Confirmed\n"
            f"Products: {[p['name'] for p in cart]}\n"
            f"Quantity: {len(cart)}\n"
            f"Total: ₹{total}\n"
            "Status: Confirmed"
        )

        cart.clear()  # clear cart after order
        return jsonify({"reply": reply})

    # 8️⃣ Gemini fallback (LAST)
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=user_msg
    )

    return jsonify({"reply": response.text})

if __name__ == "__main__":
    app.run(debug=True)
