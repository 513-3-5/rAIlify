import sys
import os
import json
import argparse
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import AnnotationBuilder

parser = argparse.ArgumentParser(description="Parse JSON data from file.")
parser.add_argument("json_file", help="Path to the input JSON file")
parser.add_argument("pdf_file", help="Path to the corresponding input PDF file")
args = parser.parse_args()

reader = PdfReader(args.pdf_file)
page = reader.pages[0]
writer = PdfWriter()
writer.add_page(page)

with open(args.json_file, 'r') as f:
    parsed_data = json.load(f)

nodes = []


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
with open(f"{args.pdf_file.split('.')[0]}_annotated.pdf", "wb") as fp:
    writer.write(fp)
