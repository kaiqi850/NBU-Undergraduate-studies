/*
第1行：整数n(1<=n<=1000)
第2-n+1行：每行若干整数，第i行有i-1个整数，空格分隔。
*/

#include<iostream>
using namespace std;
int n;
int nums[1001][1001]={0};	//原始数组，用来存储输入的数据 
int dp[1001][1001]={0};		//dp数组，用来存储输入的值 
int max(int a,int b){		//找大数 
	return (a>b)?a:b;
}
int main(){
	cin>>n;
	for(int i=1;i<=n;i++){
		for(int j=1;j<=i;j++){
			cin>>nums[i][j];
		}
	}
	
	for(int j=1; j<=n; j++){	//初始化最后一行dp数组 
		dp[n][j] = nums[n][j];
	}
	for(int i = n-1; i>=1; i--){	//从最后一行开始逆向计算 
		for(int j=1; j<=i; j++){	 	//更新每一行的dp数组值 
			dp[i][j] = nums[i][j] + max(dp[i+1][j],dp[i+1][j+1]);
		}
	}
	cout<<dp[1][1]<<endl;	//输出答案 
	return 0;
}



