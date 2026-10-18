clc;
clear;
A = imread('image1.tif'); % 读取图像
seB = [0 1 0
       1 1 1
       0 1 0]; % 初始结构元
seC = [1 1 1
       1 1 1
       1 1 1];
seD = [0 0 1 0 0
       0 1 1 1 0
       1 1 1 1 1
       0 1 1 1 0
       0 0 1 0 0];
seE = [0 0 0
       1 1 1
       0 0 0];
seF = [0 1 0
       0 1 0
       0 1 0];

figure;
subplot(2,3,1);
imshow(A);
title('原始图像');

subplot(2,3,2);
A2=recursiveDilate(A,seB,3);
imshow(A2);
title('使用结构元B膨胀三次的图像');

subplot(2,3,3);
A3=recursiveDilate(A,seC,3);
imshow(A3);
title('使用结构元C膨胀三次的图像');

subplot(2,3,4);
A4=recursiveDilate(A,seD,3);
imshow(A4);
title('使用结构元D膨胀三次的图像');

subplot(2,3,5);
A5=recursiveDilate(A,seE,3);
imshow(A5);
title('使用结构元E膨胀三次的图像');

subplot(2,3,6);
A6=recursiveDilate(A,seF,3);
imshow(A6);
title('使用结构元F膨胀三次的图像');

function dilatedImage = recursiveDilate(image, structuringElement, numIterations)
% 递归地进行形态学膨胀操作
% image: 输入图像
% structuringElement: 结构元
% numIterations: 剩余的迭代次数
% dilatedImage: 膨胀后的图像

% 终止条件：如果剩余迭代次数为0，返回当前图像
if numIterations == 0
    dilatedImage = image;
    return;
end

% 进行一次膨胀操作
dilatedImage = imdilate(image, structuringElement);

% 递归调用，减少迭代次数
dilatedImage = recursiveDilate(dilatedImage, structuringElement, numIterations - 1);
end
