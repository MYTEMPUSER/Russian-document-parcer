from Parse_INN import INN_parser
import os 

file = "инн.jpg" 
parser = INN_parser()
parser.set_image(file)
print(parser.find_INN())