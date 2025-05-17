import os
import re
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters, MessageHandler
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load .env
load_dotenv()

# Set env variables
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
groq_api_key = os.getenv("GROQ_API_KEY")

# Joke Generator Chain
def setup_llm_chain(topic="technology"):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a joking AI. Give only one joke about the given topic."),
        ("user", f"Generate a joke about {topic}.")
    ])

    llm = ChatGroq(
        model="Gemma2-9b-it",  # Ensure this matches the correct model name
        groq_api_key=groq_api_key
    )

    return prompt | llm | StrOutputParser()

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, I'm a joking AI. Mention me with a topic, e.g. '@Binary_Jokes_Bot python'.")

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a message like '@Binary_Jokes_Bot anime' to get a joke about anime.")

# Generate a joke
async def generate_joke(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    await update.message.reply_text(f"Generating a joke about '{topic}'...")
    try:
        joke = setup_llm_chain(topic).invoke({}).strip()
        await update.message.reply_text(joke)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Handle user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    bot_username = context.bot.username

    # Correct use of regex with f-string
    match = re.search(rf"@{re.escape(bot_username)}\s+(.+)", msg)
    if match:
        topic = match.group(1).strip()
        if topic:
            await generate_joke(update, context, topic)
        else:
            await update.message.reply_text("Please provide a topic after mentioning me.")
    else:
        await update.message.reply_text("Please mention me with a topic, like '@Binary_Jokes_Bot cats'.")

# Main runner
def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("Missing TELEGRAM_TOKEN in .env")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
