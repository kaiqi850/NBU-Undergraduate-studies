%% 第五章 图像复原

%% 噪声模型
clc
clear

r = imnoise2('gaussian',100000,1,0,1);
bins = 100;
hist(r,bins)
title('gaussian')

r = imnoise2('uniform',100000,1,0,1);
bins = 100;
figure,hist(r,bins)
title('uniform')

r = imnoise2('salt & pepper',1000,1,0.1,0.27);
bins = 100;
figure,hist(r,bins)
title('salt & pepper')

r = imnoise2('rayleigh',100000,1,0,1);
bins = 100;
figure,hist(r,bins)
title('rayleigh')

r = imnoise2('exponential',100000,1);
bins = 100;
figure,hist(r,bins)
title('exponential')

r = imnoise2('erlang',100000,1);
bins = 100;
figure,hist(r,bins)
title('erlang')


%% imnoise3 
clc
clear
C = [0 64; 0 128; 32 32; 64 0; 128 0; -32 32];
[r,R,S] = imnoise3(512, 512, C);
imshow(r,[])
figure
imshow(S,[])
title('指定冲击的正弦噪声周期频谱')

%% spfilt 空间噪声滤波器
clc
clear
f = imread('image.tif');
imshow(f)
title('原始图像')

[M,N] = size(f);
R = imnoise2('salt & pepper',M,N,0.1,0);
c = find(R == 0);
gp = f;
gp(c) = 0;
imshow(gp)
title('被概率为0.1的胡椒噪声污染的图像')

R = imnoise2('salt & pepper',M,N,0,0.1);
c = find(R == 1);
gs = f;
gs(c) = 255;
imshow(gs)
title('被概率为0.1的盐粒噪声污染的图像')

fp = spfilt(gp,'chmean',3,3,1.5);
imshow(fp)
title('逆谐波均值滤波器滤波结果')

fs = spfilt(gs,'chmean',3,3,-1.5);
imshow(fs)
title('用阶为Q=-1.5逆谐波均值滤波器滤波的结果')

fpmax = spfilt(gp,'max',3,3);
imshow(fpmax)
title('用3*3最大滤波器对[被概率为0.1的胡椒噪声污染的图像]滤波的结果')

fsmin = spfilt(gs,'min',3,3);
imshow(fsmin)
title('最小滤波器滤波的结果')

%% 模糊噪声图像建模 fspecial imfilter pixeldup
clc
clear

f = imread('image.tif')

PSF = fspecial('motion',7,45);  % sum(PSF(:)) = 1
gb = imfilter(f,PSF,'circular');
imshow(gb)
title('使用 PSF = fspecial(motion,7,45) 模糊后的图像')

%% 使用 deconvwnr 函数复原模糊噪声图像
clc
clear

f = checkerboard(8);
 imshow(f)

PSF = fspecial('motion',7,45)
gb = imfilter(f,PSF,'circular');
% imshowMy(gb)

noise = imnoise(zeros(size(f)),'gaussian',0,0.001);
% imshowMy(noise,[])

g = gb + noise;
imshow(g,[])
title('模糊加噪声的图像')
% ***************

fr1 = deconvwnr(g,PSF);
imshow(fr1,[])
title('逆滤波结果')

Sn = abs(fft2(noise)).^2;
nA = sum(Sn(:))/prod(size(noise));
Sf = abs(fft2(f)).^2;
fA = sum(Sf(:))/prod(size(f));
R = nA/fA;

fr2 = deconvwnr(g,PSF,R);
imshow(fr2,[])
title('维纳滤波结果')

NCORR = fftshift(real(ifft(Sn)));
ICORR = fftshift(real(ifft(Sf)));
fr3 = deconvwnr(g,PSF,NCORR,ICORR);
imshow(fr3,[])
title('使用自相关函数的维纳滤波后的结果')

% imshowMy(pixeldup(fr3,8))
%% 当模糊但不含噪声时使用维纳滤波还原
clc
clear

f = checkerboard(8);
imshow(f)

PSF = fspecial('motion',7,45)
gb = imfilter(f,PSF,'circular');
imshow(gb)

% ***************
g = gb;
fr1 = deconvwnr(g,PSF);
imshow(fr1,[])