/* 
设有n个正整数，将它们连接成一排，组成一个最大的多位整数。

*/
#include<bits/stdc++.h>
using namespace std;

bool Compare(string a, string b) {	
    return (a + b) > (b + a);
}

void FindMin(string a[],int n){	 
	sort(a,a+n,Compare);	
	for (int i = 0; i < n; i++) {	
        cout << a[i];
    }
    cout<<endl;
}

int main(){
	int n = 0;
	cin>>n;
	string a[1000+1];
	for(int i=0;i<n;i++){	
		cin>>a[i];
	}
	FindMin(a,n);
	return 0;
}




