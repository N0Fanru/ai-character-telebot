import telebot
import re
import requests
import json
import base64
import os
import random
import difflib
from dotenv import load_dotenv

try:
    from promts import *
except ImportError:
    from promts_exaple import *
    print("WARNING: This will use a promt template. Create your own promts.py file.")

load_dotenv()

TG_CHANNEL_ID = 777000 # constant
API_KEY = os.getenv("API_KEY")
TOKEN_BOT = os.getenv("TOKEN")
adm = int(os.getenv("ADMIN_ID")) # user ID to whom error messages are sent

white_list_private = os.getenv("WHITE_LIST_PRIVATE", "false").lower() in ("true", "1", "yes", "on")
white_list = [adm] + json.loads(os.getenv("WHITE_LIST")) # User IDs, in private messages with whom the bot works 
white_list_chat = os.getenv("WHITE_LIST_CHAT", "false").lower() in ("true", "1", "yes", "on")
white_chats = json.loads(os.getenv("CHATS")) # Chat IDs where the bot is active

chance_comments = float(os.getenv("CHANCE_COMMENTS"))
chance_replay = float(os.getenv("CHANCE_REPLY"))
chance_chat = float(os.getenv("CHANCE_CHAT"))

model = os.getenv("MODEL") # AI model for text generation
model_im = os.getenv("MODEL_IM") # AI model for image recognition
MAX_TRY = int(os.getenv("MAX_TRY")) # Maximum number of attempts to send an AI request
special_ids = json.loads(os.getenv("SPECIAL_IDS"))

bot = telebot.TeleBot(TOKEN_BOT)

# Gets an image and returns the AI ​​description of the image.
def analyze_image(image_data):
    print("Image recognition...")

    base64_image = base64.b64encode(image_data).decode('utf-8')
    image_data_url = f"data:image/jpeg;base64,{base64_image}"

    for n in range(MAX_TRY):
        response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}"
        },
        data=json.dumps({
            "model": model_im,
            "messages": [
            {
                "role": "user",
                "content": [
                {
                    "type": "text",
                    "text": prompt_im
                },
                {
                    "type": "image_url",
                    "image_url": {
                    "url": image_data_url
                    }
                }
                ]
            }
            ],
            
        })
        )
        print("Recognition completed.")

        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            if answer is None or answer.strip() == "":
                print("Empty answer, try again...")
            else:
                return response.json()["choices"][0]["message"]["content"]
        elif response.status_code == 429:
            bot.send_message(adm, f"Error while analyzing the photo: {response.status_code}")
            return None
        else:
            print(f"Error: {response.status_code}, try again...")
    
    error = response.status_code if response.status_code != 200 else "Empty answer"
    bot.send_message(adm, f"Error while analyzing the photo: {error}")
    return None



# Sending an AI request
def get_answer(context, text):
    print("Sending request...")
    prompt = prompt_main + context

    for n in range(MAX_TRY):
        response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}"
        },
        data=json.dumps({
            "model": model,
            "messages": [
            {   "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": text
            }
            ]
        })
        )
        print("Request sent.")

        print(response.status_code)
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            if answer is None or answer.strip() == "":
                print("Empty answer, try again...")
            else:
                return answer
        else:
            bot.send_message(adm, f"Error sending AI request: {response.status_code}")
            return False
    
    error = response.status_code if response.status_code != 200 else "Empty answer"
    bot.send_message(adm, f"Error sending AI request: {error}")


# Removes duplicate text (a problem with some AI models)
def remove_duplicate_text(text, similarity_threshold=0.9):
    lines = text.strip().split('\n')
    if len(lines) <= 1:
        return text
    
    half = len(lines) // 2
    first_half = lines[:half]
    second_half = lines[half:]
    
    similarity = difflib.SequenceMatcher(None, first_half, second_half).ratio()
    
    if similarity >= similarity_threshold:
        return '\n'.join(first_half)
    else:
        return text


# checks if the bot can respond
def can_answer(message):
    if message.chat.type == 'private': # in private messages
        if not white_list_private or message.from_user.id in white_list:
            return True
        else:
            return False
    elif not white_list_chat or message.chat.id in white_chats: # in chats
        if random.random() < chance_comments and message.from_user.id == TG_CHANNEL_ID: # comment
            return True
        elif random.random() < chance_replay and message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id: # The bot responded to the message
            return True
        elif random.random() < chance_chat:
            return True
        else:
            return False
    else:
        return False


@bot.message_handler(content_types=['text', 'photo'])
def echo_message(message):
    if can_answer(message):
        if message.content_type == "text":
            text = message.text
        elif message.caption is not None:
            text = message.caption
        else:
            text = ""
        
        # If there is a photo, it is recognized and a description is added to the text.
        if message.content_type == "photo":
            file_info = bot.get_file(message.photo[-1].file_id)
            file = bot.download_file(file_info.file_path)
            result = analyze_image(file)
            if result is not None:
                text = f"{text}\n\nAttached image: [{result}]"
        if not text or text.strip() == "":
            bot.reply_to(message, "An empty request was sent.")
        else:
            # Additional prompt depending on context
            if message.from_user.id == TG_CHANNEL_ID:
                extra_prompt = prompt_comment
            elif message.chat.type == 'private':
                extra_prompt = prompt_private
            elif message.from_user.id in special_ids:
                extra_prompt = prompt_special
            else:
                extra_prompt = prompt_chat

            answer = get_answer(extra_prompt, text)
            if answer:
                answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL)
                answer = remove_duplicate_text(answer)
                print("Message sends.")
                bot.reply_to(message, answer)

bot.infinity_polling(none_stop=True)