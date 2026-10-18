/*
将一个正整数N拆成若干个正整数的和。看谁拆的多谁就赢。为了赢得比赛，CX就向你求助一个整数的所有拆分方法。
输入N（ 1 <= N <= 50 ）。
对于N的拆分方法，请以字典序排列（数字越大越排前面）。每一种拆分之间以一个空格分开。
采用dfs深度优先算法 
*/

#include<iostream>
using namespace std;

int n;	//输入的数字 
int nums[50] = {0};	//用来各个数字 
int size;	//表示 

//深度优先算法，cur为当前需要分解的数，sum为已经分解的数，last为上一个加数 
void dfs(int cur,int sum, int last){
//	找到了一个解决方案 
	if(cur == 0 & sum == n){
		for(int i = 0; i < size-1; i++){
			cout<<nums[i]<<" ";
		}
		cout<<nums[size-1]<<endl;
	}
	else{
		//从大到小枚举所有的加数 
		for(int i = cur ; i >= 1; i--){
			//判断新的加数比上一个加数要小，并且综合小于n 
			if(i <= last & i + sum <= n){
				nums[size] = i; 
				size++;
				dfs(cur-i,sum+i,i);	// 递归继续分解剩余部分 
				size--; //进行回溯，撤销当前部分 
			}
		}
	}
}

int main(){
	while(cin>>n){
		size = 0;
		dfs(n,0,n);
	}
	return 0;
}
