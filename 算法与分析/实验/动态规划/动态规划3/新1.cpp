#include <bits/stdc++.h>
using namespace std;

int Findmax(int n, int *V) {
    if (n == 1)    
        return V[0];
    if (n == 2)
        return max(V[0], V[1]);

    vector<int> dp(n); 
    dp[0] = V[0];
    dp[1] = max(V[0], V[1]);

    for (int i = 2; i < n; i++) {    
        dp[i] = max(dp[i-1], dp[i-2] + V[i]);
    }
    return dp[n-1];
}

int main() {
    int N;
    cin >> N;
    int V[10001]; 
    for (int i = 0; i < N; i++) {
        cin >> V[i];
    }
    cout << Findmax(N, V) << endl;
    return 0;
}

