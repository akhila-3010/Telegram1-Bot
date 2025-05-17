import os
import re
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters, MessageHandler
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables from .env
load_dotenv()

# Retrieve and set environment variables safely
langchain_key = os.getenv("LANGCHAIN_API_KEY")
langchain_project = os.getenv("LANGCHAIN_PROJECT")
groq_api_key = os.getenv("GROQ_API_KEY")
telegram_token = os.getenv("TELEGRAM_TOKEN")

if langchain_key:
    os.environ["LANGCHAIN_API_KEY"] = langchain_key
else:
    print("Warning: LANGCHAIN_API_KEY not found in environment.")

if langchain_project:
    os.environ["LANGCHAIN_PROJECT"] = langchain_project
else:
    print("Warning: LANGCHAIN_PROJECT not found in environment.")

os.environ["LANGCHAIN_TRACING_V2"] = "true"

# Joke Generator Chain
def setup_llm_chain(topic="technology"):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a joking AI. Give only one joke about the given topic."),
        ("user", f"Generate a joke about {topic}.")
    ])

    llm = ChatGroq(
        model="Gemma2-9b-it",  # Make sure this model name is valid
        groq_api_key=groq_api_key
    )

    return prompt | llm | StrOutputParser()

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, I'm a joking AI. Mention me with a topic, e.g. '@Binary_Jokes_Bot python'.")

# /help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a message like '@Binary_Jokes_Bot anime' to get a joke about anime.")

# Generate joke response
async def generate_joke(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    await update.message.reply_text(f"Generating a joke about '{topic}'...")
    try:
        joke = setup_llm_chain(topic).invoke({}).strip()
        await update.message.reply_text(joke)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Handle user messages mentioning the bot
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    bot_username = context.bot.username

    match = re.search(rf"@{re.escape(bot_username)}\s+(.+)", msg)
    if match:
        topic = match.group(1).strip()
        if topic:
            await generate_joke(update, context, topic)
        else:
            await update.message.reply_text("Please provide a topic after mentioning me.")
    else:
        await update.message.reply_text("Please mention me with a topic, like '@Binary_Jokes_Bot cats'.")

# Bot main entry point
def main():
    if not telegram_token:
        raise ValueError("Missing TELEGRAM_TOKEN in environment")

    app = Application.builder().token(telegram_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
