clc
clear
A = imread('image1.tif');
B = [0 1 0
     1 1 1
     0 1 0];
 A2 = imdilate(A, B);
 A3 = imdilate(A2, B); % 二次膨胀
 A4 = imdilate(A3, B); % 三次膨胀
%  A2 = imdilate(B,A);
figure;
subplot(2,3,1)
imshow(A)
title('原始图像')
subplot(2,3,2)
imshow(A2)
title('使用结构元素[B]一次膨胀后的图像')
subplot(2,3,3)
imshow(A3)
title('使用结构元素[B]二次膨胀后的图像')
subplot(2,3,4)
imshow(A4)
title('使用结构元素[B]三次膨胀后的图像')
subplot(2,3,5)
imshow(A2-A) % 显示增加的部分
title('使用结构元素[B]一次膨胀后和原图像相比较增加的部分')