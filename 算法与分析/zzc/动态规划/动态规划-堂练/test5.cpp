/*
第一行输入珠子数量n，2<n<20
第二行输入n个珠子的头尾标记，相邻头尾相同的标记只输入一个，因此共n+1个标记值
最小的杀伤能量
*/
#include <bits/stdc++.h>
#include<algorithm>
using namespace std;
#define N 20 
int a[N + 1];
int dp[N + 1][N + 1] = { 0 };
int Solve(int* a,int n){		//dp[i][j]表示从位置i到位置j的矩阵连乘最小值 
	for (int r = 2;r <= n;r++) { //包含最小矩阵个数，子问题规模 
		for (int i = 0;i < n - r + 1;i++) {		//当前所在的行号 
			int j = i + r - 1;  // i,j表示当前考虑范围的起始终结位置
			dp[i][j] = dp[i][i] + dp[i + 1][j] + a[i] * a[i + 1] * a[j + 1]; // 赋初值，不分割 
			for (int k = i + 1;k < j;k++) {
				dp[i][j] = min(dp[i][j],(dp[i][k] + dp[k + 1][j] + a[i] * a[k + 1] * a[j + 1])); // 循环找到最佳分割点k
			}
		}
	}
	return dp[0][n - 1];
}
int main() {
	int n;
	cin >> n;
	for (int i = 0;i <= n;i++)
		cin >> a[i];
	cout <<Solve(a,n)<< endl;
	return 0;
}

