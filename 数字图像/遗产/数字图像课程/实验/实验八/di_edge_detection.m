clc
clear
f = imread('image1.tif');

figure;
subplot(2,2,1)
imshow(f)
title('原始图像')

w45 = [-2 -1 0; -1 0 1; 0 1 2];
g45 = imfilter(double(f),w45,'replicate');
T = 0.3*max(abs(g45(:)));
g45 = g45>=T;
subplot(2,2,2)
imshow(g45)
title('使用函数[imfilter]（具有指定的掩模和阈值）计算[45度]边缘的结果')

w_45 = [0 1 2; -1 0 1; -2 -1 0];
g_45 = imfilter(double(f),w_45,'replicate');
T = 0.3*max(abs(g_45(:)));
g_45 = g_45>=T;
subplot(2,2,3)
imshow(g_45)
title('使用函数[imfilter]（具有指定的掩模和阈值）计算[-45度]边缘的结果')

subplot(2,2,4)
imshow(g45 + g_45)
title('使用函数[imfilter]（具有指定的掩模和阈值）计算[-45度]+[45度]边缘的结果')