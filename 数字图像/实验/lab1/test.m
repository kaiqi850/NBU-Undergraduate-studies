I = imread('1/moon.png');

I16 = uint16(I);  % 转换为 uint16
J = immultiply(I16, I16);  % 进行 uint16 乘法

% 归一化到 0-255 并转换回 uint8
J = uint8(mat2gray(J) * 255);

% 使用 imshowpair 进行对比
figure;
imshowpair(I, J, 'montage');
title('Original Image (Left) vs Multiplied Image (Right)');
