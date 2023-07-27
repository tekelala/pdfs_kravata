import streamlit as st
from PyPDF2 import PdfReader
import re
import pandas as pd
import base64

def read_pdf(file):
    pdf = PdfReader(file)
    text = ''
    for page in pdf.pages:
        text += page.extract_text()
    return text

def extract_info(text):
    info_dict = {}
    match = re.search(r"Razón social:\s*(.*?)\s*Nit", text, re.IGNORECASE)
    info_dict["Razón Social"] = match.group(1).strip() if match else "Not found"
    match = re.search(r"Nit:\s*(.*?)\s*Administración", text, re.IGNORECASE)
    info_dict["Nit"] = match.group(1).strip() if match else "Not found"
    match = re.search(r"Matrícula No.\s*(.*?)\s*Fecha de matrícula:", text, re.IGNORECASE)
    info_dict["Num Matricula"] = match.group(1).strip() if match else "Not found"
    match = re.search(r"Dirección del domicilio principal:\s*(.*?)\s*Municipio:", text, re.IGNORECASE)
    info_dict["Dirección"] = match.group(1).strip() if match else "Not found"
    match = re.search(r"Municipio:\s*(.*?)\s*Correo electrónico:", text, re.IGNORECASE)
    info_dict["Municipio"] = match.group(1).strip() if match else "Not found"
    match = re.search(r"Correo electrónico:\s*(.*?)\s*Teléfono comercial 1:", text, re.IGNORECASE)
    info_dict["Email"] = match.group(1).strip() if match else "Not found"
    match = re.search(r"Teléfono comercial 1:\s*(.*?)\s*Teléfono comercial 2:", text, re.IGNORECASE)
    info_dict["Teléfono"] = match.group(1).strip() if match else "Not found"
    match = re.search(r"OBJETO SOCIAL\s*(.*?)\s*CAPITAL", text, re.IGNORECASE | re.DOTALL)
    objeto_social = match.group(1).strip() if match else "Not found"
    unwanted_text_pattern = r"Página 2.*-{32}"
    objeto_social = re.sub(unwanted_text_pattern, "", objeto_social, flags=re.IGNORECASE | re.DOTALL)
    info_dict["Objeto Social"] = objeto_social
    return info_dict

st.title('PDF Reader')

uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

df_info = pd.DataFrame()
df_all_text = pd.DataFrame()

for file in uploaded_files:
    text = read_pdf(file)
    info = extract_info(text)
    info_df = pd.DataFrame([info])  # Create a single-row DataFrame
    df_info = pd.concat([df_info, info_df], ignore_index=True)

    # Add the raw text to the all_text dataframe
    all_text_df = pd.DataFrame({'All Text': [text]})
    df_all_text = pd.concat([df_all_text, all_text_df], ignore_index=True)

if not df_info.empty:
    st.table(df_info)

    # Download link for the table displayed
    csv = df_info.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="extracted_info.csv">Download Extracted Info CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)

if not df_all_text.empty:
    # Creating CSV with all the text extracted from the PDFs
    csv_all = df_all_text.to_csv(index=False)
    b64_all = base64.b64encode(csv_all.encode()).decode()  
    href_all = f'<a href="data:file/csv;base64,{b64_all}" download="all_text.csv">Download All Text CSV File</a>'
    st.markdown(href_all, unsafe_allow_html=True)
