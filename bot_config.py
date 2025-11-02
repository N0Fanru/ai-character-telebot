# API Keys
API_KEY="your_openrouter_api_key"
TOKEN_BOT="your_bot_token"

# user ID to whom error messages are sent
ADMIN_ID = 123456789

# User IDs to which the bot will react "specially" in chat
SPECIAL_IDS=[]

# Maximum number of attempts to send an AI request
MAX_TRY=2

# AI model for text generation
MODEL="tngtech/deepseek-r1t-chimera:free"

# AI model for image recognition
MODEL_IM="mistralai/mistral-small-3.2-24b-instruct:free"

# Whitelist config 
WHITELIST_PRIVATE=True # Is whitelisting enabled for private messages
WHITELIST=[ADMIN_ID, 123456789] # User IDs in the whitelist
WHITELIST_CHAT=True # Is whitelisting enabled for chat
WHITE_CHATS=[-1234567890123, -3210987654321] # Chat IDs in the whitelist

# Chance of response, a number from 0 to 1 (0 - will never respond, 1 - always responds)
CHANCE_COMMENTS=1 # a chance to leave a comment under the post
CHANCE_REPLY=0.7 # chance to reply if the user replied to the bot's message
CHANCE_CHAT=0.3 # a chance to reply to a random message in chat

# Maximum number of attempts to send an AI request
MAX_TRY=2