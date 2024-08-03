import os
import requests
import sys
from dotenv import load_dotenv
from flask import Flask, request, render_template

load_dotenv()  # take environment variables from .env.
if not os.environ.get('OPENAI_API_KEY'):
    print("OPENAI_API_KEY not found in env")
    sys.exit(1)

def fetch_completion(content):
    messages = [{"role": "user", "content": content}]
    headers = {"Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}"}
    url = "https://api.openai.com/v1/chat/completions"
    data = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 1000,
    }

    response = requests.post(url, headers=headers, json=data, stream=True)
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return content

app = Flask(__name__)

@app.route('/', methods = ["GET", "POST"])
def index():
    user_message = request.form.get("question")
    if not user_message:
        return render_template("index.html")
    content = f"""
summarize the following text into sections:

{user_message}
    """
    completion = fetch_completion(content)
    return render_template("index.html",completion=completion)


if __name__ == '__main__':
    app.run(debug=True)