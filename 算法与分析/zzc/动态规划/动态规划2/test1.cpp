/*
给定两个字符串，求解这两个字符串的最长非连续（允许连续或非连续）的公共子序列的长度（Longest Common Sequence）。
*/ 
#include<iostream>
#include<string>
#include<cstring>
using namespace std;
int getLCS(string str1,string str2){
	int m = str1.length() + 1;
	int n = str2.length() + 1;
	int length[m][n];	//开辟存储矩阵 
	for(int i = 0; i<m;i++)	//初始化矩阵第一行的数字为0 
		length[i][0] = 0;
	for(int j=0; j<n; j++)	//初始化矩阵第一列为0 
		length[0][j] = 0;
	for(int i=1; i<m; i++){		//从第1个字符串查找至最后一个 
		for(int j=1; j<n; j++){		 
			if(str1[i-1] == str2[j-1]){	//假若两个字符串中相等则更新矩阵的值为左上角的值+1 
				length[i][j] = length[i-1][j-1]+1;	
			}
			else if(length[i][j-1]>length[i-1][j]){	//若两个字符串中字符不等，则取二者中较大的值 
				length[i][j] = length[i][j-1];
			}
			else{
				length[i][j] = length[i-1][j];
			}
		}
	}
	
	return length[m-1][n-1];	//返回结果 
}
int main(){
	string str1;
	string str2;
	cin>>str1;
	cin>>str2;
	cout<<getLCS(str1,str2)<<endl;
	return 0;
}
