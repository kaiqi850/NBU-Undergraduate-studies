/*
在一般情况下，符号三角形的第一行有n个符号, 符号三角形问题要求对于给定的n， 计算有多少个不同的符号三角形，使其所含的“+”和“-”的个数相同。
在这道题当中，可以得到限制：== “+”，“-”数量相等，总数量为偶数
*/

#include<cstdio>
#include<iostream>
using namespace std;

int half;
int sum = 0; 
int count = 0; 
int p[100][100]; //1代表- ； 0代表+ ； count就是"-"的计数 


void Dfs(int t,int n){	//直到第一行中符号的排列我们就可以得到整个三角形的排列 
	if(t == n && count == half)
		{
			sum ++;
			return ; //得到一个答案，向上return 回溯 
		} 
		
		//如果还有位子，一个位子要尝试 + - 两种情况 
		for(int i = 0; i < 2; i++) 
		{
			p[0][t] = i;
			count += i; 	//进行"-"符号的计算 
			
			for(int j = 1; j <= t; j++)		//进行三角形的填充，一共有t行 
			{
				p[j][t-j] = p[j-1][t-j]^p[j-1][t-j+1];	//每增长一行，该列中符号数将会减一，由上一行得到下一行的符号 
				count += p[j][t-j];		//计算"-"符号个数 
			}
			
			if(count <= half && (t+2)*(t+1)/2 - count <= half)//当前图形中+ -都没超过一半
			{
				Dfs(t + 1,n); 
			} 
			
			//还原本次，考虑下一个符号
			for( int j = 1; j <= t; j++)
			{
				count -= p[j][t-j];
			} 
			count -= i;
		}
}

int main()
{
	int n;
	cin>>n;
	half = (n+1) * n / 4; // + 和 - 都不能超过half
	Dfs(0,n);
	cout<<sum<<endl;
	return 0;
}
	

