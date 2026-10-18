/*
输入2行；

第一行一个整数n，表示有n个整数的序列要输入，n<1000;

第二行共有n个整数。

输出最长的不下降子序列，只需选数字顺位靠后的序列从大到小输出。
*/
#include<iostream>
#include<algorithm>
using namespace std;
int a[1010];  // 输入的序列
int dp[1010]; // dp[i]表示第i+1个数到最后一个数的最长非减序列长度 
int index[1010];  // 记录最长非减序列的索引 
                  // index[i]表示序列中索引i的数字的下一个数字的索引           
int n;

void findmax(){
	//找到每个数字到终点的最长非减序长度	
	for(int i=n-2; i>=0; i--){
		int length_i = 0;
		for(int j=i+1; j<n; j++){
			if(a[j]>=a[i] && dp[j]>=length_i){  // 找到数字a[j],满足非递减且到末尾长度最大，如果有多个，选择靠后的 
				length_i = dp[j];
				index[i] = j;  // 最长序列中i的下一个数字的位置 
			}
		}
		if(length_i)
			dp[i] = length_i + 1;
	}
	
	int max_length = 0, p;
	for (int i = 0; i < n; ++i)
		if (dp[i] >= max_length){  // 找到数字a[i],其到末尾的非减序列最长，如有多个，选择靠后的 
			max_length = dp[i];
			p = i;
		}
	
	int result[max_length];  // 保存最长非减序列
	for(int i=0; i<max_length; i++){
		result[i] = a[p];
		p = index[p];
	} 
	
	cout<<max_length<<endl;
	for(int i=max_length-1; i>=0; i--)  // 从大到小输出 
	{
		if(i == 0)	// 最后一个输出不要空格 
			cout << result[i];
		else
			cout << result[i] << " ";
		
	}
	
} 

int main()
{
	// 输入数据 
	cin >> n;
	for(int i=0; i<n; i++)
		cin >> a[i];
		
	//  初始化
	for(int i=0; i<n; i++){
		dp[i] = 1;
		index[i] = 0;
	} 
	findmax();
 	cout<<endl;
	return 0;
}
 
