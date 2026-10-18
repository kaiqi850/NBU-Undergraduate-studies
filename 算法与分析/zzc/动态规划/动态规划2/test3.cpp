/*
第一行输入整数n，表示共有多少个红包，n<1000；
后面n行表示n个红包，每行有三个整数，分别表示红包掉落的位置、时间和价值。
小k接到的红包价值之和。
*/ 

#include<iostream>
using namespace std;

int dp[1001][12] = {0};	//建立一个表格，行数代表时间，列数代表位置 
int max(int a,int b){	//返回两个数中的较大值 
	return a>b? a:b;
}
int max_3(int a, int b,int c){	//返回三个数中的最大值 
	int max = (a>b)? a:b;
	return (max>c)? max:c;
}

int maxValue(int max_time){	//逆向求解，表示走动下一步中所能带来的收益 
	for(int i = max_time-1; i>=0; i--){	 
		for(int j=0; j<11; j++){
			if(j == 0){	//如果在最左侧格子，那么只能站在原地或者向右走 
				dp[i][j] = max(dp[i+1][j],dp[i+1][j+1]) + dp[i][j];
			}else if(j == 10){	//如果在最右侧格子，那么只能向左走或者呆在原地 
				dp[i][j] = max(dp[i+1][j-1],dp[i+1][j]) + dp[i][j];
			}else{	//其余则可选择向左走，向右走或者呆在原地 
				dp[i][j] = max_3(dp[i+1][j-1],dp[i+1][j],dp[i+1][j+1]) + dp[i][j];
			}
		}
	}
	return dp[0][5];
}

int main(){
	int n;
	int location, time, value;	//定义三个变量，分别代表位置、时间、价值 
	int max_time = -1;
	cin>>n;		//红包个数 
	for(int i=0; i<n; i++){
		cin>>location>>time>>value;
		dp[time][location] = value;		//依据红包时间和位置将价值存入对应dp数组位置中 
		max_time = max(max_time,time);
	}
	cout<<maxValue(max_time)<<endl;
	return 0;
}
