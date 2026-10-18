clc;        % 清除命令窗口的内容
close all;  % 关闭所有的Figure窗口
clear all;  % 清除工作空间的所有变量

A = imread('image3.tif'); % 请确保图像文件存在于此路径
if isempty(A)
    error('图像文件不存在，请检查路径');
end
[m, n] = size(A);
A = im2double(A); % 将图像转换为双精度型以便进行频域操作

F = fft2(A, 2*m, 2*n); % 扩展图像以避免边缘效应
F1 = fftshift(F); % 将零频率分量移动到频谱中心

D0 = 30; % 固定截止频率
N_values = [1, 2, 3, 4]; % 阶数设置

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


for j = 1:length(N_values)
    N = N_values(j);
    
    % 布特沃斯低通滤波器
    H_BLPF = BLPF_function(m, n, D0, N);
    G_BLPF = F1.*H_BLPF;
    F2_BLPF = ifftshift(G_BLPF);
    output_BLPF = ifft2(F2_BLPF);
    output_BLPF = output_BLPF(1:size(A, 1), 1:size(A, 2));
    
    % 布特沃斯高通滤波器
    H_BHPF = BHPF_function(m, n, D0, N);
    G_BHPF = F1.*H_BHPF;
    F2_BHPF = ifftshift(G_BHPF);
    output_BHPF = ifft2(F2_BHPF);
    output_BHPF = output_BHPF(1:size(A, 1), 1:size(A, 2));
    
    % 显示低通滤波结果
    figure(1);
    subplot(2, 3, j+1);
    imshow(real(output_BLPF));
    title(['BLPF 阶数 N = ' num2str(N)]);
    
    % 显示高通滤波结果
    figure(2);
    subplot(2, 3, j+1);
    imshow(real(output_BHPF));
    title(['BHPF 阶数 N = ' num2str(N)]);
end

% 结束循环后，关闭保持状态
figure(1);
hold off;

figure(2);
hold off;

% 布特沃斯低通滤波器函数
function H = BLPF_function(m, n, D0, N)
    P = 2*m;
    Q = 2*n;
    H = zeros(P, Q);
    for u = 1:P
        for v = 1:Q
            D = sqrt((u-m)^2 + (v-n)^2);
            H(u, v) = 1 / (1 + (D/D0)^(2*N));
        end
    end
end

% 布特沃斯高通滤波器函数
function H = BHPF_function(m, n, D0, N)
    P = 2*m;
    Q = 2*n;
    H = zeros(P, Q);
    for u = 1:P
        for v = 1:Q
            D = sqrt((u-m)^2 + (v-n)^2);
            H(u, v) = 1 / (1 + (D0/D)^(2*N));
        end
    end
end

