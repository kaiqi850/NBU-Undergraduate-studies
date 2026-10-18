% 加载两张图片
img1 = imread('Evaluation_Reference.tif');
img2 = imread('Evaluation_ToBeCompare.tif');

% 如果图片是彩色的，转换为灰度图像
if size(img1, 3) == 3
    img1 = rgb2gray(img1);
end
if size(img2, 3) == 3
    img2 = rgb2gray(img2);
end

% 调用 SSIM 函数
[mssim] = ssim(img1, img2);

% 调用 CC 函数
cc_values = CC(img1, img2);

% 调用 PSNR 函数
psnr_value = PSNR(double(img1), double(img2), size(img1, 1), size(img1, 2));

% 调用 RMSE 函数
rmse_value = RMSE(double(img1), double(img2));

% 调用 UIQI 函数
uiqi_values = UIQI(img1, img2);

% 显示结果
disp('SSIM: ');
disp(mssim);
disp('CC: ');
disp(cc_values);
disp('PSNR: ');
disp(psnr_value);
disp('RMSE: ');
disp(rmse_value);
disp('UIQI: ');
disp(uiqi_values);