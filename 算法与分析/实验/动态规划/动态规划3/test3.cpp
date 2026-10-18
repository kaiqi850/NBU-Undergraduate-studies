#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<int> T(n); 
    vector<int> R(n - 1);	
    vector<int> dp(n + 1, 0);	

    for (int i = 0; i < n; i++) {	 
        cin >> T[i];
    }
    for (int i = 0; i < n - 1; i++) {
        cin >> R[i];
    }
    dp[1] = T[0];	 
    for (int i = 2; i <= n; i++) {	
        dp[i] = min(dp[i - 1] + T[i - 1], dp[i - 2] + R[i - 2]);
    }

    cout << dp[n] << endl;

    return 0;
}
