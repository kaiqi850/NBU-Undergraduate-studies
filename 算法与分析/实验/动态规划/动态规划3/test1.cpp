#include<bits/stdc++.h>
using namespace std;
int a[1010];  
int dp[1010]; 
int index1[1010] = {0};           
int n;

void solve(){	
	for(int i=n-2; i>=0; i--){
		int length_i = 0;
		for(int j=i+1; j<n; j++){
			if(a[j]>=a[i] && dp[j]>=length_i){  // a[j] 
				length_i = dp[j];
				index1[i] = j;  // i的下一个数字的位置 
			}
		}
		if(length_i)
			dp[i] = length_i + 1;
	}
	
	int max_length = 0, p;
	for (int i = 0; i < n; ++i)
		if (dp[i] >= max_length){  
			max_length = dp[i];
			p = i;
		}
	
	int result[max_length];  
	for(int i=0; i<max_length; i++){
		result[i] = a[p];
		p = index1[p];
	} 
	
	cout<<max_length<<endl;
	for(int i=max_length-1; i>=0; i--)  
	{
		if(i == 0)	
			cout << result[i];
		else
			cout << result[i] << " ";
		
	}
	
} 

int main()
{
	cin >> n;
	for(int i=0; i<n; i++)
		cin >> a[i];
		
	for(int i=0; i<n; i++){
		dp[i] = 1;
		index1[i] = 0;
	} 
	solve();
 	cout<<endl;
	return 0;
}
 
