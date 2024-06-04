import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
import google.generativeai as genai
from htmlTemplates import css, bot_template, user_template
import fitz  # PyMuPDF

load_dotenv()
st.set_page_config(page_title="SmartDoc", layout="wide")
def extract_text_from_pdf(pdf_bytes):
    text = ""
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text
def generate_answer(question, response_placeholder):
    if question and st.session_state.vector_index:
        vector_index = st.session_state.vector_index
        docs = vector_index.get_relevant_documents(question)

        # Generate answer
        prompt_template = """
        Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
        provided context, it should print same message everytime,"The answer is not in the provided context",don't provide the wrong answer\n\n
        Context:\n {context}?\n
        Question: \n{question}\n
        Answer:
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain = load_qa_chain(modelForRes, chain_type="stuff", prompt=prompt)
        response_dict = chain({"input_documents": docs, "question": question}, return_only_outputs=True)
        response = response_dict["output_text"]
        

        if "The answer is not in the provided context" in response or "I cannot answer this question" in response or "provided context does not mention anything" in response:
            responsenew = newmodelWebResponse.generate_content(question)
            updatedres = responsenew._result.candidates[0].content.parts[0].text
            response = "The answer is not in the provided context while this is Web based information:"+ updatedres

        
        # If the response does not contain sufficient information, use Gemini directly
       

        # Update response
        response_placeholder.write(user_template.replace("{{MSG}}", question), unsafe_allow_html=True)
        response_placeholder.write(bot_template.replace("{{MSG}}", response), unsafe_allow_html=True)

        # Add asked question and generated answer to history
        st.session_state.question_history.append((question, response))

# Initialize session state if not present
if 'question_history' not in st.session_state:
    st.session_state.question_history = []

if 'document_processed' not in st.session_state:
    st.session_state.document_processed = False

if 'vector_index' not in st.session_state:
    st.session_state.vector_index = None

if 'upload_status' not in st.session_state:
    st.session_state.upload_status = "No document uploaded yet."

# Main content area

st.markdown("<h1 style='text-align: center; color: white; padding: 10px; background-color: #002147;'>SmartDoc</h1>", unsafe_allow_html=True)
st.markdown("---")

# Create sidebar for key input, file uploader, and question history
with st.sidebar:
    google_api_key = st.text_input("Enter your Google API Key:", type="password", key="google_api_key")
    st.markdown("Don't have a Gemini API key? [Get it here](https://aistudio.google.com/app/apikey)")
    uploaded_file = st.file_uploader("Upload your document (PDF)", type="pdf")

    # Question history expander
    with st.expander("Chat History"):
        for qa_pair in st.session_state.question_history:
            question, answer = qa_pair
            st.write(user_template.replace("{{MSG}}", question), unsafe_allow_html=True)
            st.write(bot_template.replace("{{MSG}}", answer), unsafe_allow_html=True)

if st.session_state.google_api_key:
    # Set Google API key
    genai.configure(api_key=st.session_state.google_api_key)
    st.write(css, unsafe_allow_html=True)
    modelForRes = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.6, google_api_key=st.session_state.google_api_key)
    newmodelWebResponse = genai.GenerativeModel(model_name="gemini-1.5-pro")

    if uploaded_file and not st.session_state.document_processed:
        st.session_state.upload_status = "Uploading document..."
        with st.spinner(st.session_state.upload_status):
            file_content = uploaded_file.read()
            extracted_text = extract_text_from_pdf(file_content)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=200)
            texts = text_splitter.split_text(extracted_text)

            # Create embeddings and vector store
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=st.session_state.google_api_key)
            st.session_state.vector_index = FAISS.from_texts(texts, embeddings).as_retriever()
            st.session_state.document_processed = True
            st.session_state.upload_status = "Document processed successfully!"

# Display the question prompt if the document is ready
if st.session_state.document_processed:
    question_placeholder = st.empty()
    response_placeholder = st.empty()
    question = question_placeholder.text_input("Ask a question", key="question")
    if question:
        generate_answer(question, response_placeholder)
