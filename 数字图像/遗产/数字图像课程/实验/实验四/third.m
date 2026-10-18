clc;        % 清除命令窗口的内容
close all;  % 关闭所有的Figure窗口
clear all;  % 清除工作空间的所有变量

%% 实现理想低通滤波器，见函数 ILPF_hanshu()。
%% 实现理想高通滤波器，见函数 IHPF_hanshu()。

A = imread('image3.tif'); % 请确保图像文件存在于此路径
[m, n] = size(A);
A = im2double(A); % 将图像转换为双精度型以便进行频域操作

F = fft2(A, 2*m, 2*n); % 扩展图像以避免边缘效应
F1 = fftshift(F); % 将零频率分量移动到频谱中心

figure;
subplot(2,3,1);
imshow(A);
title('原图像');

%% 对图像应用不同截止频率的理想低通和高通滤波器
D0_values = [10, 30, 60, 160, 460];
% 创建并激活两个窗口
figure(1); % 低通滤波结果窗口
hold on; % 保持当前图像，以便后续添加子图

figure(1);
subplot(2,3,1);
imshow(A);
title('原图像');

figure(2); % 高通滤波结果窗口
hold on; % 保持当前图像，以便后续添加子图

figure(2);
subplot(2,3,1);
imshow(A);
title('原图像');

for i = 1:length(D0_values)
    D0 = D0_values(i);
    
    % 理想低通滤波器
    H_ILPF = ILPF_hanshu(A, D0); % 获取理想低通滤波器
    G_ILPF = F1.*H_ILPF; % 应用低通滤波器
    F2_ILPF = ifftshift(G_ILPF); % 将零频率分量移回原位
    output_ILPF = ifft2(F2_ILPF); % 反傅里叶变换
    output_ILPF = output_ILPF(1:size(A, 1), 1:size(A, 2)); % 裁剪图像到原始大小
    
    % 理想高通滤波器
    H_IHPF = IHPF_hanshu(A, D0); % 获取理想高通滤波器
    G_IHPF = F1.*H_IHPF; % 应用高通滤波器
    F2_IHPF = ifftshift(G_IHPF); % 将零频率分量移回原位
    output_IHPF = ifft2(F2_IHPF); % 反傅里叶变换
    output_IHPF = output_IHPF(1:size(A, 1), 1:size(A, 2)); % 裁剪图像到原始大小
    
    % 显示低通滤波结果
    figure(1);
    subplot(2,3,i+1);
    imshow(real(output_ILPF));
    title(['ILPF 截止频率 D0 = ' num2str(D0)]);
    
    % 显示高通滤波结果
    figure(2);
    subplot(2,3,i+1);
    imshow(real(output_IHPF));
    title(['IHPF 截止频率 D0 = ' num2str(D0)]);
end
% 结束循环后，关闭保持状态
figure(1);
hold off;

figure(2);
hold off;
%% 理想低通滤波器函数
function H = ILPF_hanshu(img, D0)
    [m, n] = size(img);
    P = 2*m;
    Q = 2*n;
    H = zeros(P, Q);
    
    for u = 1:P
        for v = 1:Q
            D = sqrt((u-m)^2 + (v-n)^2); % 计算到中心的距离
            if D <= D0
                H(u, v) = 1; % 如果距离小于截止频率，则通过
            else
                H(u, v) = 0; % 否则阻止
            end
        end
    end
end

%% 理想高通滤波器函数
function H = IHPF_hanshu(img, D0)
    [m, n] = size(img);
    P = 2*m;
    Q = 2*n;
    H = zeros(P, Q);
    
    for u = 1:P
        for v = 1:Q
            D = sqrt((u-m)^2 + (v-n)^2); % 计算到中心的距离
            if D > D0
                H(u, v) = 1; % 如果距离大于截止频率，则通过
            else
                H(u, v) = 0; % 否则阻止
            end
        end
    end
end
