/*
设有n=2^k个运动员要进行网球循环赛。现要设计一个满足以下要求的比赛日程表：

(1)每个选手必须与其他n-1个选手各赛一次；

(2)每个选手一天只能参赛一次；

(3)循环赛在n-1天内结束。

整数k；k<=5。
*/

#include<iostream>
#include<cmath>
using namespace std;
int table[33][33] = {0};

void Schedule(int n, int k){

	for(int i = 1; i <= n; i++){
		//初始化表格第一行 
		table[1][i] = i;
	}
	
	int m = 1;
	
	for(int s = 1; s <= k; s++){	//s是一个循环变量表示当前位于第几层大循环 
		
		n = n/2;
		
		for(int t = 1; t <= n; t++){   //t表示位于第几层子循环 
				
			for(int i = 1 + m; i <= 2*m; i++){ //i表示当前选手的编号 
				 
				for(int j = 1 + m; j <= 2*m; j++){   //j表示第几天 
				 
					//起始值为右下角正方形的起始坐标	
					table[i][j + (t-1)*m*2] = table[i - m][j + (t-1)*m*2 - m];  //表示每个内层正方形右下角中的值等于左上角中的值 
					table[i][j + (t-1)*m*2 - m] = table[i - m][j + (t-1)*m*2];  //表示左下角正方形的值等于右上角正方形中的值 
				}
			}	
		}
		m *= 2;		//m是一个变量，表示每个内循环的正方形的一半 
	}
}

int main(){
	int k,n;
	cin>>k;		//输入阶数 
	n = pow(2,k);	//得到大正方形的边长 
	Schedule(n,k);
	for(int i = 1; i <= n; i++){	//输出 
		
		for(int j = 1; j < n; j++){
			
			cout << table[i][j] << " ";			
		}
		cout << table[i][n]<<endl;
	}
	return 0;
}
