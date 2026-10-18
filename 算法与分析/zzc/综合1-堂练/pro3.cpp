#include <algorithm>
#include <iostream>
#define AUTHOR "HEX9CF"
using namespace std;

const int N = 1e7 + 7;
// 采药时间，草药数目 
int T, M;
// 时间，价值
int t[N], v[N];
long long dp[N];

void map_generate() {
	cin >> T >> M;
	for (int i = 1; i <= M; i++) {
		cin >> t[i] >> v[i];
	}
}


int main() {
	map_generate();
	for (int i = 1; i <= M; i++) {
		for (int j = t[i]; j <= T; j++) {
			dp[j] = max(dp[j], dp[j - t[i]] + v[i]);
		}
	}
	cout << dp[T] << endl;
	return 0;
}

