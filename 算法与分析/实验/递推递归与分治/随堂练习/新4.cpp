#include <iostream>
using namespace std;

int calcu(int n) {
    int N[100][100] = {0}; // 这里假设 n 不超过 100
    N[0][0] = 1;
    
    for (int i = 1; i <= n; i++) {
        N[i][0] = N[i - 1][i - 1];
        for (int j = 1; j <= i; j++) {
            N[i][j] = N[i - 1][j - 1] + N[i][j - 1];
        }
    }
    return N[n][0];
}

int main() {
    int n;
    cin >> n;

    int result = calcu(n);
    cout << result << endl;

    return 0;
}

