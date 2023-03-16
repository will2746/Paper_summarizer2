
import streamlit as st
import openai
import PyPDF2
import io
import base64
from streamlit_option_menu import option_menu
import shutil
from pathlib import Path

def extract_text_from_pdf(pdf_file_path):
    # Open the file and read its contents
    # with open(pdf_file_path, "rb") as pdf_file:
    # pdf_contents = pdf_file.read()
    # Create a pdf reader object
    pdf_file = io.BytesIO(pdf_file_path.read())
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    # Initialize an empty string to store the text
    text = ""

    # Iterate through each page of the pdf
    for page in range(len(pdf_reader.pages)):
        # Extract the text from the page
        page_text = pdf_reader.pages[page].extract_text()
        # Add a newline character after each page to retain the paragraph format
        text += page_text + " "
        # Split the text into a list of lines
        lines = text.split("\n")

        # Find the index of the line containing "References"
    index = 0
    for i, line in enumerate(lines):
        if "References" in line:
            index = i
            break

    # Delete all lines after the line containing "References"
    lines = lines[:index + 1]

    # Join the lines back into a single string
    text = "\n".join(lines)

    return text


# Function to process the uploaded file
def create_text(text_content):

    if len(text_content) > 7000*4:
        text1 = text_content[:15000]
        text2 = text_content[-15000:]
        document_text = text1+text2
    else:
        document_text = text_content
    #openai.api_key = st.secrets["API_KEY"]
    openai.api_key = "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"
    prompt = [
        {"role": "system",
         "content": "You are gathering information from an an academic research papaer for a college level student. Include a 2 sentence response to each of the followiung headers: Summary, Findings, Research Gaps, Importance, Methodolgy"},
        {"role": "user", "content": document_text}
    ]

    # Generate completions
    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=prompt,
        max_tokens=500,
        temperature=.5)
    answers_from_gpt = response['choices'][0]['message']['content']
    # st.write(prompt)
    st.write(answers_from_gpt)

    # Return the first completion
    return answers_from_gpt


def chat_with_papers(question_input, document_text):

    if len(document_text) > 7000*4:
        text1= document_text[:13000]
        text2=document_text[-13000:]
        document_text = text1+text2
    # Set the prompt
    prompt = [
        {"role": "system", "content": "You are a chatbot answering questions about a research papaer"},
        {"role": "user",
         "content": f"My question is: {question_input}" + f" Please use the following research paper to help answer the question{document_text}"}
    ]
    openai.api_key = "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"
    # Generate completions
    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=prompt,
        max_tokens=800,
        temperature=.5)

    # Return the first completion
    st.write(f"### {question_input}")

    return response['choices'][0]['message']['content']

def main():
    st.set_page_config(page_title="AI Research Pal", page_icon=":newspaper:", layout="wide")

    with st.sidebar:
        choose = option_menu("App Gallery",
                             ["Upload Paper", "Chat With Paper", "Summarize Paper"],
                             icons=['house', 'person lines fill', 'book'],
                             menu_icon="app-indicator", default_index=0,
                             styles={
                                 "container": {"padding": "5!important", "background-color": "#fafafa"},
                                 "icon": {"color": "orange", "font-size": "25px"},
                                 "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px",
                                              "--hover-color": "#eee"},
                                 "nav-link-selected": {"background-color": "#02ab21"},
                             }
                             )
    if choose == "Upload Paper":
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
        if uploaded_file:
            st.session_state.pdf_data = uploaded_file.read()
    elif choose == "Summarize Paper":
        st.title('Paper Summary')
        if 'pdf_data' in st.session_state:
            document_text = extract_text_from_pdf(io.BytesIO(st.session_state.pdf_data))
            paper_summary = create_text(document_text)
        else:
            st.write("Please upload a paper to begin")
    elif choose == 'Chat With Paper':
        if 'pdf_data' in st.session_state:
            document_text = extract_text_from_pdf(io.BytesIO(st.session_state.pdf_data))
            col1, col2 = st.columns((3, 1))
            with col1:
                st.subheader("PDF Viewer")
                base64_pdf = base64.b64encode(st.session_state.pdf_data).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,' \
                              f'{base64_pdf}" width="900" height="800" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

            with col2:
                st.subheader("Chat")
                chat_history = st.empty()
                chat_list = []

                user_input = st.text_input("Type your message and press Enter")

                if user_input:
                    chat_list.append({"user": user_input})
                    response = chat_with_papers(user_input, document_text)

                    chat_list.append({"bot": response})

                    chat_history.markdown("#### Chat History")
                    for chat in chat_list:
                        if "user" in chat:
                            chat_history.markdown(f"**You:** {chat['user']}")
                        elif "bot" in chat:
                            chat_history.markdown(f"**Bot:** {chat['bot']}")
        else:
            st.write('Please upload a file to begin')


if __name__ == "__main__":
    main()
