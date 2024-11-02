import sys
import os
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import AnnotationBuilder

x = float(input("Enter value for x: "))
y = float(input("Enter value for y: "))
s = 10  # size

pdf_path = os.path.join(".", "test.pdf")
reader = PdfReader(pdf_path)
page = reader.pages[0]
writer = PdfWriter()
writer.add_page(page)

# # Draw rect
# annotation = AnnotationBuilder.rectangle(
#     rect=(x - s, y - s, x + s, y + s),
#     #interiour_color="ff0000", #fill
# )

# Create the annotation
annotation = AnnotationBuilder.text(
    rect=(x - s, y - s, x + s, y + s),
    text = "Hello World\nThis is the second line!",
)

writer.add_annotation(page_number=0, annotation=annotation)

# Write the annotated file to disk
with open("out.pdf", "wb") as fp:
    writer.write(fp)
