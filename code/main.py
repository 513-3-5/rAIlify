import sys
import os
from PyPDF2 import PdfReader
from PIL import Image


def is_pdf(file_path):
    return file_path.lower().endswith(".pdf")

def is_tiff(file_path):
    return file_path.lower().endswith((".tif", ".tiff"))

def count_pages_in_pdf(file_path):
    try:
        with open(file_path, "rb") as file: # "rb" = read binary
            reader = PdfReader(file)
            return len(reader.pages)
    except Exception as e:
        print(f"Error reading from file: {e}")
        return None
    
def convert_tiff_to_pdf(file_path):
    output_pdf_path = file_path.rsplit(".", 1)[0] + ".pdf"
    try:
        # Öffne das TIFF-Bild
        with Image.open(file_path) as img:
            img = img.convert("RGB")
            img.save(output_pdf_path, "PDF")
            print(f"Info: File successfully saved as PDF: {output_pdf_path}")
            return output_pdf_path
    except Exception as e:
        print(f"Error converting the .tif file to a PDF: {e}")
        sys.exit(1)    
    
def is_valid_pdf(file_path):
    if not os.path.isfile(file_path):
        print("Error: The provided file doesn't exist.")
        return False
    
    if is_tiff(file_path):
        file_path = convert_tiff_to_pdf(file_path)
        
    if not is_pdf(file_path):
        print("Error: The provided file is not a .pdf file.")
        return False

    page_count = count_pages_in_pdf(file_path)
    if page_count is None:
        print("Error: The provided .pdf file has no pages.")
        return False
    elif page_count > 1: # TODO: Check if some files may have multiple plans or if they always have a single railsystem.
        print(f"The provided .pdf file has {page_count} pages") 
    

    print("Valid pdf file")
    return True


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Error: Please provide a .pdf or .tif file.")
        sys.exit(1)          

    if len(sys.argv) < 2:  
        print("Please only provide a single .pdf or .tif file.")
        sys.exit(1)

    file_path = sys.argv[1]

    if not is_valid_pdf(file_path):
        sys.exit(1)




    

