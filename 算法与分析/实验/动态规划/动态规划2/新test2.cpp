#include <bits/stdc++.h>
using namespace std;

int getLCS(string str1, string str2) {
    int m = str1.length(), n = str2.length();

    vector<int> prev(n + 1, 0), curr(n + 1, 0);

    for (int i = 1; i <= m; i++) {
        for (int j = 1; j <= n; j++) {
            if (str1[i - 1] == str2[j - 1]) {
                curr[j] = prev[j - 1] + 1;
            } else {
                curr[j] = max(prev[j], curr[j - 1]);
            }
        }
        swap(prev, curr); 
    }
    return prev[n]; 
}

int main() {
    string str1, str2;
    cin >> str1 >> str2;
    cout << getLCS(str1, str2) << endl;
    return 0;
}

