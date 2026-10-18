/*
在一般情况下，符号三角形的第一行有n个符号, 符号三角形问题要求对于给定的n， 计算有多少个不同的符号三角形，使其所含的“+”和“-”的个数相同。
在这道题当中，可以得到限制：== “+”，“-”数量相等，总数量为偶数
*/
/*
#include<cstdio>
#include<iostream>
using namespace std;

int half;
int sum = 0; 
int count = 0; 
int p[100][100]; 


void Dfs(int t,int n){	 
	if(t == n && count == half)
		{
			sum ++;
			return ;  
		} 
		
		 
		for(int i = 0; i < 2; i++) 
		{
			p[0][t] = i;
			count += i; 	
			
			for(int j = 1; j <= t; j++)	
			{
				p[j][t-j] = p[j-1][t-j]^p[j-1][t-j+1];	 
				count += p[j][t-j];		
			}
			
			if(count <= half && (t+2)*(t+1)/2 - count <= half)
			{
				Dfs(t + 1,n); 
			} 
			
			
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
	half = (n+1) * n / 4; 
	Dfs(0,n);
	cout<<sum<<endl;
	return 0;
}*/
	
#include<bits/stdc++.h>
using namespace std;
int train[21][21];
int half = 0;
int count1 =0;
int sum = 0;
int n =0;

void traceback(int start,int end){
if (start == end) {
    if (count1 == half) sum++;
    return;             //原先把两个判断条件放一起了，导致函数无法正确返回而夺走了一段代码 
}
	for(int i = 0;i<2;i++){
		train[0][start] = i;
		count1 += i;
		for(int j = 1;j<=start;j++){
			train[j][start-j] = !(train[j-1][start-j] ^ train[j-1][start-j+1]);
			count1 += train[j][start-j];
		}
		if(count1 <= half && (start+1)*start/2-count1 <= half ){
			traceback(start+1,end);
		}
		for(int j = 1;j<= start;j++){
			count1 -= train[j][start-j];
			//train[j][start - j] = 0;
		}		
		count1-= i; 
		//train[0][start] = 0;
	}
	
}

int main(){
	cin>>n;
	if(n == 0){
		cout<<0<<endl;
		return 0;
	}
	if((n*(n+1))/2%2){
		cout<<0<<endl;	
	}
	else{
		half = (n+1)*n/4;
	    traceback(0,n);
	    cout<<sum<<endl;;
	}
}
























