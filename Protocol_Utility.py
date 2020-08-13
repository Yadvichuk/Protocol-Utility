
# coding: utf-8

from pdf2image import convert_from_path
import shutil
import os
import re
import cv2
import pytesseract
from pytesseract import Output
from PyPDF2 import PdfFileReader, PdfFileWriter
from tqdm import tqdm
import math

YOUR_DIR = r'C:\Users\Home\Desktop\openCV'
PROT_DIR = YOUR_DIR + r'\Protocols'
IMG_DIR = YOUR_DIR + r'\images'
RES_DIR = YOUR_DIR + r'\result'
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
custom_config = r'--oem 3 --psm 6'
data_pattern = '[A-Z][A-Z0-9][A-Z0-9][-][A-Z0-9][A-Z0-9][-][A-Z0-9][A-Z0-9]'
os.mkdir(RES_DIR)

def rotate_image(image, angle):
    image_height = image.shape[0]
    image_width = image.shape[1]
    diagonal_square = (image_width*image_width) + (
        image_height* image_height
    )
    #
    diagonal = round(math.sqrt(diagonal_square))
    padding_top = round((diagonal-image_height) / 2)
    padding_bottom = round((diagonal-image_height) / 2)
    padding_right = round((diagonal-image_width) / 2)
    padding_left = round((diagonal-image_width) / 2)
    padded_image = cv2.copyMakeBorder(image,
                                      top=padding_top,
                                      bottom=padding_bottom,
                                      left=padding_left,
                                      right=padding_right,
                                      borderType=cv2.BORDER_CONSTANT,
                                      value=0
            )
    padded_height = padded_image.shape[0]
    padded_width = padded_image.shape[1]
    transform_matrix = cv2.getRotationMatrix2D(
                (padded_height/2,
                 padded_width/2), # center
                angle, # angle
      1.0) # scale
    rotated_image = cv2.warpAffine(padded_image,
                                   transform_matrix,
                                   (diagonal, diagonal),
                                   flags=cv2.INTER_LANCZOS4)
    return rotated_image

def convert(path):
    pages = convert_from_path(path)
    i = 0
    for page in pages:
        page.save(IMG_DIR + "\\" + str(i) + ".jpg","JPEG")
        i+=1
    return i

def clean_dir():
    shutil.rmtree(IMG_DIR)
    os.mkdir(IMG_DIR)

main_dir = []
for file in os.listdir(PROT_DIR):
    if file.endswith(".pdf"):
        main_dir.append(os.path.join(PROT_DIR, file))
print(main_dir)

for x in main_dir:
    print(x)
    print(re.match('[0-9]+',x.split('\\')[-1]).group(0))
    os.mkdir(RES_DIR+'\\'+re.match('[0-9]+',x.split('\\')[-1]).group(0))
    lenfile = convert(x)
    pages = [0]*lenfile
    for i in tqdm(range(lenfile)):
        image = cv2.imread(IMG_DIR + '\\'+str(i)+'.jpg')
        pos = 0
        d = pytesseract.image_to_data(image, output_type=Output.DICT)
        n_boxes = len(d['text'])
        f = True
        while f and pos<4:
            for j in range(n_boxes):
                if int(d['conf'][j]) > 60 and re.match(data_pattern, d['text'][j]):
                    pages[i] = re.match(data_pattern, d['text'][j]).group(0)
                    f = False
                    break
            image = rotate_image(image, 90)
            d = pytesseract.image_to_data(image, output_type=Output.DICT)
            n_boxes = len(d['text'])
            pos+=1
        for j in range(n_boxes):
            if int(d['conf'][j]) > 60 and re.match(data_pattern, d['text'][j]):
                pages[i] = re.match(data_pattern, d['text'][j]).group(0)
    clean_dir()
    pages_num = [i for i in range(len(pages)) if pages[i]!=0]
    pdf = PdfFileReader(x,strict=False)
    for k in tqdm(range(len(pages_num)-1)):
        pdf_writer = PdfFileWriter()
        for j in range(pages_num[k+1]-pages_num[k]):
            pdf_writer.addPage(pdf.getPage(pages_num[k] + j))
        output_filename = '{}\\{}.pdf'.format(RES_DIR+'\\' + re.match('[0-9]+',x.split('\\')[-1]).group(0), pages[pages_num[k]])

        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)

        print('Created: {}'.format(output_filename))
    pdf_writer = PdfFileWriter()
    for k in tqdm(range(pages_num[-1], lenfile)):
        pdf_writer.addPage(pdf.getPage(k))
    output_filename = '{}\\{}.pdf'.format(RES_DIR+re.match('[0-9]+',x.split('\\')[-1]).group(0), pages[pages_num[-1]])

    with open(output_filename, 'wb') as out:
        pdf_writer.write(out)

    print('Created: {}'.format(output_filename))

