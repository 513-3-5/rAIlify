import sys
import os
import platform
import subprocess
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from draw import draw
from pdf2image import convert_from_path  

from recognition import recognition

rail_pngs = []  
splitted_pdfs = []
annotated_pdfs = []

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

def split_pdf(file_path, num_pages):
    try:
        output_dir = "assets/temp_pdf_output"
        os.makedirs(output_dir, exist_ok=True)
        
        with open(file_path, "rb") as file:
            reader = PdfReader(file)
            num_pages = len(reader.pages)
            
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            for i in range(num_pages):
                writer = PdfWriter()
                writer.add_page(reader.pages[i])
                
                output_pdf_path = os.path.join(output_dir, f"{base_name}_p{i+1}.pdf")
                
                with open(output_pdf_path, "wb") as output_pdf:
                    writer.write(output_pdf)
                    
                print(f"Page {i+1} has been saved at {output_pdf_path}")
                splitted_pdfs.append(output_pdf_path)
    except Exception as e:
        print(f"Error splitting the PDF: {e}")
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
    elif page_count == 1:
        splitted_pdfs.append(file_path)
    elif page_count > 1: 
        print(f"The provided .pdf file has {page_count} pages")
        split_pdf(file_path, page_count) 
    
    return True

def clear_output_directory(output_dir):    
    if os.path.exists(output_dir):
        for file_name in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file_name)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

def convert_pdf_to_png(pdf_path, output_dir="assets/temp_png_output"):
    os.makedirs(output_dir, exist_ok=True)
    try:
        images = convert_from_path(pdf_path)
        for i, image in enumerate(images):
            output_png_path = os.path.join(output_dir, f"{os.path.basename(pdf_path).rsplit('.', 1)[0]}_p{i+1}.png")
            image.save(output_png_path, "PNG")
            rail_pngs.append(output_png_path)
            print(f"Page {i+1} converted to PNG: {output_png_path}")
        return rail_pngs
    except Exception as e:
        print(f"Error converting PDF to PNG: {e}")
        return None                

# Opens a pdf file directly on your standard pdf reader
def open_pdf(file_path):
    try:
        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", file_path])
        elif platform.system() == "Linux":  
            subprocess.run(["xdg-open", file_path])
    except Exception as e:
        print(f"Error opening PDF file: {e}")                

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

    for pdf in splitted_pdfs:
        convert_pdf_to_png(pdf) # Fills List rail_pngs

        c = recognition.Classify()
        # TODO, get images or path
        json = c.classify('recognition/example-network-topology-3.png')

        # TODO: Continue Process 
        #json = "code/visualization/example.json" # TODO change json path
        print(json)

        #annotated_pdfs.append(draw.draw_annotations(pdf, json))

    merger = PdfWriter()

    for an_pdf in annotated_pdfs:
        merger.append(an_pdf)
   
    an_pdf_file_name = f"{file_path.split('.pdf')[0]}_annotated.pdf"
    merger.write(an_pdf_file_name)    
    print(f"Annotated PDF generated: {an_pdf_file_name}")

    clear_output_directory("assets/temp_pdf_output")
    clear_output_directory("assets/temp_png_output")
    
    open_pdf(an_pdf_file_name);
    




    




    

