clc; clear; close all;

% 读取图像并转换为灰度
I = imread('实验二图像/tree.jpg');
I_gray = rgb2gray(I); % 转换为灰度图
[M, N] = size(I_gray); % 获取图像尺寸

% 计算灰度直方图
histogram = zeros(256,1); % 0~255 共 256 级
for i = 1:M
    for j = 1:N
        pixel_value = I_gray(i,j) + 1; % MATLAB 索引从 1 开始
        histogram(pixel_value) = histogram(pixel_value) + 1;
    end
end

% 计算累积分布函数（CDF）
cdf = cumsum(histogram); % 计算累计直方图
cdf_norm = (cdf - min(cdf)) / (M*N - min(cdf)); % 归一化到 [0,1]
cdf_scaled = round(cdf_norm * 255); % 映射到 [0,255]

% 进行直方图均衡化
I_eq = I_gray; % 复制原始图像
for i = 1:M
    for j = 1:N
        I_eq(i,j) = cdf_scaled(I_gray(i,j) + 1);
    end
end

% 绘制原始图像及其直方图
figure;
subplot(2,2,1); imshow(I_gray); title('原始图像');
subplot(2,2,2); bar(0:255, histogram, 'k'); title('原始直方图');
xlim([0 255]); xlabel('灰度值'); ylabel('像素个数');

% 绘制均衡化后图像及其直方图
subplot(2,2,3); imshow(I_eq); title('均衡化后图像');

% 计算均衡化后的直方图
hist_eq = zeros(256,1);
for i = 1:M
    for j = 1:N
        pixel_value = I_eq(i,j) + 1;
        hist_eq(pixel_value) = hist_eq(pixel_value) + 1;
    end
end

subplot(2,2,4); bar(0:255, hist_eq, 'k'); title('均衡化后直方图');
xlim([0 255]); xlabel('灰度值'); ylabel('像素个数');
