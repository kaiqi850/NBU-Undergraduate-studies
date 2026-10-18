clc;
clear;
A = imread('Fingerprint.tif'); % 读取图像

% 定义结构元
structuringElement = strel('square', 3); % 3x3的方形结构元

% 执行膨胀操作
dilatedImage = imdilate(A, structuringElement);

% 执行腐蚀操作
erodedImage = imerode(A, structuringElement);

% 计算形态学梯度
morphologicalGradient = imabsdiff(dilatedImage, erodedImage);

% 显示原始图像和形态学梯度
figure;
subplot(2,2,1);
imshow(A);
title('原始图像');

subplot(2,2,2);
imshow(dilatedImage);
title('膨胀');

subplot(2,2,3);
imshow(erodedImage);
title('腐蚀');

subplot(2,2,4);
imshow(morphologicalGradient);
title('形态学梯度');
