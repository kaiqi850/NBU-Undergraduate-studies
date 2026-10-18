clc
clear

figure;
f = imread('image1.tif');
subplot(231)
imshow(f)
title('原始图像')

[gv1,tvertical] = edge(f,'sobel','vertical');
subplot(232)
imshow(gv1)
title('使用带有自动确定的阈值的一个垂直[sobel]掩模后，函数[edge]导致的结果')

[gv1,thorizontal] = edge(f,'sobel','horizontal');
subplot(233)
imshow(gv1)
title('使用带有自动确定的阈值的一个水平[sobel]掩模后，函数[edge]导致的结果')

gv2 = edge(f,'sobel',0.15,'vertical');
subplot(234)
imshow(gv2)
title('使用指定阈值的一个垂直[sobel]掩模后，函数[edge]导致的结果')

gboth = edge(f,'sobel',0.15);
subplot(235)
imshow(gboth)
title('使用指定阈值的一个同时考虑水平垂直[sobel]掩模后，函数[edge]导致的结果')

[gboth,tboth] = edge(f,'sobel');
subplot(236)
imshow(gboth)
title('使用自动阈值的一个同时考虑水平垂直[sobel]掩模后，函数[edge]导致的结果')