from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import shutil
import os

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update this if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_and_process_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save the uploaded PDF
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text with PyMuPDF
    doc = fitz.open(file_path)
    extracted_data = []

    for page_num, page in enumerate(doc):
        page_data = {"page": page_num + 1, "content": []}

        for text_block in page.get_text("dict")["blocks"]:
            if "lines" in text_block:
                for line in text_block["lines"]:
                    for span in line["spans"]:
                        page_data["content"].append({
                            "text": span["text"],
                            "font_size": span["size"],
                            "bold": bool(span["flags"] & 2)
                        })

        extracted_data.append(page_data)

    # Return both filename and processed data
    return {"filename": file.filename, "pages": extracted_data}
