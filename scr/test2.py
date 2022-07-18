import io
import os

# Imports the Google Cloud client library
from google.cloud import vision

# Instantiates a client
client = vision.ImageAnnotatorClient()

# The name of the image file to annotate
file_name = os.path.abspath("./003cut.png")

# # Loads the image into memory
with io.open(file_name, "rb") as image_file:
    content = image_file.read()

image = vision.Image(content=content)

# Performs label detection on the image file
response = client.document_text_detection(
    image=image, image_context={"language_hints": ["ja"]}
)

# レスポンスからテキストデータを抽出
output_text = ""
for page in response.full_text_annotation.pages:
    for block in page.blocks:
        for paragraph in block.paragraphs:
            for word in paragraph.words:
                output_text += "".join([symbol.text for symbol in word.symbols])
    output_text += "\n"
print(output_text)
