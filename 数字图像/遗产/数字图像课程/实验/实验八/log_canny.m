clc
clear

figure;
f = imread('image1.tif');
subplot(2,3,1)
imshow(f)
title('原始图像')

[g_log_default,tlog] = edge(f,'log');
subplot(2,3,2)
imshow(g_log_default)
title('[LoG]边缘检测器使用默认选项产生的结果')

[g_canny_default,tc] = edge(f,'canny');
subplot(2,3,3)
imshow(g_canny_default)
title('[canny]边缘检测器使用默认选项产生的结果')

[g_log_best,tlog] = edge(f,'log',0.003,2.25);
subplot(2,3,4)
imshow(g_log_best)
title('[LoG]边缘检测器使用 edge(f,log,0.003,2.25) 产生的结果')

[g_canny_best,tc] = edge(f,'canny',[0.04 0.10],1.5);
subplot(2,3,5)
imshow(g_canny_best)
title('[canny]边缘检测器使用 edge(f,canny,[0.04 0.10],1.5) 产生的结果')