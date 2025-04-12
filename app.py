import streamlit as st
import pytesseract
from PIL import Image
import requests
import json
import re
from dotenv import load_dotenv
import os
import io

# Initializing the OCR or pytesserect into the model
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Title
st.title("📄 Invoice Parser with Invoicify")

# Upload image
uploaded_file = st.file_uploader("Upload Invoice Image", type=["png", "jpg", "jpeg"])

# Function to clean empty fields
def clean_empty_fields(data):
    if isinstance(data, dict):
        return {k: clean_empty_fields(v) for k, v in data.items() if v not in ("", [], {}, None)}
    elif isinstance(data, list):
        return [clean_empty_fields(v) for v in data if v not in ("", [], {}, None)]
    return data

if uploaded_file is not None:
    try:
        # Load image and display
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, caption="Uploaded Invoice", use_column_width=True)

        # OCR
        extracted_text = pytesseract.image_to_string(img, config="--psm 6")
        st.subheader("🔍 Extracted Text")
        st.text(extracted_text)

        # Prompt with embedded extracted text
        prompt = f"""
Your name is AnandGPT
You are an AI bot specialized in parsing invoices for a company that processes money transactions between two B2B payments.
The invoice can be in any format (PDF, scanned document, etc.).
Extract all key information and return valid JSON. Do not include empty fields.
Provide a summary about the invoice given in 3-4 lines. 

The OCR-extracted text from the invoice is below:
\"\"\"{extracted_text}\"\"\"

The JSON must follow this format:

```json
{{
  "invoiceNumber": "",
  "invoiceDate": "",
  "dueDate": "",
  "seller": {{
    "name": "",
    "address": "",
    "email": "",
    "phone": ""
  }},
  "buyer": {{
    "name": "",
    "address": "",
    "email": "",
    "phone": ""
  }},
  "items": [
    {{
      "description": "",
      "quantity": 0,
      "unitPrice": 0.0,
      "total": 0.0
    }}
  ],
  "subtotal": 0.0,
  "tax": 0.0,
  "totalAmount": 0.0,
  "paymentStatus": "",
  "notes": ""
}}

**Analyze the parsed data and generate a short professional profile summary** at the end, highlighting the candidate’s expertise, work experience, and skills in 3-4 sentences.**

Here is the extracted invoice text:
{extracted_text}
"""
        load_dotenv()
        # Access your Groq API key
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        # Groq API call
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
                    }

        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }

        with st.spinner("⏳ Analyzing invoice with AnandGPT..."):
            response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            response_text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            json_match = re.search(r'```(?:json)?\n([\s\S]*?)\n```', response_text)

            if json_match:
                parsed_json = json.loads(json_match.group(1))
                cleaned = clean_empty_fields(parsed_json)
                st.subheader("✅ Parsed Invoice JSON")
                st.json(cleaned)
            else:
                st.warning("⚠️ JSON block not found in API response.")
                st.text(response_text)
        else:
            st.error(f"❌ API request failed: {response.status_code}\n{response.text}")

    except Exception as e:
        st.error(f"🚨 Error: {str(e)}")
