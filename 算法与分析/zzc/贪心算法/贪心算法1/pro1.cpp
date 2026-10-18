/* 
共两行。
第一行是一个整数 n(1≤n≤1000) ，表示砖头堆数。
第二行n个整数，每个整数表示每堆砖头的砖头块数。
*/

#include<iostream>
#include <algorithm>
#include <vector>
using namespace std;

int FindMin(int* a,int n){
	int ans = 0;
	sort(a, a+n);
	for(int i=0; i<n-1; i++)
	{
		int cost_i = a[i] + a[i+1];
		int k = i+2;
		// 后面有比堆积的砖块少的向前移一位 
		while(a[k]<cost_i && k<n)
		{
			a[k-1] = a[k];
			k++;
		}
		a[k-1] = cost_i;
		ans += cost_i; 
	 } 
    return ans;
}

int main(){
	int n;
	cin>>n;
	int a[n+1] = {0};
	for(int i=0;i<n;i++){
		cin>>a[i];
	}
	cout<<FindMin(a,n)<<endl;
	return 0;
}
