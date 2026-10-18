clear all;
clc;

l = imread('house.jpg');         % 读取图像
l = im2double(l);                % 转为 double 类型

M = 2 * size(l, 1);
N = 2 * size(l, 2);

u = -M/2 : (M/2 - 1);
v = -N/2 : (N/2 - 1);

[U, V] = meshgrid(u, v);         % 创建二维频率网格
D = sqrt(U.^2 + V.^2);           % 计算频率距离

D0 = 70;                        % 截止频率
n = 2;                         % 巴特沃斯滤波器阶数

H = 1 ./ (1 + (D0 ./ D).^(2*n));  % 巴特沃斯高通滤波器传递函数

J = fftshift(fft2(l, size(H,1), size(H,2)));  % 傅里叶变换并中心化
K = J .* H;                                     % 频域滤波（逐元素相乘）
L = ifft2(ifftshift(K));                        % 逆变换恢复图像

L = L(1:size(l,1), 1:size(l,2));                % 截取原图大小

% 显示原图和锐化后的图像
figure;
subplot(1,2,1);
imshow(l);
title('原始图像');

subplot(1,2,2);
imshow(L);
title('巴特沃斯高通滤波锐化图像');
