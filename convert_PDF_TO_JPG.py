import os
import pdf2image

def pdf_to_images(pdf_path, pdf_images_dir=None):
    if not pdf_images_dir:
        pdf_images_dir = ''
    pdf_path = os.path.abspath(pdf_path)
    pdf_images_dir = os.path.abspath(pdf_images_dir)
    if not os.path.exists(pdf_images_dir):
        os.mkdir(pdf_images_dir)
    count = 0
    for page in pdf2image.convert_from_path(pdf_path, 200):
        page.save(os.path.join(pdf_images_dir, str(count) + '.jpg'), quality=95)
        count += 1
    #result = []
    #for i in range(count):
    #    result.append(cv2.cvtColor(cv2.imread(os.path.join(pdf_images_dir, str(i) + '.jpg')), cv2.COLOR_BGR2GRAY))
    #return result