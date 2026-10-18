#include<bits/stdc++.h>
using namespace std;

int n, c;
vector<int> nums;
bool flag = false;
unordered_set<string> vis; 

void traceback(int i, int sum1){
	if(flag || sum1 > c) return;
	if(sum1 == c){
		cout << "YES!" << endl;
		flag = true;
		return;
	}
	if(i >= n) return;

	string state = to_string(i) + "-" + to_string(sum1);
	if(vis.count(state)) return; 
	vis.insert(state);

	traceback(i + 1, sum1 + nums[i]);
	traceback(i + 1, sum1);
}

int main(){
	cin >> n >> c;
	int sum = 0, x= INT_MAX;
	for(int i = 0; i < n; i++){
		int a;
		cin >> a;
		nums.push_back(a);
		sum+=a;
		x = min(a,x);
	}
	if(sum < c ||x > c){
		cout << "No solution!" << endl;
		return 0;
	}
	traceback(0, 0);
	if(!flag) cout << "No solution!" << endl;
}
