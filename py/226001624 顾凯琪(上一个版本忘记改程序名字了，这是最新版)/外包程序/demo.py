import cv2
import os

list = []
path_dir = './images'
out_dir = './output'
for i in os.listdir(path_dir):
    if i.split('-')[1][:-4] not in list:
        if not os.path.exists(out_dir + '/' + str(i.split('-')[1][:-4])):
            os.mkdir(out_dir + '/' + str(i.split('-')[1][:-4]))
        list.append(str(i.split('-')[1][:-4]))
    im = cv2.imread(path_dir + '/' + i)
    cv2.imwrite(out_dir + '/' + str(i.split('-')[1][:-4]) + '/' + i,im)
    print(i)