#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<int> T(n); //建立一个T数组来表示单个人买票所需要耗费的时间 
    vector<int> R(n - 1);	//建立一个R数组来表示相邻两个人买票所需要耗费的时间 
    vector<int> dp(n + 1, 0);	//dp数组来存储各个子问题的最小值 
    //输入数据 

    for (int i = 0; i < n; i++) {	 
        cin >> T[i];
    }
    for (int i = 0; i < n - 1; i++) {
        cin >> R[i];
    }
    //初始化 
    dp[1] = T[0];	 
    for (int i = 2; i <= n; i++) {	//状态转移方程，当前dp数组的最小值为前一个子问题的最小值加上当前单人买票时间；或者是前两个自问题的最小值加上钱一个人的两人买票时间 
        dp[i] = min(dp[i - 1] + T[i - 1], dp[i - 2] + R[i - 2]);
    }

    cout << dp[n] << endl;

    return 0;
}
