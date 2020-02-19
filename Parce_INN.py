import pytesseract
from PIL import Image
from matplotlib import pyplot as plt
import sys
import numpy as np
import cv2
import sys
import random
from image_preprocessing import image_converter
from collections import Counter
import statistics
from statistics import mode

  



sys.setrecursionlimit(100000) 

class INN_parcer:

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
		self.thresholds = [140, 150, 160, 170, 180, 190, 200, 210]
		self.threshold = 200
		self.custom_oem_psm_config = r'--oem 1 --psm 7'
		self.ez_INN_pool = []
		

	def set_image(self, path_to_image):
		image = Image.open(path_to_image)
		self.img_pil = image
		self.img_cv = self.converter.convert_PIL_to_cv2(self.img_pil)
		self.width, self.height = self.img_pil.size
		self.MIN_area_size, self.MAX_area_size  = self.width // 65, self.width // 35 #NOT CONSTANT
		self.variant = []

	def add_to_list (self, INN):
		if (len(INN) == self.INN_len):
			self.variant.append(INN)

	def recover_digits (self, digit_line):
		digit_line = digit_line.replace("з", '3')
		digit_line = digit_line.replace("З", '3')
		digit_line = digit_line.replace("o", '0')
		digit_line = digit_line.replace("о", '0')
		digit_line = digit_line.replace("О", '0')
		digit_line = digit_line.replace("O", '0')
		return digit_line

	def try_parce_iz_image (self, text):
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
		return (0.7 < (MAX_x - MIN_x + 1) / (MAX_y - MIN_y + 1) < 1.3 and MAX_x - MIN_x > self.MIN_area_size and MAX_x - MIN_x < self.MAX_area_size)

	def check_range(self, i, j, w, h):
		return not((j >= h) or (i >= w) or (j < 0) or (i < 0))

	def check_color (self, pix):#IF image BW rework
		R,G,B = pix
		LuminanceB = (0.299*R + 0.587*G + 0.114*B)
		return LuminanceB > 50

	def dfs (self, i, j, color, cnt): #NEED BFS?
		self.MIN_x = min(self.MIN_x, i)
		self.MAX_x = max(self.MAX_x, i)
		self.MIN_y = min(self.MIN_y, j)
		self.MAX_y = max(self.MAX_y, j)
		if (cnt == 3000):
			return
		width, height = self.current_cropped_img_pil.size

		#self.current_cropped_img_pil.putpixel((i, j), color)
		
		self.used[i][j] = True
		#self.current_cropped_img_pil_BW.putpixel((i, j), color)
		for d in range(4):
			if (self.check_range(i + self.dx[d], j + self.dy[d], width, height) and self.check_color(self.current_cropped_img_pil_BW.getpixel((i + self.dx[d], j + self.dy[d]))) and not self.used[i + self.dx[d]][j + self.dy[d]]):
				self.dfs(i + self.dx[d], j + self.dy[d], color, cnt + 1)

	def start_dfs (self):
		self.current_cropped_img_pil_BW = self.converter.convert_cv2_to_PIL(self.current_cropped_img_cv)
		dig_cnt = 0
		width, height = self.current_cropped_img_pil.size
		self.used = np.zeros((width, height)).tolist()
		digit_list_parts_parce = []
		color_background = None
		digit_list = []

		for i in range(width):
			for j in range(height):
				if (self.check_color(self.current_cropped_img_pil_BW.getpixel((i,j))) and not self.used[i][j]):
					self.MIN_x = self.MAX_x = i
					self.MIN_y = self.MAX_y = j
					self.dfs(i, j, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 0)

					if (self.check_inner_area(self.MIN_x, self.MAX_x, self.MIN_y, self.MAX_y)):
						#BW if good Quality else ..
						digit = self.current_cropped_img_pil_BW.crop((self.MIN_x + 1, self.MIN_y + 1, self.MAX_x, self.MAX_y))
						color_background = digit.getpixel((0,0))
						img_with_background = Image.new('RGB', (self.MAX_area_size * 3 // 2, self.MAX_area_size * 3 // 2),  color_background) #REWORK NO Const
						img_with_background.paste(digit, (7, 7)) #insert digit to mid
						custom_oem_psm_config_one_char = r'--oem 1 --psm 10'
						text = pytesseract.image_to_string(img_with_background, 'rus', config=custom_oem_psm_config_one_char)
						dig_cnt += 1
						img_with_background.save("test/INN_num" + str(dig_cnt) + ".jpg")
						text = self.recover_digits(text)
						if (text.isdigit()):
							digit_list.append(digit)
							digit_list_parts_parce.append(text)


		digit_list_in_sequence_parce = []
		if (color_background != None):
			img = Image.new('RGB', (self.MAX_area_size * 3 * 12 // 2, self.MAX_area_size * 3 // 2),  color_background)#REWORK NO Const
			sum_x = 10
			digit_list_parce_rebuild = []	
			for digit in digit_list:
				img.paste(digit, (sum_x, 7))
				width, height = digit.size
				sum_x += width
				custom_oem_psm_config = r'--oem 1 --psm 7'
				text = pytesseract.image_to_string(img, 'rus', config=custom_oem_psm_config)
				digit_list_parce_rebuild = text
				if len(text) > 0:
					digit_list_in_sequence_parce.append(text[-1])
			if digit_list_parce_rebuild != []:
				digit_list_parce_rebuild = digit_list_parce_rebuild.replace(" ", "")
				digit_list_parce_rebuild = self.recover_digits(digit_list_parce_rebuild)
			digit_list_in_sequence_parce =self.recover_digits(''.join(digit_list_in_sequence_parce))
			digit_list_parts_parce = self.recover_digits(''.join(digit_list_parts_parce))
			self.add_to_list(digit_list_parce_rebuild)
			self.add_to_list(digit_list_in_sequence_parce)
			self.add_to_list(digit_list_parts_parce)
			print("REBUILD ALL: ", digit_list_parce_rebuild)
			print("In sequence parce: ", digit_list_in_sequence_parce)
			print("Parts parce: ", digit_list_parts_parce)
			img.save("test/rebuild.jpg")

	def select_INN(self, INN_list):
		if (len(INN_list) > 0):
			print(mode(INN_list))

	def try_find_inn_solid_string(self):
		x_scale = [2, 3]
		y_scale = [20]
		offset_x = [0/10, 1/10, 2/10, 3.5/10, 5/10]
		offset_y = [0/10, 5/10]
		dict_INN = {}
		for x_sc in x_scale:
			for y_sc in y_scale:
				for off_x in offset_y:
					for off_y in offset_y:
						part_sz_x = self.width / x_sc
						part_sz_y = self.height / y_sc
						for left_pos in range(int(self.width / part_sz_x)):
							for top_pos in range(int(self.height // part_sz_y)):
								area = ((left_pos + off_x)  * part_sz_x, (top_pos + off_y) * part_sz_y, (left_pos + 1 + off_x)  * part_sz_x, (top_pos + 1 + off_y) * part_sz_y)
								part = self.img_pil.crop(area)
								text = pytesseract.image_to_string(part, 'rus', config=self.custom_oem_psm_config)
								text = text.replace(" ", "")
								if len(text) >= 12:
									text = text[-12:]
									text = ''.join([sym for sym in text if sym.isdigit()])
									if (len(text) == self.INN_len and text.isdigit()):
										print(text)
										if not (text in dict_INN):
											dict_INN[text] = 0 
										else:
											print(text)
											return text


	def find_INN(self):
		for parts in self.parts_number:
			for i in range(parts):
				area = (0, i * (self.height / parts), self.width, (i + 1) * (self.height / parts))
				self.current_cropped_img_pil = self.img_pil.crop(area)
				cropped_img_name = "test/part" + str(i) + ".png"
				self.current_cropped_img_pil.s ave(cropped_img_name)

				text = pytesseract.image_to_string(self.current_cropped_img_pil, 'rus', config=self.custom_oem_psm_config)

				if "инн" in text.lower():
					print("string with INN:", text)
					INN = self.try_parce_iz_image(text)
					if (len(INN) == self.INN_len):
						self.ez_INN_pool.append(INN)

					print("INN after parce: ", INN)
					for self.threshold in self.thresholds:
						self.current_cropped_img_cv = self.converter.convert_PIL_to_cv2(self.current_cropped_img_pil)
						self.current_cropped_img_cv = cv2.cvtColor(self.current_cropped_img_cv,cv2.COLOR_BGR2GRAY)
						self.current_cropped_img_cv = cv2.threshold(self.current_cropped_img_cv, self.threshold, 255, cv2.THRESH_BINARY)[1]#Для обхода в глубину/ширину

						self.start_dfs()
						self.current_cropped_img_pil.save("test/INN_dfs.jpg")
						cv2.imwrite("test/INN.jpg", self.current_cropped_img_cv)

		self.select_INN(self.variant)
		self.select_INN(self.ez_INN_pool)