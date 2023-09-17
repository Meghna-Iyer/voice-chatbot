import openai
from dotenv import load_dotenv
import os
load_dotenv()

def getChatGptResponse(input_text):
    messages = [
                        {"role": "system", "content": "You are a helpful assistant that provides concise answers."},
                        {"role": "user", "content": input_text},
            ]

    openai.api_key=os.environ.get("OPENAI_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=messages
    )

    assistant_reply = response['choices'][0]['message']['content']
    return assistant_reply
