import logging
from telethon import TelegramClient, events, Button
from secret_santa_utils import secret_santa, send_email

# Configure logging
logging.basicConfig(
    filename="secret_santa_bot.log",  # Log file name
    level=logging.INFO,              # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s"  # Log message format
)

# Telegram API Credentials
api_id = "2API_ID"  # Replace with your API ID
api_hash = "API_HASH"  # Replace with your API Hash
bot_token = "TOKEN"  # Replace with your Bot Token
# Initialize the Telegram Bot
bot = TelegramClient('secret_santa_bot', api_id, api_hash).start(bot_token=bot_token)

# State Management
user_state = {}

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    chat_id = event.chat_id
    user_state[chat_id] = {}
    
    logging.info(f"User {chat_id} started the bot.")
    
    await event.respond(
        "Welcome to the Secret Santa Bot!\nWould you like to create a Secret Santa event?",
        buttons=[
            [Button.inline("✅ Yes", b"Yes"), Button.inline("❌ No", b"No")]
        ]
    )

@bot.on(events.CallbackQuery)
async def handle_response(event):
    chat_id = event.chat_id
    data = event.data.decode("utf-8")  # Decode the callback data
    
    logging.info(f"User {chat_id} selected option: {data}")
    
    if data == "Yes":
        user_state[chat_id] = {"participants": []}
        await event.edit("How many participants are in the event?")
    elif data == "No":
        await event.edit("Okay! Let me know if you change your mind. Use /start to begin.")
        user_state.pop(chat_id, None)
    else:
        logging.warning(f"User {chat_id} sent an invalid response: {data}")
        await event.edit("Invalid response. Please use /start to try again.")

@bot.on(events.NewMessage)
async def collect_details(event):
    chat_id = event.chat_id
    
    if chat_id in user_state and "participants" in user_state[chat_id]:
        state = user_state[chat_id]
        
        # Check if we're collecting the number of participants
        if "num_participants" not in state:
            try:
                num = int(event.raw_text)
                state["num_participants"] = num
                logging.info(f"User {chat_id} set number of participants to {num}.")
                await event.respond("Great! Now, please enter the name and email of each participant in the format:\n\n`Name, email@example.com`")
            except ValueError:
                logging.error(f"User {chat_id} entered an invalid number: {event.raw_text}")
                await event.respond("Please enter a valid number.")
        
        # Collect participant details
        elif len(state["participants"]) < state["num_participants"]:
            try:
                name, email = map(str.strip, event.raw_text.split(","))
                state["participants"].append((name, email))
                logging.info(f"User {chat_id} added participant: {name}, {email}")
                
                if len(state["participants"]) == state["num_participants"]:
                    await event.respond("All participants have been added. Sending emails now...")
                    
                    # Logging all participants for traceability
                    participants = {name: email for name, email in state["participants"]}
                    logging.info(f"Participants for chat {chat_id}: {participants}")
                    
                    # Generate Secret Santa matches
                    matches = secret_santa(list(participants.keys()))
                    logging.info(f"Secret Santa matches for chat {chat_id}: {matches}")

                    # Send emails to participants
                    sender_email = "your_email@example.com"
                    sender_password = "your_email_password"  # Use app password or API key
                    for giver, receiver in matches.items():
                        email_sent = send_email(
                            sender_email,
                            sender_password,
                            participants[giver],
                            giver,
                            receiver,
                        )
                        if email_sent:
                            logging.info(f"Email successfully sent to {giver} ({participants[giver]}) with match: {receiver}")
                        else:
                            logging.error(f"Failed to send email to {giver} ({participants[giver]})")
                    
                    await event.respond("All emails have been sent! 🎉")
                    user_state.pop(chat_id, None)
                else:
                    await event.respond(f"Added {name}. Please add the next participant.")
            
            except Exception as e:
                logging.error(f"Error while adding participant for user {chat_id}: {e}")
                await event.respond("Invalid format. Please enter as `Name, email@example.com`.")

# Run the bot
try:
    logging.info("Bot is starting...")
    bot.run_until_disconnected()
except Exception as e:
    logging.critical(f"Bot crashed with error: {e}")

