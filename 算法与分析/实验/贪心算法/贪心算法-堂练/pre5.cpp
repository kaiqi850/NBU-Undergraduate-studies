

#include <bits/stdc++.h>
using namespace std;

void solve() {
    vector<int> nums;			
    int num;
    int curDiff,nextDiff;
    bool flag = true;			
    while (cin >> num) {	    
        nums.push_back(num);
        if (cin.peek() == '\n') {	        
            cin.ignore();		
            break;
        }
    }
    int n = nums.size();	
    if (n <= 1) {
        cout << nums[0] <<endl;
        cout << n << endl;
        return;
    }
    
    cout<<nums[0];
    
    int count = 1;
    
    for (int i = 1; i < n - 1; i++) {
        curDiff = nums[i] - nums[i-1];
        nextDiff = nums[i+1] - nums[i];  
        if ((curDiff *nextDiff) < 0) {
            cout <<" "<< nums[i] ;	
            count++;	
            flag = false; 
        }
    }

	if ((curDiff *nextDiff) < 0||flag){
		if(nextDiff!=0){
			cout<<" "<<nums[n-1];	 
	    	count++;
		}
	}
    cout << endl;
    cout << count << endl;
}

int main() {
    solve();
    return 0;
}
/*
#include<bits/stdc++.h>
using namespace std;

vector<int> nums;


int main(){
	int i =0;
	while(cin>>i){
		nums.push_back(i);
	}
	if(nums.empty()){
            return 0;
        }

    if(nums.size() < 2){
            return nums.size();
    }

    int symbol = 0;

    int max = 1;
    cout<<
    for(int i = 1; i < nums.size(); i++){
        if(nums[i] - nums[i-1] > 0 && symbol <= 0){
			cout<<nums[i]<<" ";
                max++;
                symbol = symbol == 0;
        }else if(nums[i] - nums[i-1] < 0 && symbol >= 0){
			cout<<nums[i]<<" ";
                max++;
                symbol = -1;
            }

    }
    cout<<endl;
    cout<<max<<endl;
}*/




































