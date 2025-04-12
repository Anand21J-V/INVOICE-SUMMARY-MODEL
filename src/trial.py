import streamlit as st
from groq import Groq
import base64
import magic

from groq import Groq

client = Groq(api_key="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")


# Initialize Groq client
#client = Groq()

st.set_page_config(page_title="Image Summary Bot", layout="centered")
st.title("🖼️ Image Summary Chatbot")

uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # Read and encode the image
    image_bytes = uploaded_file.read()
    mime_type = magic.from_buffer(image_bytes, mime=True)
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    image_data_url = f"data:{mime_type};base64,{encoded_image}"

    if st.button("Get Summary"):
        with st.spinner("Generating summary..."):
            completion = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "provide me the summary of the given image"
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
                temperature=1,
                max_completion_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )

            summary = ""
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    summary += content
                    st.write(content)

        st.success("Summary Generated!")
