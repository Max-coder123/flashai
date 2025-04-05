import os
import requests
import sys
import json
import uuid

from db import (
    Flashcard,
    FlashcardSource,
    User,
    delete_flashcard_source_by_id,
    get_flashcard_source,
    get_flashcard_sources_for_user,
    get_flashcards_for_source,
    get_user,
    insert_flashcard,
    insert_flashcard_source,
    delete_flashcard_sources_for_user,
    get_user_by_name_and_password,
    insert_user,
)
from dotenv import load_dotenv
from flask_mail import Mail, Message
from flask import (
    Flask,
    jsonify,
    request,
    render_template,
    redirect,
    request_tearing_down,
    session,
    url_for,
)


load_dotenv()
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
    return json.loads(content)


def save_flashcards(content, completion, user_id):
    flashcard_source = FlashcardSource(content=content, user_id=user_id, title = completion["title"])
    source_id = insert_flashcard_source(flashcard_source)

    
    for flashcard in completion["data"]:
        flashcard = Flashcard(
            question=flashcard["question"],
            answer=flashcard["answer"],
            source_id=source_id,
            user_id=user_id,
        )
        insert_flashcard(flashcard)


app = Flask(__name__)

app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "True") == "True"
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get(
    "MAIL_DEFAULT_SENDER", os.environ.get("MAIL_USERNAME")
)

mail = Mail(app)


app.secret_key = "supersecretkey"


@app.get("/cards")
def cards():
    if "user_id" in session:
        return render_template("cards.html")

    return redirect("/")


@app.get("/")
def index():

    return render_template("index.html")


@app.route("/history")
def history():
    if "user_id" in session:
        user = get_user(session["user_id"])
        retrieved_sources = get_flashcard_sources_for_user(user.id)
        return render_template("history.html", history=retrieved_sources)

    return redirect("/")


@app.route("/dashboard")
def dashboard():
    if "user_id" in session:
        return render_template("dashboard.html")

    return redirect("/")


@app.route("/practice")
def practice():
    if "user_id" in session:
        return render_template("practice.html")

    return redirect("/")


@app.route("/studyguide")
def studyguide():
    if "user_id" in session:
        return render_template("studyguide.html")

    return redirect("/")


@app.route("/study_guide.json")
def study_guide():
    return app.send_static_file("study_guides.json")


@app.get("/flashcards/<flashcard_source_id>")
def view_flashcards(flashcard_source_id):
    retrieved_flashcards = get_flashcards_for_source(flashcard_source_id)
    retrieved_flashcards = [
        {"question": flashcard.question, "answer": flashcard.answer, "id": flashcard.id}
        for flashcard in retrieved_flashcards
    ]
    retrieved_source = get_flashcard_source(flashcard_source_id)
    return render_template("view_flashcards.html", flashcard_set=retrieved_flashcards, flashcard_source=retrieved_source)


@app.post("/api/register")
def register():
    user_name = request.json.get("username")
    password = request.json.get("password")

    if not user_name or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user = User(username=user_name, password=password)
    user_id = insert_user(user)

    if user_id:
        session["user_id"] = user_id
        return (
            jsonify({"message": "registration successful", "username": user.username}),
            200,
        )
    else:
        return jsonify({"error": "user already exists"}), 401


@app.post("/api/login")
def login():
    user_name = request.json.get("username")
    password = request.json.get("password")

    if not user_name or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user = get_user_by_name_and_password(user_name, password)

    if user:
        session["user_id"] = user.id
        return jsonify({"message": "Login successful", "username": user.username}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@app.get("/api/logout")
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out successfully"}), 200


@app.route("/api/feedback", methods=["POST"])
def feedback():
    data = request.get_json()
    name = data.get("name")
    subject = data.get("subject")
    message = data.get("message")

    if not all([name, subject, message]):
        return (
            jsonify(
                {"error": "Missing fields. Please provide name, subject, and message."}
            ),
            400,
        )

    msg = Message(
        subject=subject,
        recipients=["maxx68329@gmail.com"],
        body=f"Feedback received from {name}:\n\n{message}",
    )

    try:
        mail.send(msg)
        return (
            jsonify({"status": "success", "message": "Feedback sent successfully!"}),
            200,
        )
    except Exception as e:
        print("Error sending email:", e)
        return (
            jsonify({"error": "Error sending feedback. Please try again later."}),
            500,
        )


@app.post("/api/completion")
def completion():
    if "user_id" not in session:
        return {"error": "unauthorized"}, 401
    user_message = request.json.get("question")
    # if not user_message:

    content = f"""
generate flashcards for the following text, giving an individual flashcard for each question/answer pair, and provide a title that summarizes the text concisely without unnecessary words:

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
        }},
        {{
            "question": "question 2 about the text", 
            "answer": "answer 2 for question 2",
        }}
    ],
    "title": "concise summary of flashcards"
}}
```

    """
    completion = fetch_json_completion(content)
    save_flashcards(user_message, completion, session["user_id"])

    return completion

@app.route("/api/clear-history", methods=["DELETE"])
def clear_history():
    if "user_id" not in session:
        return {"error": "unauthorized"}, 401
    delete_flashcard_sources_for_user(session["user_id"])
    return {"status":"success"}

@app.delete("/api/flashcard-source/<flashcard_source_id>")
def delete_flashcard_source(flashcard_source_id):
    if "user_id" not in session:
        return {"error": "unauthorized"}, 401

    deleted = delete_flashcard_source_by_id(flashcard_source_id, session["user_id"])
    if deleted:
        return {"status": "success"}
    return {"status": "failure"}, 404


if __name__ == "__main__":
    app.run(debug=True)
