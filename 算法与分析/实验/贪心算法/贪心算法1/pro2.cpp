/* 
最少经过几次跳跃，可以到达最后一个位置。



#include<iostream>
#include <algorithm>
#include <vector>
using namespace std;

// FindMin函数计算到达数组最后一个位置所需的最少跳跃次数
int FindMin(int* a, int n){
    // 如果只有一个元素，不需要跳跃
    if(n == 1)
        return 0;
    // 如果第一个位置的跳跃长度足够到达最后一个位置，只需要一次跳跃
    if(a[0] >= n){
        return 1;
    }
    int jump = a[0], index_i = 0, temp = 0, cnt = 0; // 初始化跳跃长度、当前位置、最大值和计数器
    int max = 0;
    // 遍历数组
    while(index_i < n){
        // 在当前跳跃长度内寻找最远的可达位置
        for(int i = 1; i <= jump; i++){
            if(a[index_i + i] > temp){
                temp = a[index_i + i]; // 更新最远可达位置
                index_i = index_i + i; // 更新当前位置
            }
        }
        cnt++; // 增加跳跃次数
        jump = temp; // 更新跳跃长度为当前最远可达位置
        temp = 0; // 重置最远可达位置
        // 如果下一次跳跃后可以达到或超过数组末尾，结束循环
        if((index_i + jump + 1) >= n){
            return cnt + 1; // 返回总跳跃次数
        }
    }
}

int main(){
    int a[500 + 10] = {0}; // 初始化数组，大小为510，以存储输入的最多500个元素
    int index = 0; // 当前输入元素的下标
    // 循环读取输入直到换行符
    while((cin >> a[index])){
        char x = cin.get(); // 读取下一个字符
        index++; // 增加元素下标
        // 如果读取到换行符，停止读取更多输入
        if(x == '\n')
            break;
    }
    cout << FindMin(a, index) << endl; // 输出最少跳跃次数
    return 0;
}*/


#include<bits/stdc++.h>
using namespace std;



int main(){
    int a[500 + 1] = {0};
	int n = 0; 
    while(cin >>a[n++]);
    n = n-1;
    int maxpos =0,end = 0,step = 0;
    for(int i = 0;i<n-1;i++){
    	if(maxpos >= i){
    		maxpos = max(maxpos,i+a[i]);
    		/*if(maxpos == n-1){
    			break;
			}*/
    		if(end == i){
    			end = maxpos;
    			step++;
			}
		}
		
	}
	cout<< step <<endl;
}

















