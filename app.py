import os
import streamlit as st
import langchain_google_genai
from langchain_google_genai import GoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from PyPDF2 import PdfReader

# Set page config
st.set_page_config(
    page_title="Rhino AI 🦏",
    page_icon="🦏"
)

# Load environment variables
os.environ["api_key"] = st.secrets["secrets"]["api_key"]

# Define function to extract text from a PDF file
def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        pdf_reader = PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None
    return text

# Define function to generate response using Google Generative AI
@st.cache_data
def generate_google_response(input_text):
    llm = GoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=os.environ["api_key"],
        safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        },
    )

    generated_text = ""
    try:
        for chunk in llm.stream(input_text):
            generated_text += chunk
    except Exception as e:
        st.error(f"Error generating text: {str(e)}")
        return None
    return generated_text

# Define function to check if the input text is a mathematical expression
def is_math_expression(text):
    try:
        eval(text)
        return True
    except:
        return False

# Streamlit app
st.title('Rhino AI 🦏')

# Initialize chat history
chat_history = []


with st.form('my_form'):
        text = st.text_area('Enter text:')
        submitted = st.form_submit_button('Submit')
        if submitted:
            if is_math_expression(text):
                response = str(eval(text))
            else:
                response = generate_google_response(text)
            # Append user input and response to chat history
            chat_history.append(("You", text))
            chat_history.append(("Rhino AI", response))
            # Display chat history
            for role, message in chat_history:
                st.write(f"{role}: {message}")
            st.write('You submitted the form')
    
with st.sidebar:
        if st.button("Clear Chat", use_container_width=True, type="primary"):
            st.session_state.history = []
            st.rerun()


uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
if uploaded_file:
        text = extract_text_from_pdf(uploaded_file)
        if text is not None:
            st.write("Text extracted from PDF:")
            st.write(text)
            st.write("---")
            st.write("Ask a question or provide input related to the text:")
            user_input = st.text_input("Your question or input:")
            if st.button("Submit"):
                if user_input:
                    if "extracted_text" in st.session_state:
                        # If extracted text is available in the session state, use it for generating responses
                        response = generate_google_response(user_input + "\n" + st.session_state["extracted_text"])
                    else:
                        # If extracted text is not available in the session state, use only the user input
                        response = generate_google_response(user_input)
                    # Append user input and AI response to chat history
                    chat_history.append(("You", user_input))
                    chat_history.append(("Rhino AI", response))
                    # Display chat history
                    for role, message in chat_history:
                        st.write(f"{role}: {message}")
                else:
                    st.warning("Please ask a question or provide input.")
            # Store the extracted text in the session state
            st.session_state["extracted_text"] = text