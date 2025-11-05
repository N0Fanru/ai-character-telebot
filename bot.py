import telebot
import re
import requests
import json
import base64
import os
import random
import difflib

try:
    from prompts import *
except ImportError:
    from bot_prompts import *
    print("WARNING: This will use a promt template. Create your own prompts.py file.")

try:
    from config import *
except ImportError:
    from bot_config import *


TG_CHANNEL_ID = 777000 # constant
adm = ADMIN_ID

bot = telebot.TeleBot(TOKEN_BOT)

# Gets an image and returns the AI ​​description of the image.
def analyze_image(image_data):
    print("Image recognition...")

    base64_image = base64.b64encode(image_data).decode('utf-8')
    image_data_url = f"data:image/jpeg;base64,{base64_image}"

    for n in range(MAX_TRY):
        if n == 0:
            model = MODEL_IM
        else:
            model = MODEL_IM2
        response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}"
        },
        data=json.dumps({
            "model": model,
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
            "model": MODEL,
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
        if not WHITELIST_PRIVATE or message.from_user.id in WHITELIST:
            return True
        else:
            return False
    elif not WHITELIST_CHAT or message.chat.id in WHITE_CHATS: # in chats
        if random.random() < CHANCE_COMMENTS and message.from_user.id == TG_CHANNEL_ID: # comment
            return True
        elif random.random() < CHANCE_REPLY and message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id: # The bot responded to the message
            return True
        elif random.random() < CHANCE_CHAT:
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
            if result is None and ADMIN_DESCRIP_IM:
                send = bot.send_photo(adm, message.photo[-1].file_id, "Enter a description of the image:")
                bot.register_next_step_handler(send, get_im_descript, message, text)
                return
            if result is not None:
                text = f"{text}\n\nAttached image: [{result}]"
        if not text or text.strip() == "":
            bot.reply_to(message, "An empty request was sent.")
        else:
            send_answer(message, text)
            
    elif not NO_WHITELIST_M.strip() == "" and message.chat.type == 'private':
        bot.reply_to(message, NO_WHITELIST_M)

def get_im_descript(message, mes, text):
    text = f"{text}\n\nAttached image: [{message.text}]"
    send_answer(mes, text)

def send_answer(message, text):
    # Additional prompt depending on context
    if message.from_user.id == TG_CHANNEL_ID:
        extra_prompt = prompt_comment
    elif message.chat.type == 'private':
        extra_prompt = prompt_private
    elif message.from_user.id in SPECIAL_IDS:
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