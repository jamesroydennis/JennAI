# First, ensure you have the google-generativeai library installed in your 'aura' Conda environment.
# If you get an error like "ModuleNotFoundError: No module named 'google.generativeai'",
# then uncomment the line below and run it in a new Jupyter cell:
# !pip install google-generativeai

import google.generativeai as genai
import os

# --- Configuration for your API Key ---
# IMPORTANT: Replace "YOUR_API_KEY" with your actual Google Gemini API Key.
# It's highly recommended to use environment variables for API keys in real projects,
# but for initial Jupyter exploration, direct pasting is acceptable for quick testing.
API_KEY = "YOUR_API_KEY" 

# Configure the Gemini API with your API Key
try:
    genai.configure(api_key=API_KEY)
    print("Gemini API configured successfully!")
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    print("Please double-check your API Key.")

# --- Define the Generative Model ---
# We'll use the 'gemini-2.0-flash' model for its speed and cost-effectiveness,
# making it ideal for our interactive experiments.
model = genai.GenerativeModel('gemini-2.0-flash')

# --- Your First Human-Led Prompt! ---
# This is where you direct the AI's power.
# Let's start by exploring the core concept of our project: "vibe coding".
prompt = "Explain the concept of 'vibe coding' in a simple, friendly, and encouraging way, like you're inspiring a fellow engineer. Keep it concise, but convey enthusiasm."

print(f"\n--- Sending your human-crafted prompt to Gemini ---\n'{prompt}'\n")

try:
    # --- Make the API Call to Gemini ---
    # The generate_content method sends our prompt to the model and fetches the response.
    response = model.generate_content(prompt)

    # --- Display Gemini's Response ---
    # The actual generated text content is typically accessed via response.text
    if response.text:
        print("\n--- Aura's Co-Creation (Gemini's Response) ---\n")
        print(response.text)
    else:
        print("\nNo text content received in the response from Gemini.")
        if response.candidates and response.candidates[0].finish_reason:
            print(f"AI Model Finish Reason: {response.candidates[0].finish_reason}")
            print("This might indicate content moderation or safety filters.")
except Exception as e:
    print(f"\nAn error occurred during the API call: {e}")
    print("Possible issues: Incorrect API Key, network problems, or API rate limits.")
    print("Please verify your API Key and internet connection.")