#include<bits/stdc++.h>
using namespace std;

int n, a, b, k[210];
bool visited[210] = { false }; 

void bfs() {
    queue<pair<int, int> > q; 
    pair<int, int> p, t; 
    p.first = a; p.second = 0;
    q.push(p);
    while (!q.empty()) {
        p = q.front(); q.pop();
        if (visited[p.first]) 
            continue;
        if (p.first == b) {
            cout << p.second << endl;
            return;
        }
        visited[p.first] = true; 
        if (p.first - k[p.first] > 0) { // 向下按
            t.first = p.first - k[p.first];
            t.second = p.second + 1;
            q.push(t);
        }
        if (p.first + k[p.first] <= n) { // 向上按
            t.first = p.first + k[p.first];
            t.second = p.second + 1;
            q.push(t);
        }
    }
    cout << -1 << endl;
}

int main() {
	cin >>n>>a>>b;
	for (int i = 1; i <= n; i++)
        cin >> k[i];
    bfs(); 
    return 0;
}
/*
#include<bits/stdc++.h>
using namespace std;

int N,A,B;
int lev[201] = {0};
queue<int> node;

void bfs() {
    queue<pair<int, int> > q; // 定义队列
    pair<int, int> p, t; // <当前第几层，当前按了几次>
    p.first = a; p.second = 0;// 赋初值
    q.push(p);//进入队列
    while (!q.empty()) {//队列非空
        p = q.front(); q.pop();
        if (f[p.first]) // 如果楼层访问过
            continue;
        f[p.first] = true; // 标记楼层访问过
        if (p.first == b) { // 达到目标楼层
            cout << p.second << endl;
            return;// 退出搜索
        }
        if (p.first - k[p.first] > 0) { // 向下按
            t.first = p.first - k[p.first];
            t.second = p.second + 1;
            q.push(t);
        }
        if (p.first + k[p.first] <= n) { // 向上按
            t.first = p.first + k[p.first];
            t.second = p.second + 1;
            q.push(t);
        }
    }
    cout << -1 << endl;
}

void bfs(int start){
	node.push(start);
	while(!node.empty()){
		int temp = node.front();
		node.pop();
		for(int i = temp;i<=temp+lev[temp];i++){  //temp是当前楼层,i是可以到达的楼层 
			if(i>=) 
		}
		for(int i = temp;i>=temp+lev[temp];i--){  //temp是当前楼层,i是可以到达的楼层 
			if(i>=) 
		}
	}
	
}

int main(){
	cin>>N>>A>>B;
	for(int i = 1;i<=N;i++){
		cin>>lev[i];		
	}
	
	bfs(1);
}*/



































