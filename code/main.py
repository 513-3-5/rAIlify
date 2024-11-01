import sys
import os
import PyPDF2



def is_pdf(file_path):
    return file_path.lower().endswith(".pdf")

def count_pages_in_pdf(file_path):
    try:
        with open(file_path, "rb") as file: # "rb" = read binary
            reader = PyPDF2.PdfReader(file)
            return len(reader.pages)
    except Exception as e:
        print(f"Error reading from file: {e}")
        return None
    
def is_valid_pdf(pdf_path):
    if not os.path.isfile(pdf_path):
        print("Error: The provided file doesn't exist.")
        return False

    if not is_pdf(pdf_path):
        print("Error: The provided file is not a .pdf file.")
        return False

    page_count = count_pages_in_pdf(pdf_path)
    if page_count is None:
        print("Error: The provided .pdf file has no pages.")
        return False
    # if page_count > 1: # TODO: Check if some files may have multiple plans or if they always have a single railsystem.
    #     print(f"Error: The provided .pdf file has {page_count} pages instead of one.") 
    

    print("Valid pdf file")
    return True


if __name__ == "__main__":
    # if len(sys.argv) < 2: # TODO: probably multiple pdf files possible?
    #    print("Please only provide a single .pdf file.")
    #    sys.exit(1)

    pdf_path = sys.argv[1]

    if not is_valid_pdf(pdf_path):
        sys.exit(1)




    

