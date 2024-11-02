import json
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import AnnotationBuilder

def ab_rect(x, y, size = 10, color = "ff0000"):
    return AnnotationBuilder.rectangle(
        rect = (x - size, y - size, x + size, y + size),
        interiour_color = color,
    )

def ab_text(x, y, size = 10, text = "Hello World"): 
    return AnnotationBuilder.text(
        rect = (x - size, y - size, x + size, y + size),
        text = text,
    )


class Node:
    def __init__(self, uuid, element, name, x, y):
        self.uuid = uuid
        self.element = element
        self.name = name
        self.x = x
        self.y = y


def draw_annotations(input_pdf_path, json_path):
    print(f"input: {input_pdf_path}")
    reader = PdfReader(input_pdf_path)
    page = reader.pages[0]
    writer = PdfWriter()
    writer.add_page(page)
    with open(json_path, 'r') as f:
        parsed_data = json.load(f)

    nodes = []

    for item in parsed_data:
        if item["type"] == "node":
            nodes.append(
                Node(
                    item["uuid"],
                    item["element"],
                    item["name"],
                    item["originX"],
                    item["originY"]
                )
            )

    print(f"Found {len(nodes)} nodes")

    for n in nodes:
        if n.x == None or n.y == None:
            print("Error: no coordinates found")
            continue

        print(f"NODE:")
        print(f"\tuuid: {n.uuid}")
        print(f"\telement: {n.element}")
        print(f"\tx: {n.x}")
        print(f"\ty: {n.y}")
        text = f"UUID: {n.uuid}\nElement: {n.element}"
        size = len(text.split('\n')[0])
        writer.add_annotation(page_number=0, annotation = ab_text(n.x, n.y, size, text))
        writer.add_annotation(page_number=0, annotation = ab_rect(n.x, n.y, size = 2))

    # Write the annotated file to disk
    
    file_name = f"{input_pdf_path.split('.pdf')[0]}_annotated.pdf"
    print(f"annotated file_name: {file_name}")
    with open(file_name, "wb") as fp:
        writer.write(fp)

    return file_name    

