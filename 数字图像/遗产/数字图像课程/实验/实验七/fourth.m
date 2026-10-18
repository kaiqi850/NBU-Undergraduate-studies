clc;
clear;
A = imread('Fingerprint.tif'); % 读取图像

% 定义结构元
structuringElement = strel('square', 3); % 3x3的方形结构元

% 执行开操作
openImage = imopen(A, structuringElement);

% 执行闭操作
closeImage = imclose(A, structuringElement);

% 将开操作与闭操作的结果相加
combinedImage = openImage + closeImage;

% 对相加的结果进行开操作
final1Image = imopen(combinedImage, structuringElement);

% 计算原始图像减去开操作结果的差值
difference = A - openImage;

% 计算最终结果：闭操作结果减去上述差值
final2Image = closeImage - difference;


% 显示原始图像、开操作、闭操作、相加的结果以及最终的开操作结果
figure;
subplot(2,3,1);
imshow(A);
title('原始图像');

subplot(2,3,2);
imshow(openImage);
title('开操作结果');

subplot(2,3,3);
imshow(closeImage);
title('闭操作结果');

subplot(2,3,4);
imshow(combinedImage);
title('开操作与闭操作相加的结果');

subplot(2,3,5);
imshow(final1Image);
title('对相加图片开操作');

subplot(2,3,6);
imshow(final2Image);
title('闭操作-（原始-开操作）');

