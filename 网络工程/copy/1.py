import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import torch.utils.data as data
from torch.optim.lr_scheduler import ReduceLROnPlateau

# 文件路径
file_path = r"C:\Users\asus\Desktop\x\试卷卷卷子\网络工程\Intelligent-temperature-and-humidity-system\public\mqtt_data.xlsx"

# 从 Excel 文件中读取数据
df = pd.read_excel(file_path)

# 按 8:2 比例划分训练集和测试集
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# 拆分日期列，并添加 'hour', 'minute', 'second' 等列
def split_date_columns(df):
    df = df.copy()  # 避免 SettingWithCopyWarning
    df[['hour', 'minute', 'second']] = df['Timestamp'].str.split(':', expand=True)
    return df

train_df = split_date_columns(train_df)
test_df = split_date_columns(test_df)

# 使用温度和湿度作为特征
tr_timeseries = train_df[['Temperature', 'Humidity', 'hour', 'minute', 'second']].values.astype('float32')
te_timeseries = test_df[['Temperature', 'Humidity', 'hour', 'minute', 'second']].values.astype('float32')

# 合并训练和测试数据，用于标准化
new = pd.concat([train_df, test_df], axis=0).reset_index().drop('index', axis=1)
new_timeseries = new[['Temperature', 'Humidity', 'hour', 'minute', 'second']].values.astype('float32')

# MinMax标准化
scaler = MinMaxScaler()
tr_timeseries = scaler.fit_transform(tr_timeseries)
te_timeseries = scaler.transform(te_timeseries)

# 创建数据集，lookback为7
def create_dataset(dataset, lookback):
    X, y = [], []
    for i in range(len(dataset) - lookback):
        feature = dataset[i:i + lookback, :5]  # 只取前5列特征
        target = dataset[i + lookback, 0:2]  # 第0列是Temperature，第1列是Humidity
        X.append(feature)
        y.append(target)
    return torch.tensor(np.array(X), dtype=torch.float32), torch.tensor(np.array(y), dtype=torch.float32)

lookback = 7

# 创建训练和测试数据集
X_train, y_train = create_dataset(tr_timeseries, lookback)
X_test, y_test = create_dataset(te_timeseries, lookback)

# DataLoader
loader = data.DataLoader(data.TensorDataset(X_train, y_train),
                         batch_size=8, shuffle=True)

# 定义LSTM模型
class LSTMModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=5,  # 输入5个特征
                            num_layers=2,
                            hidden_size=128,
                            batch_first=True,
                            bidirectional=True)
        self.dropout = nn.Dropout(0.2)
        self.linear1 = nn.Linear(128 * 2, 64)
        self.linear2 = nn.Linear(64, 8)
        self.output_linear = nn.Linear(8, 2)  # 输出2个值：Temperature 和 Humidity

    def forward(self, x):
        x, _ = self.lstm(x)
        x = self.dropout(x)
        x = self.linear1(x)
        x = self.linear2(x)
        x = self.output_linear(x)
        return x

# 定义优化器、损失函数和学习率调度器
model = LSTMModel()
optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
loss_fn = nn.MSELoss()
scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5, verbose=True)

# 自定义早停类
class CustomEarlyStopping:
    def __init__(self, patience=20, delta=0, verbose=False):
        self.patience = patience
        self.delta = delta
        self.verbose = verbose
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.best_state = None

    def __call__(self, val_loss, model):
        score = -val_loss

        if self.best_score is None:
            self.best_score = score
            self.best_state = model.state_dict()
        elif score < self.best_score + self.delta:
            self.counter += 1
            if self.verbose:
                print(f'EarlyStopping counter: {self.counter} out of {self.patience}, score: {self.best_score}')
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.best_state = model.state_dict()
            self.counter = 0

early_stopping = CustomEarlyStopping(patience=15, verbose=True)

best_score = None
best_weights = None
best_train_preds = None
best_test_preds = None

n_epochs = 200

# 训练模型
for epoch in range(n_epochs):
    model.train()
    for X_batch, y_batch in loader:
        y_pred = model(X_batch)
        loss = loss_fn(y_pred[:, -1, :], y_batch)  # 取最后一个时间步的输出
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        y_pred_train = model(X_train)
        train_rmse = torch.sqrt(loss_fn(y_pred_train[:, -1, :], y_train))  # 取最后一个时间步的输出
        train_preds = y_pred_train.clone().detach().cpu().numpy()

        y_pred_test = model(X_test)
        test_rmse = torch.sqrt(loss_fn(y_pred_test[:, -1, :], y_test))  # 取最后一个时间步的输出
        test_preds = y_pred_test.clone().detach().cpu().numpy()

        # 更新学习率调度器
        scheduler.step(test_rmse)

        if best_score is None or test_rmse < best_score:
            best_score = test_rmse
            best_weights = model.state_dict()
            best_train_preds = train_preds
            best_test_preds = test_preds

        early_stopping(test_rmse, model)

        if early_stopping.early_stop:
            print("Early stopping")
            break

    if epoch % 10 == 0:
        print('*' * 10, 'Epoch: ', epoch, '\ train RMSE: ', train_rmse.item(), '\ test RMSE', test_rmse.item())

# 加载最佳模型权重
if best_weights is not None:
    model.load_state_dict(best_weights)

    # 使用最佳模型生成预测
    with torch.no_grad():
        y_pred_train = model(X_train).clone().detach().cpu().numpy()
        y_pred_test = model(X_test).clone().detach().cpu().numpy()

# 绘制预测结果
train_plot = np.ones_like(new_timeseries) * np.nan
train_plot[lookback: len(tr_timeseries)] = best_train_preds[:, -1, :]

test_plot = np.ones_like(new_timeseries) * np.nan
test_plot[len(tr_timeseries) + lookback:len(new_timeseries)] = best_test_preds[:, -1, :]

# 逆变换
train_predictions = scaler.inverse_transform(train_plot.reshape(-1, 2))
test_predictions = scaler.inverse_transform(test_plot.reshape(-1, 2))

print("训练和测试完成，预测结果已经逆变换。")
