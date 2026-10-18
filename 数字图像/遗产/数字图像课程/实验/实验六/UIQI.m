function [uiqi] = UIQI(sta,fused)

sta=double(sta);
fused=double(fused);
[M,N,bs1] = size(sta);
[m,n,bs2] = size(fused);

assert(M == m && N == n,'图像行列数应相等');
assert(bs1 == bs2,'图像波段数应相等');
uiqi = zeros(1,bs1);

for k = 1 : bs1
    A = single(sta(:,:,k));
    B = fused(:,:,k);
    cov_matrix = cov(A,B);
    %cov_AB = abs(cov_matrix(3));
    cov_AB = abs(cov_matrix(3));

    ma = mean2(A); mb = mean2(B);
    std_A = std2(A); std_B = std2(B);

    uiqi(k) = (4*cov_AB * ma * mb) / ( (std_A*std_A + std_B*std_B) * (ma * ma + mb*mb) );
end
% uiqi(bs1+1) = sum(uiqi) / bs1;

