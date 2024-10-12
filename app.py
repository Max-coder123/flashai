import os
import requests
import sys
import json
import uuid
from dotenv import load_dotenv
from flask import Flask, request, render_template, request_tearing_down, url_for

load_dotenv()  # take environment variables from .env.
if not os.environ.get("OPENAI_API_KEY"):
    print("OPENAI_API_KEY not found in env")
    sys.exit(1)


def fetch_json_completion(content):
    """fetches a json completion from openAI, content must contain the word json"""
    messages = [{"role": "user", "content": content}]
    headers = {"Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}"}
    url = "https://api.openai.com/v1/chat/completions"
    data = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 5000,
        "response_format": {"type": "json_object"},
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return content


def save_flashcards(content, flashcards):
    file_path = "flashcards_history.json"

    # Check if the file exists, if not create an empty one
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            json.dump([], file)

    # Load current history
    with open(file_path, "r") as file:
        history = json.load(file)

    flashcard_id = str(uuid.uuid4())

    # Append new flashcards to the history
    history.append({"id": flashcard_id, "input": content, "flashcards": flashcards})

    # Save updated history
    with open(file_path, "w") as file:
        json.dump(history, file)


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    user_message = request.form.get("question")
    if not user_message:
        return render_template("index.html", completion={"data": []})
    content = f"""
generate flashcards for the following text:

'''

{user_message}

'''

please return the following json structure:


```
{{
    "data": [
        {{
            "question": "question 1 about the text", 
            "answer": "answer 1 for question 1",
            "explanation": "explanation of answer 1"
        }},
        {{
            "question": "question 2 about the text", 
            "answer": "answer 2 for question 2",
            "explanation": "explanation of answer 2"
        }}
    ]
}}
```

    """
    completion = fetch_json_completion(content)
    save_flashcards(user_message, completion)
    return render_template("index.html", completion=completion)


@app.route("/api/completion")
def completion():
    return fetch_json_completion("return the answer in json format: what is 5+5?")


@app.route("/history")
def history():
    flashcards_history = load_flashcard_history()
    return render_template("history.html", history=flashcards_history)


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/practice")
def practice():
    return render_template("practice.html")


@app.route("/studyguide")
def studyguide():
    return render_template("studyguide.html")


@app.route("/study_guide.json")
def study_guide():
    return app.send_static_file("study_guides.json")


def load_flashcard_history():
    file_path = "flashcards_history.json"
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r") as file:
        history = json.load(file)

    return history


@app.route("/clear-history", methods=["POST"])
def clear_history():
    file_path = "flashcards_history.json"
    if os.path.exists(file_path):
        with open(file_path, "w") as file:
            json.dump([], file)  
    return render_template("history.html", history=[])  


@app.route("/flashcards/<flashcard_id>")
def view_flashcards(flashcard_id):
    flashcards_history = load_flashcard_history()
    flashcard_set = next(
        (entry for entry in flashcards_history if entry["id"] == flashcard_id), None
    )
    if not flashcard_set:
        return "Flashcards not found", 404
    return render_template("view_flashcards.html", flashcard_set=flashcard_set)


if __name__ == "__main__":
    app.run(debug=True)
