import fitz
from pathlib import Path

def dump_pdf_text(pdf_path):
    path = Path(pdf_path)
    if not path.exists():
        print(f"File {pdf_path} does not exist.")
        return
    
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    
    with open("pdf_dump.txt", "w") as f:
        f.write(text)
    print("PDF text dumped to pdf_dump.txt")

if __name__ == "__main__":
    import sys
    dump_pdf_text(sys.argv[1])
