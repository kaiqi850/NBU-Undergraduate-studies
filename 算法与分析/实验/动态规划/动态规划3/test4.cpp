/*
输入数据有多组。多组数据的第一行以正整数n(0<n<100000),表示有n个蘑菇会出现在这条路上。
在接下来的n行中，每行有两个整数x,T(0<T<100000),表示在第T秒有一个蘑菇出现在x点上。
同一秒钟在同一个点上可能出现多个蘑菇。 
每一组输入数据对应一行输出。输出一个整数m，表示提莫队长最多可能踩到m个蘑菇。
提示：本题的输入数据量比较大，建议用scanf读入，用cin可能会超时。
*/ 
#include<bits/stdc++.h>
using namespace std;

int dp[100000+10][12] = {0};	//建立一个表格，行数代表时间，列数代表位置 

int max_3(int a, int b,int c){	//返回三个数中的最大值 
	return max(a,max(b,c));
}

long maxValue(int max_time){	//逆向求解，表示走动下一步中所能带来的收益 
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
	int location, time;	//定义两个变量，分别表示蘑菇产生的位置与时间 
	int max_time = -1;	//表示所有蘑菇中最晚产生的蘑菇的时间 
	while(cin>>n){
		for(int i=0; i<n; i++){
			cin>> location >> time;	//接下来在每一行中输入蘑菇的位置和时间 
			dp[time][location] = dp[time][location]+1;		//初始化dp数组，若某时间某位置存在该蘑菇，则dp数组的值加一 
			max_time = max(max_time,time);	//更新max_time 
	}
	cout<<maxValue(max_time)<<endl;
	memset(dp, 0, sizeof(dp));
	}
	
	return 0;
}

