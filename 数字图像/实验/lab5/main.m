% 生成棋盘格图像
I = checkerboard(8);

% 生成高斯模糊PSF
PSF = fspecial('gaussian', 7, 10);

% 噪声方差
V = 0.0001;

% 模糊图像并添加高斯噪声
BlurredNoisy = imnoise(imfilter(I, PSF), 'gaussian', 0, V);

% 定义权重矩阵，中间部分为1，边缘为0
WT = zeros(size(I));
WT(5:end-4, 5:end-4) = 1;

% 不带参数的Lucy-Richardson复原
J1 = deconvlucy(BlurredNoisy, PSF);

% 迭代20次，带噪声标准差参数的Lucy-Richardson复原
J2 = deconvlucy(BlurredNoisy, PSF, 20, sqrt(V));

% 迭代20次，带噪声标准差和权重矩阵的Lucy-Richardson复原
J3 = deconvlucy(BlurredNoisy, PSF, 20, sqrt(V), WT);

% 显示4个图像进行对比
figure;
subplot(2,2,1);
imshow(BlurredNoisy);
title('A. 模糊且带噪声图像');

subplot(2,2,2);
imshow(J1);
title('B. deconvlucy(无参数)');

subplot(2,2,3);
imshow(J2);
title('C. deconvlucy(20次迭代 + 噪声参数)');

subplot(2,2,4);
imshow(J3);
title('D. deconvlucy(带权重矩阵)');
