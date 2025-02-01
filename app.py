import os
import requests
import sys
import json
import uuid
from db import (
    Flashcard,
    FlashcardSource,
    get_flashcard_sources_for_user,
    get_flashcards_for_source,
    get_user,
    insert_flashcard,
    insert_flashcard_source,
    delete_flashcard_sources_for_user,
    get_user_by_name_and_password
)
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template, request_tearing_down, session, url_for


user_id = "1b27d88b-73f8-48b4-9132-c447146ca172"

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


def save_flashcards(content, completion):
    flashcard_source = FlashcardSource(content=content, user_id=user_id)

    source_id = insert_flashcard_source(flashcard_source)

    completion = json.loads(completion)
    for flashcard in completion["data"]:
        flashcard = Flashcard(
            question=flashcard["question"],
            answer=flashcard["answer"],
            explanation=flashcard["explanation"],
            source_id=source_id,
            user_id=user_id,
        )
        insert_flashcard(flashcard)



app = Flask(__name__)

app.secret_key = "supersecretkey"


@app.get("/")
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


@app.post("/api/completion")
def completion():
    user_message = request.json.get("question")
    # if not user_message:

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

    return completion


@app.route("/history")
def history():
    retrieved_sources = get_flashcard_sources_for_user(user_id)
    return render_template("history.html", history=retrieved_sources)



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


@app.route("/clear-history", methods=["DELETE"])
def clear_history():
    delete_flashcard_sources_for_user(user_id)
    return render_template("history.html", history=[])


@app.route("/flashcards/<flashcard_source_id>")
def view_flashcards(flashcard_source_id):
    retrieved_flashcards = get_flashcards_for_source(flashcard_source_id)
    retrieved_flashcards = [
        {"question": flashcard.question, "answer": flashcard.answer, "id": flashcard.id}
        for flashcard in retrieved_flashcards
    ]
    return render_template("view_flashcards.html", flashcard_set=retrieved_flashcards)

@app.post("/login")
def login():
    user_name = request.json.get("username")
    password = request.json.get("password")

    if not user_name or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user = get_user_by_name_and_password(user_name, password)
    
    if user:
        session["user"] = user.username 
        return jsonify({"message": "Login successful", "username": user.username}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.get("/profile")
def profile():
    if "user" in session:
        return jsonify({"message": "Welcome!", "username": session["user"]}), 200
    else:
        return jsonify({"error": "Not logged in"}), 401
 
@app.get("/logout")
def logout():
    session.pop("user", None)  
    return jsonify({"message": "Logged out successfully"}), 200




if __name__ == "__main__":
    app.run(debug=True)
