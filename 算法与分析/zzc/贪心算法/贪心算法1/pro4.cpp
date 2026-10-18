/* 
设有n个正整数，将它们连接成一排，组成一个最大的多位整数。

*/
#include<iostream>
#include <algorithm>
#include <vector>
#include <string>
using namespace std;

bool Compare(string a, string b) {	//比较两个连接字符串大小 
    return (a + b) > (b + a);
}

void FindMin(string a[],int n){	 
	sort(a,a+n,Compare);	//按连接字符串由小到大进行排列 
	for (int i = 0; i < n; i++) {	//打印连接字符串数值 
        cout << a[i];
    }
    cout<<endl;
}

int main(){
	int n = 0;
	cin>>n;
	string a[1000+1];
	for(int i=0;i<n;i++){	//输入字符 
		cin>>a[i];
	}
	FindMin(a,n);
	return 0;
}




