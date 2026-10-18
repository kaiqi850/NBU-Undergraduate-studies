clear
clc
%% 二维中值滤波
I = imread('2.jpg');  % 读入图像
I = rgb2gray(I);
I=im2double(I);
j=imnoise(I, 'salt & pepper', 0.05);%添加椒盐噪声
k=medfilt2(j, [3, 3]);  %二维中值滤波
figure;
subplot(231);  imshow(I);title('原始图像');
subplot(232);  imshow(j);title('含有噪声的图像');
subplot(233);  imshow(k);title('中值滤波结果');
%% 二维排序滤波
domain=[0 1 1 0; 1 1 1 1; 1 1 1 1; 0 1 1 0];%窗口模板
k=ordfilt2(j, 6, domain);  %顺序滤波
subplot(234);  imshow(k);title('顺序滤波结果');
%% 最大值和最小值滤波对图像进行复原
k=ordfilt2(k, 1, ones(4,4));  %最大值滤波
m=ordfilt2(I, 9, ones(3));    %最小值滤波
subplot(235);  imshow(k); title('最大值滤波');%显示最大值滤波后的结果
subplot(236);  imshow(m); title('最小值滤波');%显示最小值滤波后的结果
%% 自适应滤波
J=imnoise(I, 'gaussian', 0, 0.03);%添加噪声
[K, noise]=wiener2(J, [5, 5]);%自适应滤波
figure;
subplot(121);  imshow(J);title('含有噪声的图像');%显示含有噪声的图像
subplot(122);  imshow(K);title('自适应滤波');%显示滤波后的结果
%% 维纳滤波对含有噪声的运动模糊图像进行复原
LEN=21;        %参数设置
THETA=11;
PSF=fspecial('motion', LEN, THETA);    %产生PSF
J=imfilter(I, PSF, 'conv', 'circular');%运动模糊
noise_mean=0;
noise_var=0.0001;
K=imnoise(J, 'gaussian', noise_mean, noise_var); %添加高斯噪声
NSR1=0;
L1=deconvwnr(K, PSF, NSR1);  %维纳滤波复原
NSR2=noise_var/var(I(:));
L2=deconvwnr(K, PSF, NSR2);  %图像复原
figure;
subplot(131);  imshow(I); title('原始图像');%显示原始图像
subplot(132);  imshow(K); title('退化图像');%显示退化图像
subplot(133);  imshow(L2);title('维纳滤波复原'); %显示结果