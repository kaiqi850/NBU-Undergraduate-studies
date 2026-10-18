#include <iostream>
#include <cstdlib>
#include <ctime>
#include <vector>

using namespace std;

struct SimulationResult {
    int players;
    int bankrupt_count;
    double bankrupt_rate;
};

SimulationResult gamble_simulation(int players, int initial_balance, int rounds) {
    vector<int> balances(players, initial_balance);
    
    // 使用当前时间作为随机数生成器的种子
    srand(time(0));

    for (int round = 0; round < rounds; ++round) {
        for (int i = 0; i < players; ++i) {
            if (balances[i] > 0) { // 如果该玩家还有钱
                int result = rand() % 2 + 1;  // 生成1或2的随机数
                if (result == 1) {
                    balances[i] -= 1;  // 庄家赢，买家输
                } else {
                    balances[i] += 1;  // 买家赢，庄家输
                }
            }
        }
    }
    
    int bankrupt_count = 0;
    for (int i = 0; i < players; ++i) {
        if (balances[i] <= 0) {
            bankrupt_count++;
        }
    }
    
    SimulationResult result;
    result.players = players;
    result.bankrupt_count = bankrupt_count;
    // 使用 static_cast 将破产人数转换为 double 类型，以确保精确的浮点数除法
    result.bankrupt_rate = static_cast<double>(bankrupt_count) / players * 100.0;

    return result;
}

int main() {
    int initial_balance = 100;     // 每人初始资金
    int rounds = 1200;             // 每人赌1200次
    int start_players = 1000;      // 开始的玩家数
    int end_players = 20000;       // 结束的玩家数
    int step = 1000;               // 步长

    for (int players = start_players; players <= end_players; players += step) {
        SimulationResult result = gamble_simulation(players, initial_balance, rounds);
        cout << "Players: " << result.players 
             << ", Bankrupt Count: " << result.bankrupt_count 
             << ", Bankrupt Rate: " << result.bankrupt_rate << "%" << endl;
    }

    return 0;
}

