clc;
clear;

% 1. 读取原始图像
A = imread('Fingerprint.tif');

% 2. 转灰度（如果是彩色图像）
if size(A, 3) == 3
    A_gray = rgb2gray(A);
else
    A_gray = A;
end

% 3. 判断是否已经是逻辑类型，避免重复二值化
if ~islogical(A_gray)
    BW = imbinarize(A_gray);
else
    BW = A_gray;
end

% 4. 去除小噪声
BW_clean = bwareaopen(BW, 30);

% 5. 闭操作连接断裂
se = strel('disk', 2);
BW_closed = imclose(BW_clean, se);

% 6. 再次去噪
BW_final = bwareaopen(BW_closed, 30);

% 7. 提取骨架
BW_skel = bwmorph(BW_final, 'skel', Inf);

% 8. 显示
figure;
subplot(2, 3, 1); imshow(A); title('原始指纹图像');
subplot(2, 3, 2); imshow(BW); title('二值化图像');
subplot(2, 3, 3); imshow(BW_clean); title('去噪图像');
subplot(2, 3, 4); imshow(BW_closed); title('闭操作后图像');
subplot(2, 3, 5); imshow(BW_final); title('最终处理图像');
subplot(2, 3, 6); imshow(BW_skel); title('骨架提取图像');
