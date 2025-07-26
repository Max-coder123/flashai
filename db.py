import re
import sqlite3
import string
import uuid
from datetime import datetime


class User:
    def __init__(
        self, id=None, username=None, password=None, created_at=None, updated_at=None
    ):
        self.id = id or str(uuid.uuid4())
        self.username = username
        self.password = password
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or self.created_at

    @staticmethod
    def from_row(row):
        return User(
            id=row["id"],
            username=row["username"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            password=row["password"],
        )

    def validate(self):
        errors = []
        pwd = self.password
        user = self.username

        # Length
        if len(pwd) < 8:
            errors.append("Password must be at least 8 characters long.")
        if len(pwd) > 15:
            errors.append("Password must be shorter than 15 characters.")
        if len(user) < 4:
            errors.append("Username must be at least 4 characters")
        if len(user) > 15:
            errors.append("Username must be shorter than 15 characters")

        # Character‐type checks
        if not re.search(r"[A-Z]", pwd):
            errors.append("Password must include at least one uppercase letter.")
        if not re.search(r"[a-z]", pwd):
            errors.append("Password must include at least one lowercase letter.")
        if not re.search(r"\d", pwd):
            errors.append("Password must include at least one number.")
        if not any(ch in string.punctuation for ch in pwd):
            errors.append("Password must include at least one symbol (e.g. !@#$%^&*).")

        return errors


class FlashcardSource:
    def __init__(
        self,
        id=None,
        content=None,
        title=None,
        user_id=None,
        created_at=None,
        updated_at=None,
    ):
        self.id = id or str(uuid.uuid4())
        self.content = content
        self.title = title
        self.user_id = user_id
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or self.created_at

    @staticmethod
    def from_row(row):
        return FlashcardSource(
            id=row["id"],
            content=row["content"],
            title=row["title"],
            user_id=row["user_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


class Flashcard:
    def __init__(
        self,
        id=None,
        question=None,
        answer=None,
        explanation=None,
        source_id=None,
        user_id=None,
        created_at=None,
        updated_at=None,
    ):
        self.id = id or str(uuid.uuid4())
        self.question = question
        self.answer = answer
        self.explanation = explanation
        self.source_id = source_id
        self.user_id = user_id
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or self.created_at

    @staticmethod
    def from_row(row):
        return Flashcard(
            id=row["id"],
            question=row["question"],
            answer=row["answer"],
            explanation=row["explanation"],
            source_id=row["source_id"],
            user_id=row["user_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


conn = sqlite3.connect("flashai.db", check_same_thread=False)
conn.row_factory = sqlite3.Row

cursor = conn.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS user (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    created_at TEXT,
    updated_at TEXT
)
"""
)


cursor.execute(
    """
CREATE TABLE IF NOT EXISTS flashcard_source (
    id TEXT PRIMARY KEY,
    content TEXT,
    title TEXT,
    user_id TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (user_id) REFERENCES user (id)
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS flashcard (
    id TEXT PRIMARY KEY,
    question TEXT,
    answer TEXT,
    explanation TEXT,
    source_id TEXT,
    user_id TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (source_id) REFERENCES flashcard_source (id),
    FOREIGN KEY (user_id) REFERENCES user (id)
)
"""
)


def insert_user(user: User):
    cursor.execute(
        """
        INSERT INTO user (id, username, password, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    """,
        (user.id, user.username, user.password, user.created_at, user.updated_at),
    )
    conn.commit()
    return user.id


def insert_flashcard_source(flashcard_source: FlashcardSource):
    cursor.execute(
        """
        INSERT INTO flashcard_source (id, content, title, user_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (
            flashcard_source.id,
            flashcard_source.content,
            flashcard_source.title,
            flashcard_source.user_id,
            flashcard_source.created_at,
            flashcard_source.updated_at,
        ),
    )
    conn.commit()
    return flashcard_source.id


def insert_flashcard(flashcard: Flashcard):
    cursor.execute(
        """
        INSERT INTO flashcard (id, question, answer, explanation, source_id, user_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            flashcard.id,
            flashcard.question,
            flashcard.answer,
            flashcard.explanation,
            flashcard.source_id,
            flashcard.user_id,
            flashcard.created_at,
            flashcard.updated_at,
        ),
    )
    conn.commit()


def get_user(user_id):
    cursor.execute("SELECT * FROM user WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    return User.from_row(row) if row else None


def update_username(user_id, new_username):
    cursor.execute("UPDATE user SET username = ? WHERE id = ?", (new_username, user_id))
    conn.commit()


def update_password(user_id, new_password):
    cursor.execute("UPDATE user SET password = ? WHERE id = ?", (new_password, user_id))
    conn.commit()


def get_user_by_name(username):
    cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
    row = cursor.fetchone()
    return User.from_row(row) if row else None


def get_flashcard_source(source_id):
    cursor.execute("SELECT * FROM flashcard_source WHERE id = ?", (source_id,))
    row = cursor.fetchone()
    return FlashcardSource.from_row(row) if row else None


def get_flashcard_sources_for_user(user_id):
    cursor.execute("SELECT * FROM flashcard_source WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    return [FlashcardSource.from_row(row) for row in rows]

def get_flashcards_for_source(source_id):
    cursor.execute("SELECT * FROM flashcard WHERE source_id = ?", (source_id,))
    rows = cursor.fetchall()
    return [Flashcard.from_row(row) for row in rows]


def delete_flashcard_sources_for_user(user_id):
    cursor.execute("DELETE FROM flashcard WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM flashcard_source WHERE user_id = ?", (user_id,))
    conn.commit()


def delete_flashcard_source_by_id(flashcard_source_id, user_id):
    flashcard_deleted = cursor.execute(
        "DELETE FROM flashcard WHERE source_id = ? AND user_id = ?",
        (flashcard_source_id, user_id),
    ).rowcount
    source_deleted = cursor.execute(
        "DELETE FROM flashcard_source WHERE id = ? AND user_id = ?",
        (flashcard_source_id, user_id),
    ).rowcount
    conn.commit()
    return flashcard_deleted > 0 or source_deleted > 0


# user = User(username="john_doe")
# user_id = insert_user(user)

# flashcard_source = FlashcardSource(
#     content="Spurious Correlation: when data appears to be related, but isn’t\r\n"
#             "ie: a cow is always in a green background, but when it’s in a different background, AI assumes it’s not a cow.\r\n",
#     user_id=user_id
# )

# source_id = insert_flashcard_source(flashcard_source)

# flashcard1 = Flashcard(
#     question="What is spurious correlation?",
#     answer="Spurious correlation refers to a situation where data appears to be related but is not actually connected.",
#     explanation="In the context of the provided text, it illustrates this concept with the example of a cow that is always seen against a green background. The AI mistakenly assumes that the cow is not a cow if it appears in a different background.",
#     source_id=source_id,
#     user_id=user_id
# )

# flashcard2 = Flashcard(
#     question="What example is given to illustrate spurious correlation?",
#     answer="The example given is a cow that is always in a green background.",
#     explanation="The text explains that because the AI has only seen the cow in a green background, it may incorrectly conclude that an object not in that background is not a cow, demonstrating how spurious correlations can lead to incorrect assumptions.",
#     source_id=source_id,
#     user_id=user_id
# )

# insert_flashcard(flashcard1)
# insert_flashcard(flashcard2)


def list_all_users():
    cursor.execute("SELECT * FROM user")
    rows = cursor.fetchall()
    return [User.from_row(row) for row in rows]


if __name__ == "main":
    # Example usage
    all_users = list_all_users()
    for user in all_users:
        print(
            f"ID: {user.id}, Username: {user.username}, Created At: {user.created_at}, Updated At: {user.updated_at}"
        )
    user_id = "1b27d88b-73f8-48b4-9132-c447146ca172"

    retrieved_user = get_user(user_id)
    retrieved_sources = get_flashcard_sources_for_user(user_id)
    source_id = retrieved_sources[0].id

    print(retrieved_sources[0].content)
    print(retrieved_user)

    retrieved_flashcards = get_flashcards_for_source(source_id)
    print(retrieved_flashcards)

    for flashcard in retrieved_flashcards:
        print(flashcard.question)

    conn.close()

# ID: 40e7617c-d695-4433-addf-de57e1f62a5e, Username: max, Created At: chen, Updated
# At: 2025-02-22T10:22:41.471295
# ID: a992461d-438f-4eab-a76d-cf72d3929317, Username: john, Created At: doe, Updated
# At: 2025-02-22T10:42:08.250578
