import os
import bcrypt
import requests
import sys
import json
import uuid
from pathlib import Path
from functools import wraps

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")

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
    get_user_by_name,
    insert_user,
    update_password,
    update_username,
)

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


if not os.environ.get("OPENAI_API_KEY"):
    print("OPENAI_API_KEY not found in env")


def login_required(f):
    """Decorator to require login for routes"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/")
        user = get_user(session["user_id"])
        if not user:
            session.pop("user_id", None)
            return redirect("/")
        return f(user, *args, **kwargs)

    return decorated_function


def api_login_required(f):
    """Decorator to require login for API routes"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return {"error": "unauthorized"}, 401
        user = get_user(session["user_id"])
        if not user:
            session.pop("user_id", None)
            return {"error": "unauthorized"}, 401
        return f(user, *args, **kwargs)

    return decorated_function


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
    flashcard_source = FlashcardSource(
        content=content, user_id=user_id, title=completion["title"]
    )
    source_id = insert_flashcard_source(flashcard_source)

    for flashcard in completion["data"]:
        flashcard = Flashcard(
            question=flashcard["question"],
            answer=flashcard["answer"],
            source_id=source_id,
            user_id=user_id,
        )
        insert_flashcard(flashcard)


def hash_password(plain_text_password: str) -> str:
    """
    Generate a bcrypt hash for the given plain-text password and
    return it as a UTF-8 string to store in the database.
    """
    # gensalt() by default uses 12 rounds. Adjust 'rounds' if you want higher cost.
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode("utf-8"), salt)
    return hashed_bytes.decode("utf-8")


def verify_password(plain_text_password: str, hashed_password: str) -> bool:
    """
    Check whether the plain-text password matches the stored bcrypt hash.
    """
    return bcrypt.checkpw(
        plain_text_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


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
@login_required
def cards(user):
    return render_template("cards.html")


@app.get("/")
def index():

    return render_template("index.html")


@app.route("/history")
@login_required
def history(user):
    retrieved_sources = get_flashcard_sources_for_user(user.id)
    return render_template("history.html", history=retrieved_sources)


@app.route("/dashboard")
@login_required
def dashboard(user):
    return render_template("dashboard.html")


@app.route("/practice")
@login_required
def practice(user):
    return render_template("practice.html")


@app.route("/account")
@login_required
def account(user):
    return render_template("account.html", username=user.username)


@app.route("/studyguide")
@login_required
def studyguide(user):
    return render_template("studyguide.html")


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
    return render_template(
        "view_flashcards.html",
        flashcard_set=retrieved_flashcards,
        flashcard_source=retrieved_source,
    )


@app.post("/api/register")
def register():
    if not request.json:
        return jsonify({"error": "Invalid JSON"}), 400

    user_name = request.json.get("username")
    password = request.json.get("password")

    if not user_name or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user = User(username=user_name, password=password)
    validation_errors = user.validate()
    if validation_errors:
        return jsonify({"errors": validation_errors}), 422
    hashed_pw = hash_password(password)
    user = User(username=user_name, password=hashed_pw)
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
    if not request.json:
        return jsonify({"error": "Invalid JSON"}), 400

    user_name = request.json.get("username")
    password = request.json.get("password")

    # if not user_name or not password:
    #     return jsonify({"error": "Missing username or password"}), 400

    user = get_user_by_name(user_name)

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    if not verify_password(password, user.password):
        return jsonify({"error": "Invalid credentials"}), 401
    session["user_id"] = user.id
    return jsonify({"message": "Login successful", "username": user.username}), 200


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


@app.post("/api/change-username")
@api_login_required
def change_username(user):
    if not request.json:
        return jsonify({"error": "Invalid JSON"}), 400

    new_user_name = request.json.get("username")
    user.username = new_user_name
    validation_errors = user.validate()
    if validation_errors:
        return jsonify({"errors": validation_errors}), 422
    update_username(session["user_id"], new_user_name)
    return jsonify({"message": "okay"})


@app.post("/api/change-password")
@api_login_required
def change_password(user):
    if not request.json:
        return jsonify({"error": "Invalid JSON"}), 400

    new_password = request.json.get("password")
    if not new_password:
        return jsonify({"error": "Missing new password"}), 400
    user.password = new_password
    validation_errors = user.validate()
    if validation_errors:
        return jsonify({"errors": validation_errors}), 422
    new_hashed_pw = hash_password(new_password)
    user.password = new_hashed_pw
    update_password(session["user_id"], new_hashed_pw)
    return jsonify({"message": "password updated"}), 200


@app.post("/api/completion")
@api_login_required
def completion(user):
    if not request.json:
        return jsonify({"error": "Invalid JSON"}), 400

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
@api_login_required
def clear_history(user):
    delete_flashcard_sources_for_user(session["user_id"])
    return {"status": "success"}


@app.delete("/api/flashcard-source/<flashcard_source_id>")
@api_login_required
def delete_flashcard_source(user, flashcard_source_id):
    deleted = delete_flashcard_source_by_id(flashcard_source_id, session["user_id"])
    if deleted:
        return {"status": "success"}
    return {"status": "failure"}, 404


if __name__ == "__main__":
    app.run(debug=True)
