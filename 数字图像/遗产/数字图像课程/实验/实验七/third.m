clc;
clear;
A = imread('image3.tif'); % 读取图像

% 定义不同的结构元
seB = [0 1 0
       1 1 1
       0 1 0]; % 十字形结构元
seC = [1 1 1
       1 1 1
       1 1 1]; % 全1的矩阵，各向同性腐蚀
seD = [0 0 1 0 0
       0 1 1 1 0
       1 1 1 1 1
       0 1 1 1 0
       0 0 1 0 0]; %更大的十字形结构元
seE = [0 0 0
       1 1 1
       0 0 0]; % 垂直结构元
seF = [0 1 0
       0 1 0
       0 1 0]; % 水平结构元

% 显示原始图像和不同结构元腐蚀后的图像
figure;
subplot(2,3,1);
imshow(A);
title('原始图像');

subplot(2,3,2);
A2 = imerode(A, seB);
imshow(A2);
title('使用结构元B腐蚀后的图像');

subplot(2,3,3);
A3 = imerode(A, seC);
imshow(A3);
title('使用结构元C腐蚀后的图像');

subplot(2,3,4);
A4 = imerode(A, seD);
imshow(A4);
title('使用结构元D腐蚀后的图像');

subplot(2,3,5);
A5 = imerode(A, seE);
imshow(A5);
title('使用结构元E腐蚀后的图像');

subplot(2,3,6);
A6 = imerode(A, seF);
imshow(A6);
title('使用结构元F腐蚀后的图像');

