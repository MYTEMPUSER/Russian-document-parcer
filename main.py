from Parce_INN import INN_parcer
from PIL import Image
from convert_PDF_TO_JPG import pdf_to_images
import pytesseract


file = "INN (5).jpg"
custom_oem_psm_config_one_char = r'--oem 1 --psm 7'
#pdf_to_images("romashko_inn.PDF")

#img = Image.open(file)

#text = pytesseract.image_to_string(img, 'rus', config=custom_oem_psm_config_one_char)
#print(text)

parcer = INN_parcer()
parcer.set_image(file)
parcer.find_INN()
#parcer.try_find_inn_atomic()