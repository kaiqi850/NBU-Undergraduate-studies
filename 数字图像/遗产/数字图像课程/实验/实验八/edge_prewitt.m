clc
clear
f = imread('image1.tif');

figure;
subplot(2,2,1)
imshow(f)
title('原始图像')

[gv1,t] = edge(f,'prewitt','vertical');
subplot(2,2,2)
imshow(gv1)
title('使用带有自动确定的阈值的一个垂直[prewitt]掩模后，函数[edge]导致的结果')

gv2 = edge(f,'prewitt',0.15,'vertical');
subplot(2,2,3)
imshow(gv2)
title('使用指定阈值的一个垂直[prewitt]掩模后，函数[edge]导致的结果')

gboth = edge(f,'prewitt',0.15);
subplot(2,2,4)
imshow(gboth)
title('使用指定阈值的一个同时考虑水平垂直[prewitt]掩模后，函数[edge]导致的结果')