import pytesseract
from PIL import Image
from matplotlib import pyplot as plt
import sys
import numpy as np
import cv2
import sys
import random
import math
from image_preprocessing import image_converter
from collections import Counter
import statistics
from statistics import mode
from convert_PDF_TO_JPG import pdf_to_images
import os


sys.setrecursionlimit(100000) 

class INN_parser:
	def __init__(self):
		self.INN_len = 12
		self.converter = image_converter()
		self.dx = [0, 0, 1, -1]
		self.dy = [1, -1, 0, 0]
		self.parts_number = [17, 18, 19, 20, 21, 22, 23, 24]
		self.used = []
		self.MIN_area_x, self.MAX_area_x, self.MIN_area_y, self.MAX_area_y = 0, 0, 0, 0
		self.current_cropped_img_cv = None
		self.current_cropped_img_pil = None
		self.current_cropped_img_pil_BW = None
		self.thresholds = [120, 140, 170, 200, 210]
		self.threshold = 200
		self.custom_oem_psm_config = r'--oem 1 --psm 7'
		self.ez_INN_pool = []
		self.INN_validate_coefs1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8, 0, 0]
		self.INN_validate_coefs2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8, 0]

	def validate_INN (self, INN):
		check_sum1 = 0
		check_sum2 = 0
		for sym_num in range(len(INN)):
			check_sum1 += int(INN[sym_num]) * self.INN_validate_coefs1[sym_num]
			check_sum2 += int(INN[sym_num]) * self.INN_validate_coefs2[sym_num]
		check_sum1 %= 11
		check_sum1 %= 10
		check_sum2 %= 11
		check_sum2 %= 10
		return check_sum1 == int(INN[10]) and check_sum2 == int(INN[11])

	def set_image(self, path_to_image):
		print(path_to_image)
		filename, file_extension = os.path.splitext(path_to_image)
		print(file_extension)
		if (file_extension.lower() == ".pdf"):
			pdf_to_images(path_to_image)
			path_to_image = "0.jpg"

		self.img_pil = Image.open(path_to_image)
		self.img_cv = self.converter.convert_PIL_to_cv2(self.img_pil)
		self.width, self.height = self.img_pil.size
		self.MIN_area_size, self.MAX_area_size  = self.height // 200, self.height // 50 #NOT CONSTANT
		self.variant = []

	def add_to_list (self, INN):
		if (len(INN) == self.INN_len):
			self.variant.append(INN)

	def recover_digits (self, digit_line):
		for i in range(len(digit_line)):
			digit_line = digit_line.replace("з", '3')
			digit_line = digit_line.replace("З", '3')
			digit_line = digit_line.replace("o", '0')
			digit_line = digit_line.replace("о", '0')
			digit_line = digit_line.replace("О", '0')
			digit_line = digit_line.replace("O", '0')
			digit_line = digit_line.replace("т", '7')
			digit_line = digit_line.replace("Т", '7')
		return digit_line

	def try_parse_iz_image (self, text):
		INN = ""
		start_inn = False
		for sym in text:
			if sym.isdigit() and start_inn:
				INN += sym
			else:
				if sym.isalpha():
					start_inn = True
		#print("EZ PARCE INN:", INN)
		return INN

	def check_inner_area(self, MIN_x, MAX_x, MIN_y, MAX_y):
		return (1 < (MAX_y - MIN_y + 1) / (MAX_x - MIN_x + 1) < 3 and MAX_y - MIN_y > self.MIN_area_size and MAX_y - MIN_y < self.MAX_area_size)

	def check_range(self, i, j, w, h):
		return not((j >= h) or (i >= w) or (j < 0) or (i < 0))

	def check_color (self, pix):#IF image BW rework
		R,G,B = pix
		LuminanceB = (0.299*R + 0.587*G + 0.114*B)
		return LuminanceB == 0

	def dfs (self, i, j, color, cnt): #NEED BFS?
		self.MIN_x = min(self.MIN_x, i)
		self.MAX_x = max(self.MAX_x, i)
		self.MIN_y = min(self.MIN_y, j)
		self.MAX_y = max(self.MAX_y, j)
		if (cnt == 3000):
			return
		width, height = self.current_cropped_img_pil.size

		self.current_cropped_img_pil.putpixel((i, j), color)

		
		self.used[i][j] = True
		#self.current_cropped_img_pil_BW.putpixel((i, j), color)
		for d in range(4):
			if (self.check_range(i + self.dx[d], j + self.dy[d], width, height) and self.check_color(self.current_cropped_img_pil_BW.getpixel((i + self.dx[d], j + self.dy[d]))) and not self.used[i + self.dx[d]][j + self.dy[d]]):
				self.dfs(i + self.dx[d], j + self.dy[d], color, cnt + 1)

	def select_areas(self, posible_variants):
		posible_variants.sort(key=lambda x: x[1])
		for variant in range(len(posible_variants)):
			areas = [posible_variants[variant]]
			res = ""
			can_be_INN = []
			if len(posible_variants) - variant >= 12:
				for i in range(variant + 1, min(len(posible_variants), variant + 40)):
					if abs(areas[0][1] - posible_variants[i][1]) < self.MIN_area_size / 2:
						areas.append(posible_variants[i])
				areas.sort(key=lambda x: x[0])
				print(areas)
				#print(areas)
				if len(areas) >= self.INN_len:
					for start_ind in range(len(areas) - 1):
						res = ""
						res += areas[start_ind][4]
						res_description = []
						res_description.append(areas[start_ind])
						curent_x = areas[start_ind][0]
						for item in areas[start_ind + 1:]:
							if (abs(item[0] - curent_x)) < self.MAX_area_size  * 2:
								curent_x = item[2]
								res += item[4]
								res_description.append(item)
						#print(res)
						if len(res) == self.INN_len and self.validate_INN(res):
							print(res)
							return res, res_description
						if len(res) == self.INN_len:
							print("NOT VALID INN:", res)
		return "", []

	def start_dfs (self):
		self.current_cropped_img_pil_BW = self.converter.convert_cv2_to_PIL(self.current_cropped_img_cv)
		dig_cnt = 0
		width, height = self.current_cropped_img_pil.size
		self.used = np.zeros((width, height)).tolist()
		digit_list_parts_parse = []
		color_background = None
		digit_list = []
		posible_areas = []
		print(self.threshold)
		for j in range(height):
			for i in range(width):
				if (self.check_color(self.current_cropped_img_pil_BW.getpixel((i,j))) and not self.used[i][j]):
					self.MIN_x = self.MAX_x = i
					self.MIN_y = self.MAX_y = j
					if (self.current_cropped_img_pil.mode == "RGB"):
						self.dfs(i, j, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 0)
					else:
						self.dfs(i, j, (random.randint(0, 255)), 0)

					if (self.check_inner_area(self.MIN_x, self.MAX_x, self.MIN_y, self.MAX_y)):
						#BW if good Quality else ..
						#if self.width > 1500: #WHAT IS GOOD Quality?
						#digit = self.current_cropped_img_pil_BW.crop((self.MIN_x, self.MIN_y, self.MAX_x + 2, self.MAX_y + 2))
						#else:
						digit = self.current_cropped_img_pil_BW.crop((self.MIN_x - 1, self.MIN_y - 1, self.MAX_x + 2, self.MAX_y + 2))
						
						digit2 = digit.resize((28, 28), Image.ANTIALIAS)

						#self.MAX_area_size = 28

						color_background = digit.getpixel((0,0))
						img_with_background = digit

						img_with_background = Image.new('RGB', (self.MAX_area_size * 2, self.MAX_area_size * 2),  (255, 255, 255)) #REWORK NO Const
						img_with_background.paste(digit, (self.MAX_area_size // 2, self.MAX_area_size // 2)) #insert digit to mid
						
						custom_oem_psm_config_one_char = r'--oem 1 --psm 10'

						text = pytesseract.image_to_string(img_with_background, 'rus', config=custom_oem_psm_config_one_char)
						print(text)

						text = self.recover_digits(text)
						cnt_digits = 0
						for sym in text:
							if sym.isdigit():
								cnt_digits += 1

						#img_with_background.save("test/" + str(self.threshold) + '_' + str(self.MIN_x) + '_' + str(self.MIN_y) + ".jpg")
						#print(str(self.threshold) + '_' + str(self.MIN_x) + '_' + str(self.MIN_y) + ".jpg: ", text)
								
						for sym in text:
							if sym.isdigit() and (cnt_digits == 1 or sym != '1'):
								text = sym
								break
							else:
								cnt_digits = 1
						
						
						#print(str(self.threshold) + '_' + str(self.MIN_x) + '_' + str(self.MIN_y) + ".jpg: ", text)	
						#digit.save("test/" + str(self.threshold) + '_' + str(int(self.MIN_y / 100)) + '_' + str(self.MIN_x) + ".jpg")	
						if text.isdigit():
							digit2.save("test/" + "dig" + str(self.threshold) + '_' + str(int(self.MIN_y / 100)) + '_' + str(self.MIN_x) + ".jpg")
							img_with_background.save("test/" + str(self.threshold) + '_' + str(int(self.MIN_y / 100)) + '_' + str(self.MIN_x) + ".jpg")
							print("test/" + str(self.threshold) + '_' + str(int(self.MIN_y / 100)) + '_' + str(self.MIN_x) + ".jpg = ", text, "  " + str(self.MIN_y))
							posible_areas.append([self.MIN_x, self.MIN_y, self.MAX_x, self.MAX_y, text])
		print(len(posible_areas))
		res = self.select_areas(posible_areas)[0]
		if res != '':
			print(res)
			return True
		return False


	def find_INN(self):
		for self.threshold in self.thresholds:
			self.current_cropped_img_pil = self.img_pil.copy()
			self.current_cropped_img_cv = self.converter.convert_PIL_to_cv2(self.current_cropped_img_pil)
			self.current_cropped_img_cv = cv2.cvtColor(self.current_cropped_img_cv,cv2.COLOR_BGR2GRAY)
			self.current_cropped_img_cv = cv2.threshold(self.current_cropped_img_cv, self.threshold, 255, cv2.THRESH_BINARY)[1]#Для обхода в глубину/ширину
			
			find = self.start_dfs()

			self.current_cropped_img_pil.save("test/INN_dfs" + str(self.threshold) + ".jpg")
			cv2.imwrite("test/INN" + str(self.threshold) + ".jpg", self.current_cropped_img_cv)
			if (find):
				return