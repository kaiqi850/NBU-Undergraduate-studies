#include<bits/stdc++.h>
using namespace std;

int n, a, b, k[210];
bool visited[210] = { false }; // 标记楼层是否访问过，默认没有

void bfs() {
    queue<pair<int, int> > q; // 定义队列
    pair<int, int> p, t; // <当前第几层，当前按了几次>
    p.first = a; p.second = 0;// 赋初值
    q.push(p);//进入队列
    while (!q.empty()) {//队列非空
        p = q.front(); q.pop();
        if (visited[p.first]) // 如果楼层访问过
            continue;
        if (p.first == b) { // 达到目标楼层
            cout << p.second << endl;
            return;// 退出搜索
        }
        visited[p.first] = true; // 标记楼层访问过
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

void solve(){
	cin >>n>>a>>b;
	for (int i = 1; i <= n; i++)
        cin >> k[i];
    bfs(); //广度优先搜索答案
}

int main() {
	solve();
    return 0;
}


