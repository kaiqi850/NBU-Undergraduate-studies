#include<bits/stdc++.h>
using namespace std;

int n;
int nums[1001]={0};
int Opt = 0;


int main(){
	int max1;
	cin>>n;
	for(int i=0; i<n; i++){
		cin>>nums[i];
	}
	Opt = nums[0];	
	max1 = nums[0];	 
	for (int i = 0; i < n; i++) {
		Opt = max(nums[i],Opt+nums[i]);	
		
		if(max1<Opt)	
			max1 = Opt;
    }
    cout<<max1<<endl;
	return 0;
}
