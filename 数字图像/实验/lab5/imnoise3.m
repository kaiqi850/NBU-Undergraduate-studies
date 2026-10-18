function [r,R,S] = imnoise3(M, N, C)
% imnoise3 生成带有指定冲击点的正弦噪声图像及频谱
% 输入：
%   M, N - 图像大小
%   C - 冲击点数组，每行一个冲击的频率坐标，如 [u v]
% 输出：
%   r - 空间域合成图像（噪声）
%   R - 频域幅度谱
%   S - 频域功率谱

% 初始化频域复数矩阵
F = zeros(M,N);

for k = 1:size(C,1)
    u = mod(C(k,1), M);
    v = mod(C(k,2), N);
    % 频域冲击: 两个共轭点对称赋值
    F(u+1,v+1) = 1;          % MATLAB索引从1开始
    F(M-u+1,N-v+1) = 1;
end

S = abs(F);          % 幅度谱
R = abs(F).^2;       % 功率谱

% 空间域合成信号（反傅里叶变换）
r = real(ifft2(F));

end
