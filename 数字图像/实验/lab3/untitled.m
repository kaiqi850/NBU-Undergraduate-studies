clc; clear; close all;

%% ================== 原始图像读取 ==================
I = imread('3/lena.tif');
if size(I, 3) == 3
    I = rgb2gray(I);
end
figure, imshow(I); title('原始图像');

%% ================== Sobel锐化 ==================
% Sobel 梯度边缘检测
sobel_x = fspecial('sobel');
sobel_y = sobel_x';

Ix = imfilter(double(I), sobel_x);
Iy = imfilter(double(I), sobel_y);
I_sobel = uint8(sqrt(Ix.^2 + Iy.^2));  % Sobel 边缘图像

%% ================== Laplacian锐化 ==================
% 拉普拉斯算子锐化
lap = fspecial('laplacian', 0.2);
I_lap = imfilter(double(I), lap);
I_lapsharp = uint8(double(I) - I_lap);  % 原图减去拉普拉斯算子结果锐化

%% ================== 显示锐化结果 ==================
figure;
subplot(1,3,1), imshow(I), title('原始图像');
subplot(1,3,2), imshow(I_sobel), title('Sobel 锐化');
subplot(1,3,3), imshow(I_lapsharp), title('Laplacian 锐化');
