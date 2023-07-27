import streamlit as st
from PyPDF2 import PdfReader
import re

def read_pdf(file):
    pdf = PdfReader(file)
    text = ''
    for page in pdf.pages:
        text += page.extract_text()
    return text

def extract_razon_social(text):
    match = re.search(r"Razón social:\s*(.*?)\s*Nit", text, re.IGNORECASE)
    razon_social = match.group(1).strip() if match else "Not found"
    return razon_social

st.title('PDF Reader')

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    text = read_pdf(uploaded_file)
    razon_social = extract_razon_social(text)
    st.write(razon_social)
