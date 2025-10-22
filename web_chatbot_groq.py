from flask import Flask, render_template_string, request, jsonify
from groq import Groq
import os

# Load your API key
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise RuntimeError("Please set your GROQ_API_KEY first!")

client = Groq(api_key=API_KEY)

# Persistent chat memory
chat_history = []

# HTML + CSS + JS template with pastel theme
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Groq AI Chat</title>
<style>
body { 
    font-family: Arial, sans-serif; 
    background: #e0f7fa; /* pastel mint background */ 
    display:flex; 
    justify-content:center; 
    padding-top:50px; 
}
#chat-container { 
    width:500px; 
    max-width:90%; 
    background:#fef9f9; /* pastel cream */ 
    border-radius:10px; 
    box-shadow:0 0 15px rgba(0,0,0,0.2); 
    overflow:hidden; 
    display:flex; 
    flex-direction:column; 
}
#messages { 
    height:450px; 
    overflow-y:auto; 
    padding:20px; 
    display:flex; 
    flex-direction:column; 
    gap:10px; 
}
.message { 
    padding:10px 15px; 
    border-radius:20px; 
    max-width:80%; 
    word-wrap: break-word;
}
.user { 
    align-self:flex-end; 
    background:#a0c4ff; /* pastel blue */ 
    color:white; 
}
.bot { 
    align-self:flex-start; 
    background:#ffd6a5; /* pastel peach */ 
    color:black; 
}
#input-form { 
    display:flex; 
    border-top:1px solid #ccc; 
}
#user-input { 
    flex:1; 
    padding:10px; 
    border:none; 
    outline:none; 
    background:#fff1f3; /* pastel pink */ 
}
#send-btn { 
    padding:10px; 
    background:#b5ead7; /* pastel green */ 
    color:white; 
    border:none; 
    cursor:pointer; 
}
#send-btn:hover { 
    background:#a0e1c6; 
}
</style>
</head>
<body>
<div id="chat-container">
    <div id="messages">
        {% for u,b in history %}
            <div class="message user">{{u}}</div>
            <div class="message bot">{{b}}</div>
        {% endfor %}
    </div>
    <form id="input-form">
        <input type="text" id="user-input" placeholder="Type a message..." required autofocus>
        <button type="submit" id="send-btn">Send</button>
    </form>
</div>

<script>
const form = document.getElementById("input-form");
const input = document.getElementById("user-input");
const messagesDiv = document.getElementById("messages");

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const userMessage = input.value.trim();
    if(!userMessage) return;

    // Show user message
    const userDiv = document.createElement("div");
    userDiv.className = "message user";
    userDiv.textContent = userMessage;
    messagesDiv.appendChild(userDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    input.value = "";

    // Call backend API
    const response = await fetch("/send", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({message: userMessage})
    });
    const data = await response.json();

    // Show bot message
    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    botDiv.textContent = data.reply;
    messagesDiv.appendChild(botDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
});
</script>
</body>
</html>
"""

app = Flask(__name__)

# Home route


@app.route("/")
def index():
    return render_template_string(HTML, history=chat_history)

# API endpoint for sending messages


@app.route("/send", methods=["POST"])
def send():
    user_text = request.json.get("message")
    if not user_text:
        return jsonify({"reply": "I didn't understand that!"})

    # Prepare system prompt for emotional intelligence, friendliness, adaptiveness
    system_prompt = {
        "role": "system",
        "content": (
            "You are an AI chatbot that is emotionally intelligent, empathy-first, friendly, "
            "informative, and adaptive. "
            "Sense the user's mood and respond accordingly: "
            "celebrate if happy, comfort if sad/stressed/frustrated. "
            "Use casual, polite language, occasional light humor. "
            "Provide clear, concise explanations with examples if needed. "
            "Adapt your responses based on previous messages. "
            "Encourage engagement, be positive, safe, and neutral. "
            "Assume a pastel-colored interface and complement the tone."
        )
    }

    # Keep last 10 messages for context
    prompt_messages = [system_prompt]
    for u, b in chat_history[-10:]:
        prompt_messages.append({"role": "user", "content": u})
        prompt_messages.append({"role": "assistant", "content": b})
    prompt_messages.append({"role": "user", "content": user_text})

    # Call Groq API
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=prompt_messages,
        temperature=0.75,
        max_tokens=400
    )
    bot_reply = response.choices[0].message.content

    # Save to memory
    chat_history.append((user_text, bot_reply))

    return jsonify({"reply": bot_reply})


if __name__ == "__main__":
    app.run(debug=False)
