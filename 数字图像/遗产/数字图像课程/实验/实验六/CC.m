function [cc] = CC(sta,fused)

sta=double(sta);
fused=double(fused);
[M,N,bs1] = size(sta);
[m,n,bs2] = size(fused);

cc = zeros(1,bs1);
for i = 1 : bs1
    A = sta(:,:,i);B = fused(:,:,i);
    A=single(A);
    std_A = std2(A);
    std_B = std2(B);
    cov_matrix = cov(A,B);
    cov_AB = cov_matrix(3);
    cc(i) = abs(cov_AB / (std_A * std_B));
    %cc(i) = cov_AB / (std_A * std_B);
end
%   cc(bs1) = sum(cc) / bs1;
end
