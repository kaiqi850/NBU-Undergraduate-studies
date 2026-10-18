/*
第一行一个整数N<=100，商店数。

第二行N个整数，每个商店的价值。
*/
#include<iostream>
using namespace std;

int max(int a,int b){	//返回较大的数 
	return a>b? a:b;
}

int Findmax(int n,int *dp){	//找出最大值 
	if(n == 1)	// 商家数为1时，直接返回 
		return dp[0];
	if(n == 2)	//商家数为2时，返回较大值 
		return max(dp[0],dp[1]);
	for(int i=2; i<n; i++){	//当商家数大于等于二时，进行选择并更新dp数组 
		dp[i] = max(dp[i-1],dp[i-2]+dp[i]);
	}
	return dp[n-1];
}

int main(){
	int N;
	int V[101];
	cin>>N;
	for(int i=0; i<N; i++){
		cin>>V[i];
	}
	cout<<Findmax(N,V)<<endl;
	return 0;
}
