# AI Character Telegram Bot

[![eng](https://img.shields.io/badge/lang-en-en)](https://github.com/N0Fanru/ai-character-telebot/blob/master/README.md)
[![rus](https://img.shields.io/badge/lang-ru-ru?color=DCDCDC)](https://github.com/N0Fanru/ai-character-telebot/blob/master/README-ru.md)

A Telegram bot with AI integration (via OpenRouter) for generating text responses in the persona of any character.

## ✨ Features:
* Generating meaningful responses according to the character's personality defined in your prompt
* Image recognition
* Context understanding (private messages, comments, group chats, different reactions to specific users in chats)
* Configurable response frequency/chance in different contexts
* Whitelists for security and request economy

## ⚙️ Installation and Setup

**Note:** It's recommended to run the bot on hosting, as any Telegram bot requires continuously running code for constant operation.

1. Prerequisites
   - Python 3.8+
   - Your Telegram bot token ([Where to get](https://t.me/BotFather))
   - [OpenRouter API key](https://openrouter.ai/settings/keys) (Sign up on the website -> Create API Key -> Copy)

2. Clone repository
   <br>`git clone https://github.com/N0Fanru/ai-character-telebot`
   <br>*or*
   <br>download as ZIP file and extract

3. Install dependencies
   <br>In command line: `pip install -r requirements.txt`

4. Configuration setup
   <br>Modify the contents of the bot_config.py file to suit your needs following the comments in the file.
   <br>*Note: You can find user or group IDs using various Telegram bots (e.g., Get Any ID)*

5. Create prompts
   <br>Rename prompts_exaple.py file to prompts.py and modify its content according to your needs.
   <br>*Note: Experiment with prompts! In the main prompt, you can define everything you consider necessary. It's recommended to primarily include examples of the character's messages.*

6. Run the bot
   <br>`python bot.py`

## 📋 Usage
- For private messages: make sure you're in the whitelist or the whitelist is disabled. Send a message to the bot.
- For comments/messages in chats: make sure the chat is in the whitelist or the whitelist is disabled. Ensure the bot's response chance is set correctly. Write a post or message in the chat.

## About AI
The project uses free AI models that worked best in **my** case. You can choose any other AI model on [OpenRouter](https://openrouter.ai/models) and change to it in the .env file.

## ❗ Possible Issues:
- Code 429 - [request limits](https://openrouter.ai/docs/api-reference/limits). (For free models this is 20 requests per minute, 50 requests per day)
- [About other errors](https://openrouter.ai/docs/api-reference/errors)

## 🔮 Planned Future Features:
1. Audio recognition
2. Analysis of certain files
3. Context memory with database

#### If you liked the project, don't forget to give it a ⭐ on GitHub!
