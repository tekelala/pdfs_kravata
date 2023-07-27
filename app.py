import streamlit as st
import PyPDF2
import io

def read_pdf(file):
    pdf = PyPDF2.PdfFileReader(file)
    text = ''
    for page_num in range(pdf.getNumPages()):
        page = pdf.getPage(page_num)
        text += page.extract_text()
    return text

st.title('PDF Reader')

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    text = read_pdf(uploaded_file)
    st.write(text)
