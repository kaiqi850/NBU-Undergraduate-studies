/*
第一行包含数据N，区域的个数；

第二行包含H，房子的数目；

下面的H行描述居民们的需要:B E T。 
输出能满足所有要求的最少的树的数。

#include <iostream>
#include <algorithm>

using namespace std;

const int MAX = 3e4+5;

// 定义一个结构体，用于存储每个居民的种树要求
struct House{
    int b; // 居民要求种树的起始区域编号
    int e; // 居民要求种树的结束区域编号
    int t; // 居民希望至少种植的树的数量
}house[5005];

// 数组，用于标记每个区域是否已经种了一棵树
bool q[MAX];

// 自定义比较函数，用于对居民的种树要求按照结束区域编号进行排序
bool cmp(House A, House B){
    return A.e < B.e;
}

// 解决问题的函数，计算满足所有居民要求的最少树的数量
int solve(int n, int h){
    int ans = 0; // 最少树的数量
    sort(house, house+h, cmp); // 对居民的种树要求按照结束区域编号进行升序排序

    // 遍历每个居民的种树要求
    for(int i=0; i<h; i++){
        int count = 0; // 已种植树的数量
        // 检查当前居民要求的区域内已经种了多少棵树
        for(int j=house[i].b; j<=house[i].e; j++){
            if(q[j])
                count++;
        }
        // 如果当前区域内已种的树少于居民要求的数量
        if(count < house[i].t){
            // 从区域的结束编号向前遍历，寻找可以种树的位置
            for(int j=house[i].e; j>=house[i].b; j--){
                if(!q[j]){ // 如果该位置没有种树
                    q[j] = 1; // 标记该位置已种树
                    count++; // 已种树的数量增加
                    ans++;    // 最少树的数量增加
                }
                if(count == house[i].t) // 如果已达到居民要求的树的数量
                    break; // 停止当前循环
            }
        }
    }
    return ans; // 返回满足所有要求的最少树的数量
}

// 主函数，读取输入并调用解决函数
int main(){
    int n, h;
    cin >> n >> h; // 读取总区域数和居民数量
    for(int i=0; i<h; i++)
        cin >> house[i].b >> house[i].e >> house[i].t; // 读取每个居民的种树要求
    cout << solve(n, h) << endl; // 输出最少树的数量
    return 0;
}*/
/*
#include <bits/stdc++.h>
using namespace std;

int n, h, k, ans;

class per{
public:
	int b,e,t;
}; 
per a[5005];

bool cmp(per p1,per p2){
	return p1.e<p2.e;
}
int test(int *res,int start,int end,int num){
	int sum =0;
	for(int i =start;i<=end;i++){
		if(res[i]==1) sum++;
	}
	if(sum >= num) return 1;
	else return 0;
}
int main()
{
	cin >> n >> h;
	int res[n+1]={0};
	for (int i = 0;i < h;i++) 
	{
		cin >> a[i].b >> a[i].e >> a[i].t;
	}
	sort(a, a + h, cmp);
	int count1 = 0;
	for(int i =0;i<h;i++){
		if(!test(res,a[i].b,a[i].e,a[i].t)){  //还没种完 
			for(int j =a[i].e;j>=a[i].b;j--){
			if(res[j]!=1&&!test(res,a[i].b,a[i].e,a[i].t)){  
				res[j] = 1;
				count1++;
			}
		}	
		}
	}
	cout<<count1<<endl; 
	
}*/


#include<bits/stdc++.h>
using namespace std;

int N,H;
class peo{
	public:
	int B,E,T;
};

bool compare(peo p1,peo p2){
	return p1.E<p2.E;
}

int main(){
	cin>>N>>H;
	peo peo[H];
	vector<bool> tree(N+1,false);
	for(int i =0;i<H;i++){
		cin>>peo[i].B>>peo[i].E>>peo[i].T;
	}
	sort(peo,peo+H,compare);
	
	int sum1 = 0;
	
	for(int i = 0;i<H;i++){
		int cnt = 0;
		for(int j = peo[i].B;j<=peo[i].E;j++){
			if(tree[j]) cnt++;
		}
		int k = peo[i].E;
		while(cnt<peo[i].T){
			if(!tree[k]){
				tree[k] = true;
				cnt++;
				sum1++;
			}
			k--;
		}
	}
	cout<<sum1<<endl;
}
































































