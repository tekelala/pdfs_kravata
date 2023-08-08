import streamlit as st
from PyPDF2 import PdfReader
import re
import pandas as pd
import base64
import os
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

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

df = pd.DataFrame()

for file in uploaded_files:
    text = read_pdf(file)
    info = extract_info(text)
    info_df = pd.DataFrame([info])  # Create a single-row DataFrame
    df = pd.concat([df, info_df], ignore_index=True)

if not df.empty:
    st.table(df)

    # Create a new workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active

    from openpyxl.styles import Font, NamedStyle

    # Set the default font of the workbook
    if "Normal" not in wb.named_styles:
        normal_style = NamedStyle(name="Normal", font=Font(name='Calibri', size=11))
        wb.add_named_style(normal_style)



    # Convert the DataFrame to rows and add them to the worksheet
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)

    # Save the workbook to a file
    wb.save(filename = 'extracted_info.xlsx')

    # Read the .xlsx file as binary for the download link
    with open('extracted_info.xlsx', 'rb') as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="extracted_info.xlsx">Download Excel File</a>'
        st.markdown(href, unsafe_allow_html=True)

    # Delete the temporary .xlsx file
    os.remove('extracted_info.xlsx')
