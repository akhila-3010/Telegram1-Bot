from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import streamlit as st
import os

# Load environment variables
load_dotenv()
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_TRACING_V2"] = "true"

HF_TOKEN = os.getenv("HF_TOKEN")

# Streamlit UI
st.title("Langchain Joke Generator")
st.markdown("Powered by Hugging Face")

topic = st.text_input("Enter a topic for the joke")

# ✅ Correct way to define the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a joke-generating assistent.generate only one joke on the given topic and do not continue the conversation"),
    ("user", "Topic: {topic}")
])

# Define the HuggingFace model endpoint
llm = HuggingFaceEndpoint(
    endpoint_url="https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta",
    huggingfacehub_api_token=HF_TOKEN
)

# Output parser to format the result
output_parser = StrOutputParser()

# Chain the prompt, model, and parser together
chain = prompt | llm | output_parser

# When user inputs a topic
if topic:
    with st.spinner("Generating Joke..."):
        response = chain.invoke({"topic": topic})
        st.success("Joke Generated!")
        st.write(response.strip())
