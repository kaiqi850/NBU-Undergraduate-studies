#include<iostream>
using namespace std;

int n;	//输入的数字 
int nums[50] = {0};	//用来各个数字 
int size1=0;	//表示 

void dfs(int cur,int sum,int last){
	if(cur == 0){
		for(int i=0;i<size1-1;i++){
			cout<<nums[i]<<" ";
		}
		cout<<nums[size1-1]<<endl;
	}
	else {
		for(int i = cur;i>=1;i--){
			if(i<=last&&i+sum<=n){
				nums[size1]=i;
				size1++;
				dfs(cur-i,sum+i,i);
				size1--;
			}
		}
	}
} 

int main(){
	while(cin>>n){
		size1 = 0;
		dfs(n,0,n);
	}}

