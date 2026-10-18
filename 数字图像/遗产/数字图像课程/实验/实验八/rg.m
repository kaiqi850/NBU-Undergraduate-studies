% 清屏和清除工作空间
clc;
clear;

% 读取图像
f = imread('image2.tif');

% 显示原始图像
imshow(f);
title('原始图像');

% 显示原始图像的直方图
imhist(f);

% 初始化阈值T为图像最小和最大灰度值的平均值
T = 0.5 * (double(min(f(:))) + double(max(f(:))));
done = false;

% 迭代阈值分割
while ~done
    % 根据当前阈值T分割图像
    g = f >= T;
    % 计算新的阈值Tnext，为分割后的两部分灰度值的平均值
    Tnext = 0.5 * (mean(f(g)) + mean(f(~g)));
    % 如果阈值变化小于0.5，则停止迭代
    done = abs(T - Tnext) < 0.5;
    T = Tnext;
end

% 显示最终确定的阈值
T

% 根据最终阈值分割图像
g = f <= T;
imshow(g);
title('使用迭代方法得到的阈值处理后的图像');

% 清屏和清除工作空间
clc;
clear;

% 读取另一幅图像
f = imread('image1.tif');

% 显示原始图像
imshow(f);
title('原始图像');

% 区域生长算法
[g,NR,SI,TI] = regiongrow(f,100,10);
imshow(SI); % 显示包含种子点的图像
title('种子点图像');

imshow(TI); % 显示包含在经过连通性处理前通过阈值测试的像素
title('所有[经过种子点连通性处理前]通过阈值测试的像素');

% 显示区域生长后的结果
imshow(g);
title('所有通过阈值测试的像素在对种子点进行8连通性分析后的结果');


function [g, NR, SI, TI] = regiongrow(f, S, T)
%REGIONGROW Perform segmentation by region growing.
% [G, NR, SI, TI] = REGIONGROW(F, S, T). S can be an array (the
% same size as F) with a 1 at the coordinates of every seed point
% and 0s elsewhere. S can also be a single seed value. Similarly,
% T can be an array (the same size as F) containing a threshold
% value for each pixel in F. T can also be a scalar, in which case
% it becomes a global threshold. All values in S and T must be in
% the range [0, 1]
%
% G is the result of region growing, with each region labeled by a
% different integer, NR is the number of regions, SI is the final
% seed image used by the algorithm, and TI is the image consisting
% of the pixels in F that satisfied the threshold test, but before
% they were processed for connectivity.
f = tofloat(f);
% If S is a scalar, obtain the seed image.
if numel(S) == 1
SI = f == S;
S1 = S;
else
% S is an array. Eliminate duplicate, connected seed locations
% to reduce the number of loop executions in the following
% sections of code.
SI = bwmorph(S, 'shrink', Inf);
S1 = f(SI); % Array of seed values.
end
TI = false(size(f));
for K = 1:length(S1)
seedvalue = S1(K);
S = abs(f - seedvalue) <= T; % Re-use variable S.
TI = TI | S;
end
% Use function imreconstruct with SI as the marker image to
% obtain the regions corresponding to each seed in S. Function
% bwlabel assigns a different integer to each connected region.
[g, NR] = bwlabel(imreconstruct(SI, TI));
end

function [out, revertclass] = tofloat(in)
identity = @(x) x;
tosingle = @im2single;

table = {'uint8', tosingle, @im2uint8
    'uint16', tosingle, @im2uint16
    'int16', tosingle, @im2int16
    'logical', tosingle, @logical
    'double', identity, identity
    'single', identity, identity};

classIndex = find(strcmp(class(in), table(:, 1)));

if isempty(classIndex)
    error('Unsupported input image class.');
end

out = table{classIndex, 2}(in);

revertclass = table{classIndex, 3};
end
