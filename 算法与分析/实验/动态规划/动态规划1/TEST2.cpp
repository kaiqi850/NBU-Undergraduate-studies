/*
第1行输入一个整数n<50；表示输入数组的大小

第2行输入n个数，中间用空格隔开
*//*
#include<iostream>
using namespace std;

int n;
int nums[51]={0};
int Opt = 0;

int FindMax(int a,int b){	//返回较大的数 
	return a>b? a:b;
}


int main(){
	int max;
	cin>>n;
	for(int i=0; i<n; i++){
		cin>>nums[i];
	}
	Opt = nums[0];	//局部最大值 
	max = nums[0];	//全局最大值 
	for (int i = 0; i < n; i++) {
		Opt = FindMax(nums[i],Opt+nums[i]);	//在现在的数字和局部最大值与现在的数字的和中取较大的数 
		
		if(max<Opt)	//存储全局最大值 
			max = Opt;
    }
    cout<<max<<endl;
	return 0;
}*/

#include<bits/stdc++.h>
using namespace std;

int nums[51] = {0};

int Max(int a,int b){
	return (a>b)?a:b;
}

int main(){
	int n;
	cin>>n;
	for(int i = 0 ; i<n ; i++){
		cin >> nums[i];
	}
	int opt = nums[0];
	int max = nums[0];
	for(int i = 1 ;i<n;i++){
		opt = Max(nums[i],nums[i]+opt);
		
		if(max<opt){
		max = opt;
	}
	}
	cout<<max<<endl;
	return 0;
}





