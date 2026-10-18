clc;
clear;

% 读取图像（假设图像均为灰度图或单通道图像）
ref = imread('Evaluation_Reference.tif');
cmp = imread('Evaluation_ToBeCompare.tif');

% 转为双精度
ref = double(ref);
cmp = double(cmp);

% 确保图像尺寸相同
if ~isequal(size(ref), size(cmp))
    error('参考图像与待比较图像尺寸不匹配');
end

% 计算RMSE
rmse = sqrt(mean((ref(:) - cmp(:)).^2));

% 计算PSNR
max_pixel = 255;  % 假设8位图像
psnr_val = 10 * log10( (max_pixel^2) / (rmse^2) );

% 输出结果
fprintf('RMSE = %.4f\n', rmse);
fprintf('PSNR = %.4f dB\n', psnr_val);

% 可视化（可选）
figure;
subplot(1,2,1), imshow(uint8(ref)), title('参考图像');
subplot(1,2,2), imshow(uint8(cmp)), title('待评价图像');
