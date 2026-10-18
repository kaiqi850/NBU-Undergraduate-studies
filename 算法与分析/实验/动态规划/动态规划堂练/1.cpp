/*#include<bits/stdc++.h>
using namespace std;

string A,B;
int k;


int main(){
	getline(cin,A);
	getline(cin,B);
	cin>>k;
	int len = B.length();
	int dp[len] = {0};
	for(int i =0;i<=B.length()-A.length();i++){
		
	}
} */


#include <bits/stdc++.h>
using namespace std;

int k;

int dis(char a, char b) {
    if (a == ' ' && b == ' ') return 0;
    if (a == ' ' || b == ' ') return k;
    return abs(a - b);
}

int main() {
    string A, B;
    getline(cin, A);
    getline(cin, B);
    cin >> k;

    int n = A.size(), m = B.size();
    vector<int> prev(m + 1, 0), curr(m + 1, 0);

    for (int j = 1; j <= m; ++j) {
        prev[j] = j * k;
    }

    for (int i = 1; i <= n; ++i) {
        curr[0] = i * k;  // dp[i][0]

        for (int j = 1; j <= m; ++j) {
            int cost1 = prev[j - 1] + dis(A[i - 1], B[j - 1]); 
            int cost2 = prev[j] + k;                           // A 插入空格
            int cost3 = curr[j - 1] + k;                       // B 插入空格
            curr[j] = min({cost1, cost2, cost3});
        }

        prev = curr; 
    }

    cout << prev[m] << endl;
    return 0;
}



