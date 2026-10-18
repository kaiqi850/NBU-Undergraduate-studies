#include<bits/stdc++.h>
using namespace std;

int T,M;
int t[100] = {0},v[100] = {0};

int main(){
	cin >>T>>M;
	int dp[105][1005] = {0};
	
	for(int i = 1;i<=M;i++){
		cin>>t[i]>>v[i];
	}
	for(int i = 1;i<=M;i++){
		for(int j = T;j>=0;j--){
			if(j<t[i]){
				dp[i][j] = dp[i-1][j];
			}
			else{
			
			dp[i][j] = max(dp[i-1][j],dp[i-1][j-t[i]] + v[i]);}
		}
	}
	cout<<dp[M][T];
} 
