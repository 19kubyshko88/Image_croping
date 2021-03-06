import os, re
from PIL import Image
import cv2 as cv
import numpy as np
import pytesseract
from pdf2image import convert_from_path
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Store Pdf with convert_from_path function
images = convert_from_path(r'C:\Users\19kub\Desktop\New_folder\receipt.pdf', dpi=200,
                           poppler_path = r'D:\progs\PythonLibs\poppler-21.03.0\Library\bin')
for i in range(len(images)):
    # Save pages as images in the pdf
    images[i].save(r'C:\Users\19kub\Desktop\New_folder\page' + str(i) + '.jpg', 'JPEG')

directory=r'C:\Users\19kub\Desktop\New_folder'
list_of_files_in_directory = os.listdir(directory)
list_of_images = [i for i in list_of_files_in_directory if i[-4:]== ".jpg"]


for name_img in list_of_images:
    img_to_crop = Image.open(f'{directory}/{name_img}')

    # Ищем пунктирную линию между квитанциями
    # Search for the dotted line between receipts
    img = cv.imread(cv.samples.findFile(relative_path=r"C:\Users\19kub\Desktop\New_folder\\" + name_img))
    kernel1 = np.ones((2,10),np.uint8)    # Здесь менял цифры для подбора линии
    kernel2 = np.ones((9,9),np.uint8)

    imgGray=cv.cvtColor(img,cv.COLOR_BGR2GRAY)



    imgBW=cv.threshold(imgGray, 230, 255, cv.THRESH_BINARY_INV)[1]

    img1=cv.erode(imgBW, kernel1, iterations=1)
    img2=cv.dilate(img1, kernel2, iterations=3)
    img3 = cv.bitwise_and(imgBW,img2)
    img3= cv.bitwise_not(img3)
    img4 = cv.bitwise_and(imgBW,imgBW,mask=img3)
    imgLines= cv.HoughLinesP(img4,5,np.pi/180,10, minLineLength = 500, maxLineGap = 10) # И здесь менял цифры для подбора линии

    for i in range(len(imgLines)):
        l = imgLines[i][0]
        cv.line(img,(l[0], l[1]), (l[2], l[3]), (0,255,0),2) # (l[0],l[1]), (l[2],l[3]) Х,У - коорд. начала и конца линии
        print((l[0], l[1]), (l[2], l[3]))

        if 100<l[1] < 1500:     # approximately here is the line we are looking for
            y_of_cut1 = l[1]
            break
    """ # Uncomment to see the line found
    cv.namedWindow('Final Image with dotted Lines detected', cv.WINDOW_NORMAL)
    cv.imshow('Final Image with dotted Lines detected', img)
    cv.waitKey()
    """
    # Режем файл по поответствующей координате y, распознаём чья это квитанция и сохраняем по нужным именем
    # We cut the file by the corresponding y-coordinate, recognize whose receipt it is and save it by the correct name
    width, height = img_to_crop.size
    im_crop1 = img_to_crop.crop((0, 0, width, y_of_cut1))
    pattern = r'ФИО: (\w+) '
    config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(im_crop1, config=config, lang='rus') # весь текст с картинки
    # print(text)
    match = re.search(pattern, text)
    print(name_img, match[1])
    if match:
        # print('_____________________________________________')
        # print(f'Найдена подстрока >{match[1]}< с позиции {match.start(0)} до {match.end(0)}')
        # print('_____________________________________________')
        im_crop1.save(f'IMG_Croped/{match[1]}.jpg','JPEG', quality=95)
        # print(text)
    else:
        print(name_img)
    # I know it's not good, but it was faster than creating a function. One day I'll fix it. :)
    im_crop2 = img_to_crop.crop((0, y_of_cut1, width, height))
    text = pytesseract.image_to_string(im_crop2, config=config, lang='rus')
    match = re.search(pattern, text)
    if match:
        # print('_____________________________________________')
        # print(f'Найдена подстрока >{match[1]}< с позиции {match.start(0)} до {match.end(0)}')
        # print('_____________________________________________')
        im_crop2.save(f'IMG_Croped/{match[1]}.jpg','JPEG', quality=95)
    else:
        print(name_img)



