function [rmse] = RMSE(sta,fused)
mse = mean((sta(:) - fused(:)).^2);
rmse = sqrt(mse);