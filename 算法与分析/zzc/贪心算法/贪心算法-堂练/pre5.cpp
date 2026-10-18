/*
一个整数数字序列

第1行输出所求摆动子序列；第2行输出摆动子序列的长度
*/ 
#include <iostream>
#include <vector>
using namespace std;

void solve() {
    vector<int> nums;			// 存储输入的整数序列 
    int num;
    int curDiff,nextDiff;
    bool flag = true;			//用于标记是否找到了摆动 
    while (cin >> num) {	    // 读取整数数字序列
        nums.push_back(num);
        if (cin.peek() == '\n') {	        // 检查输入是否结束
            cin.ignore();		//忽略换行符，为下一次读取做准备 
            break;
        }
    }
    int n = nums.size();	//获取序列的长度 
    if (n <= 1) {
        // 序列长度小于等于1，直接输出序列和长度
        cout << nums[0] <<endl;
        cout << n << endl;
        return;
    }
    
    // 添加第一个元素到摆动子序列
    cout<<nums[0];
    
    int count = 1;
    
    // 计算摆动子序列
    for (int i = 1; i < n - 1; i++) {
        curDiff = nums[i] - nums[i-1];	//当前数字与前一个数字的差 
        nextDiff = nums[i+1] - nums[i];	//下一个数字与当前数字的差 
        
        // 如果当前差值和下一个差值为一正一负，说明找到了摆动 
        if ((curDiff *nextDiff) < 0) {
            cout <<" "<< nums[i] ;	//输出摆动点 
            count++;	//增加摆动子序列的计数 
            flag = false; 	//标记已经找到摆动 
        }
    }
    
    //检查序列末尾是否需要添加一个数字以构成摆动 
    // 如果前面没有找到摆动，或者当前查和下一个差为一正一负的情况下，
	//如果此时最后一格数字和倒数第二个数字的差不是0，则可添加最后一个数字 
	if ((curDiff *nextDiff) < 0||flag){
		if(nextDiff!=0){
			cout<<" "<<nums[n-1];	 
	    	count++;
		}
	}
    // 输出摆动子序列和长度
    cout << endl;
    cout << count << endl;
}

int main() {
    solve();
    return 0;
}
