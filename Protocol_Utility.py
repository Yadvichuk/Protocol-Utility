
# coding: utf-8

from pdf2image import convert_from_path
import shutil
import os
import re
import cv2
from pytesseract import Output
from PyPDF2 import PdfFileReader, PdfFileWriter
from tqdm import tqdm

YOUR_DIR = r'C:\Users\Home\Desktop\openCV'
PROT_DIR = YOUR_DIR + r'\Protocols'
IMG_DIR = YOUR_DIR + r'\images'
RES_DIR = YOUR_DIR + r'\result'
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
custom_config = r'--oem 3 --psm 6'
data_pattern = '[A-Z][A-Z0-9][A-Z0-9][-][A-Z0-9][A-Z0-9][-][A-Z0-9][A-Z0-9]'
os.mkdir(RES_DIR)

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
    lenfile = convert(x)
    pages = [0]*lenfile
    for i in tqdm(range(lenfile)):
        image = cv2.imread(IMG_DIR + '\\'+str(i)+'.jpg')
        d = pytesseract.image_to_data(image, output_type=Output.DICT)
        n_boxes = len(d['text'])
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
        output_filename = '{}\\{}.pdf'.format(RES_DIR, pages[pages_num[k]])

        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)

        print('Created: {}'.format(output_filename))
    pdf_writer = PdfFileWriter()
    for k in tqdm(range(pages_num[-1], lenfile)):
        pdf_writer.addPage(pdf.getPage(k))
    output_filename = '{}\\{}.pdf'.format(RES_DIR, pages[pages_num[-1]])

    with open(output_filename, 'wb') as out:
        pdf_writer.write(out)

    print('Created: {}'.format(output_filename))

