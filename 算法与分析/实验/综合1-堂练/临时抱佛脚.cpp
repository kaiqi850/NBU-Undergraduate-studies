#include <bits/stdc++.h>
using namespace std;

int main() {
    int N, M;
    cin >> N >> M;

    vector<vector<int>> score(N + 1, vector<int>(M + 1, 0)); 
    for (int i = 1; i <= N; i++) {
        for (int j = 1; j <= M; j++) {
            cin >> score[i][j];
        }
    }

    vector<int> dp(M + 1, 0);  

    for (int i = 1; i <= N; i++) {
        for (int j = M; j >= 0; j--) {
            for (int k = 1; k <= j; k++) {
                dp[j] = max(dp[j], dp[j - k] + score[i][k]);
            }
        }
    }

    cout << dp[M] << endl;
    return 0;
}

