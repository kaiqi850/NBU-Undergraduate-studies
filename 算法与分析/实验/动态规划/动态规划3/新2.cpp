#include <bits/stdc++.h>
using namespace std;

int main(){
    string A, B;
    cin >> A >> B;
    int n = A.size();
    
    vector<vector<long long>> dp(n+1, vector<long long>(n+1, 0));
    
    for (int j = n - 1; j >= 0; j--) {
        for (int left = j; left >= 0; left--) {
            int right = n - (j - left) - 1;
            long long option1 = (long long)A[left] * B[j] + dp[left+1][j+1];
            long long option2 = (long long)A[right] * B[j] + dp[left][j+1];
            dp[left][j] = max(option1, option2);
        }
    }
    
    cout << dp[0][0] << endl;
    return 0;
}

