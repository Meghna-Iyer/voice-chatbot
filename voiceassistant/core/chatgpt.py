import openai
from .models import Message
from core.enums import MessageUserType, ChatGPTRoles
from dotenv import load_dotenv
import os
import concurrent.futures
load_dotenv()

def getChatGptResponse(input_text, use_chat_history, user_id, conversation_id):
    messages = [{"role": "system", "content": "You are a helpful assistant that provides concise answers."},]
    if use_chat_history:
        db_messages = Message.objects.filter(user_id=user_id, conversation_id=conversation_id).values('content', 'message_user_type').order_by('-created')[:10][::-1]
        for msg in db_messages:
            role = ChatGPTRoles.ASSISTANT.value if msg['message_user_type'] == MessageUserType.BOT.value else ChatGPTRoles.USER.value
            messages.append({"role": role, "content": msg['content']},)
    else:
        messages.append({"role": "user", "content": input_text})

    openai.api_key=os.environ.get("OPENAI_KEY")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(openai.ChatCompletion.create, model="gpt-3.5-turbo", messages=messages)
        try:
            response = future.result(timeout=20)
            assistant_reply = response['choices'][0]['message']['content']
            return assistant_reply
        except concurrent.futures.TimeoutError:
            raise TimeoutError("Timeout occurred while waiting for the response.")

def getConversationTitle(input_text):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates one appropriate conversation title."},
            {"role": "user", "content": input_text},
        ]

        openai.api_key = os.environ.get("OPENAI_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=messages
        )

        title = response['choices'][0]['message']['content'].strip('"')
        return title

    except Exception as e:
        # Log the error or handle it in a way that suits your application
        print(f"Error: {e}")

        # Return a default title or handle the error as needed
        return "Conversation With FRIDAY"
