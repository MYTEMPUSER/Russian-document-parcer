from Parse_INN import INN_parser
from PIL import Image
from convert_PDF_TO_JPG import pdf_to_images
import pytesseract
import os 

#file = "INN_with_cells/Ian_INN.pdf" 
parser = INN_parser()
#parser.set_image(file)
#parser.find_INN()

directory = 'INN_with_cells'  
files = os.listdir(directory)
for file in files:
	parser.set_image(directory + '/' + file)
	parser.find_INN()
#parser.try_find_inn_atomic()