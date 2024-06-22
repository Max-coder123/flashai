import json
import os
import requests
from dotenv import load_dotenv
from pyfiglet import Figlet

load_dotenv()  # take environment variables from .env.


f = Figlet(font="varsity")
fonts = f.getFonts()
print(f.renderText("Max's Chat"))


messages = []
while True:
    question = input("> ")
    messages.append({"role": "user", "content": question})
    headers = {"Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}"}
    url = "https://api.openai.com/v1/chat/completions"
    data = {
        "model": "gpt-4-turbo",
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 1000,
        "stream": True,  # Enable streaming
    }

    response = requests.post(url, headers=headers, json=data, stream=True)
    response.raise_for_status()

    ai_response = ""
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode("utf-8")
            if decoded_line.startswith("data: "):
                try:
                    json_data = json.loads(decoded_line[len("data: ") :])
                    content = json_data["choices"][0]["delta"].get("content", "")
                    ai_response += content
                    print(content, end="", flush=True)
                except json.JSONDecodeError:
                    continue
    print()  # To ensure the final output ends with a newline
    messages.append({"role": "assistant", "content": ai_response})