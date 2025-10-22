from groq import Groq
import os

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise RuntimeError("Please set your GROQ_API_KEY first!")

client = Groq(api_key=API_KEY)


def chat():
    print("🤖 Groq Chatbot — type 'exit' to quit\n")
    messages = [
        {"role": "system", "content": "You are a friendly AI assistant."}]

    while True:
        user = input("You: ")
        if user.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user})
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # You can change this to another model if needed
            messages=messages,
            temperature=0.5,
            max_tokens=300
        )

        reply = response.choices[0].message.content
        print("Bot:", reply, "\n")
        messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    chat()
