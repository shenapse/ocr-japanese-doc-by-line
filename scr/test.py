import io
import os

import pdf2image

# Imports the Google Cloud client library
from google.cloud import vision

# Instantiates a client
client = vision.ImageAnnotatorClient()

# pdfから画像オブジェクトに
images = pdf2image.convert_from_path(pdf_path="test_pdf.pdf", dpi=200, fmt="jpg")

output_text = ""

# レスポンスからテキストデータを抽出
for image in images:
    # Performs label detection on the image file
    response = client.document_text_detection(
        image=image, image_context={"language_hints": ["ja"]}
    )
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    output_text += "".join([symbol.text for symbol in word.symbols])
                output_text += "\n"
print(output_text)
