function [rmse] = RMSE(sta,fused)

mse = MSE(sta,fused);
rmse = sqrt(mse);

