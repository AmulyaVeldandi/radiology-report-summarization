import sqlite3
import pandas as pd
import gradio as gr
import requests
from dotenv import load_dotenv
import os

# Load API key from .env
load_dotenv()
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Step 1: Database Setup
def initialize_database():
    conn = sqlite3.connect('radiology_reports.db')
    return conn

# Step 2: RAG Framework - Retrieval
def retrieve_reports(conn, query):
    cursor = conn.cursor()
    cursor.execute("SELECT findings FROM reports WHERE findings LIKE ? LIMIT 5", (f'%{query}%',))
    return [row[0] for row in cursor.fetchall()]

# Step 3: Augment and Generate Summary
def generate_summary(reports, mode='local'):
    combined_text = " ".join(reports)
    
    if mode == 'local':
        payload = {
            "prompt": f"Summarize the following radiology reports concisely: {combined_text}",
            "max_tokens": 150
        }
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        
        if response.status_code == 200:
            return response.json().get("summary", "No summary generated.")
        else:
            return "Error generating summary. Check LM Studio/Ollama setup."
    
    elif mode == 'online':
        api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {"inputs": combined_text, "max_length": 150, "min_length": 50, "do_sample": False}

        response = requests.post(api_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()[0].get("summary_text", "No summary generated.")
        else:
            return "Error generating summary. Check Hugging Face API setup."

# Step 4: Gradio Interface
def query_interface(query, mode):
    conn = initialize_database()
    reports = retrieve_reports(conn, query)
    if reports:
        summary = generate_summary(reports, mode)
        return summary
    else:
        return "No matching reports found."

# Gradio UI
iface = gr.Interface(
    fn=query_interface,
    inputs=[
        gr.Textbox(lines=2, placeholder="Enter your query here..."),
        gr.Radio(choices=["local", "online"], label="Select Summarization Mode", value="local")
    ],
    outputs="text",
    title="Radiology Report Summarization",
    description="Enter keywords to retrieve and summarize relevant radiology reports. Choose between local or online summarization."
)

if __name__ == "__main__":
    iface.launch()
