% 读取灰度图像
I = imread('Evaluation_Reference.tif');
if size(I,3) == 3
    I = rgb2gray(I);
end

% 展平图像像素为一维数据
data = I(:);

% 获取唯一灰度值及其概率分布
symbols = unique(data);
counts = histc(data, symbols);
prob = counts / numel(data);

% 构建霍夫曼字典
dict = huffmandict(symbols, prob);

% 编码
encoded = huffmanenco(data, dict);

% 解码验证
decoded = huffmandeco(encoded, dict);
assert(isequal(data, decoded), '解码图像与原图像不一致');

% 计算原始和编码后的 bit 数
orig_bits = numel(data) * 8;            % 每个像素8位
encoded_bits = numel(encoded);          % 编码后的总位数
compression_ratio = orig_bits / encoded_bits;

% 输出结果
fprintf('原始数据大小：%d bits\n', orig_bits);
fprintf('编码后数据大小：%d bits\n', encoded_bits);
fprintf('压缩比：%.2f\n', compression_ratio);
