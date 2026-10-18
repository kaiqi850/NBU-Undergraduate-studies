function f2 = changeclass(classname, f)
% changeclass 将数组 f 转换成 classname 类型
%
% classname - 目标数据类型字符，如 'double', 'uint8', 'int16' 等
% f - 输入数组
%
% 返回转换后的数组

switch classname
    case 'double'
        f2 = double(f);
    case 'single'
        f2 = single(f);
    case 'uint8'
        f2 = uint8(f);
    case 'uint16'
        f2 = uint16(f);
    case 'int16'
        f2 = int16(f);
    case 'logical'
        f2 = logical(f);
    otherwise
        error('不支持的数据类型转换');
end

end
