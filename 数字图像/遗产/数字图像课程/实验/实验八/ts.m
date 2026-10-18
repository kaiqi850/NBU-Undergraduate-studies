clc
clear
figure;
f = imread('image2.tif');
subplot(121)
imshow(f)
title('原始图像')
imhist(f)

T = 0.5*(double(min(f(:))) + double(max(f(:))));
done = false;
while ~done
    g = f>=T;
    Tnext = 0.5*(mean(f(g)) + mean(f(~g)));
    done = abs(T - Tnext) < 0.5;
    T = Tnext;
end
T
g = f<=T;
subplot(122)
imshow(g)
title('使用迭代方法得到的阈值处理后的图像')