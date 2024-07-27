import os
import requests
import sys
from dotenv import load_dotenv
from flask import Flask, request, render_template

load_dotenv()  # take environment variables from .env.
if not os.environ.get('OPENAI_API_KEY'):
    print("OPENAI_API_KEY not found in env")
    sys.exit(1)


app = Flask(__name__)

@app.route('/', methods = ["GET", "POST"])
def index():
    content = request.form.get("question", request.args.get("question","hello"))
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
    return render_template("index.html",content=content)


if __name__ == '__main__':
    app.run(debug=True)