from PIL import Image
import sys
import cv2
import numpy as np

class image_converter:

	def convert_PIL_to_cv2(self, image_PILL):
		pil_image = image_PILL.convert('RGB') 
		open_cv_image = np.array(pil_image) 
		open_cv_image = open_cv_image[:, :, ::-1].copy() 
		return open_cv_image

	def convert_cv2_to_PIL(self, image_cv):
		image_cv = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
		im_pil = Image.fromarray(image_cv)
		return im_pil