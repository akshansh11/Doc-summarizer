# -*- coding: utf-8 -*-
"""text summarizer.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1IXtQW5boA41tyYI3-TN_VcANikAU6LyW
"""



import streamlit as st
import fitz  # PyMuPDF
from transformers import pipeline
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Load the summarization pipeline
summarizer = pipeline("summarization")

def summarize_text(text):
    # Summarize the text with a maximum length of 150 words
    summary = summarizer(text, max_length=150, min_length=30, do_sample=False)
    return summary[0]['summary_text']

def extract_text_from_pdf(file):
    # Open the PDF file from the uploaded file
    document = fitz.open(stream=BytesIO(file.read()), filetype="pdf")
    page_summaries = []

    for page_num in range(len(document)):
        # Extract text from the page
        page = document.load_page(page_num)
        text = page.get_text()

        if text:
            # Summarize the extracted text
            summary = summarize_text(text)
            page_summaries.append({
                "page_number": page_num + 1,
                "summary": summary
            })

    return page_summaries

def save_summaries_to_pdf(summaries, output_path):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    for summary in summaries:
        c.drawString(100, 750, f"Page {summary['page_number']} Summary:")
        text = summary['summary']
        text_lines = text.split('\n')

        y = 730
        for line in text_lines:
            c.drawString(100, y, line)
            y -= 20
            if y < 50:
                c.showPage()
                y = 750

        c.showPage()

    c.save()

    buffer.seek(0)
    return buffer

# Streamlit app layout
st.title("PDF Summarizer")
st.write("Upload a PDF file to summarize its content page by page.")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    st.write("Summarizing the document...")
    summaries = extract_text_from_pdf(uploaded_file)

    for summary in summaries:
        st.subheader(f"Page {summary['page_number']} Summary")
        st.write(summary['summary'])
        st.write("\n" + "="*50 + "\n")

    if st.button("Download Summaries as PDF"):
        summarized_pdf = save_summaries_to_pdf(summaries, "summarized_document.pdf")
        st.download_button(
            label="Download PDF",
            data=summarized_pdf,
            file_name="summarized_document.pdf",
            mime="application/pdf"
        )
