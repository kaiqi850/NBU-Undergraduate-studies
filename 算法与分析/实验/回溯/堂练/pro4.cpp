/*
给定一个无向图G=(V,E)。若 ,且对任意的,都有边 ,则称U是图G的一个完全子图。


G的完全子图U是一个图，当且仅当U不包含在G的更大的完全子图中。


G的最大团是指包含顶点数最多的团。对给定的无向图，找出最大团中定点的个数。
*

#include <iostream>
#include <cstring>
#include <algorithm>
using namespace std;

int G[50][50], bestn;
bool x[50];	//代表是否在云图中 
int n;

void Backtrack(int t, int n, int pn) {		//t是当前正在考虑的的顶点的索引。n是图的顶点总数,pn是当前团中顶点的数量。 
    if (t > n) {
        bestn = max(bestn, pn);
        return;
    }

    bool op = true;			//op用于进行剪枝操作的判断 
    for (int i = 1; i < t; i++) {		//遍历先前的所有节点 
        if (x[i] && G[t][i] == 0) {		//如果先前的顶点有加入至云图并且与当前节点不存在边的联系，则不符合条件，剪枝 
            op = false;
            break;
        }
    }

    if (op) {		//如果符合条件，当前考虑节点+1 ，云图节点+1 
        x[t] = true;
        Backtrack(t + 1, n, pn + 1);
    }

    if (pn + n - t > bestn) {	//如果云图节点 + 剩余节点的和大于最大云图节点数，则还可以继续搜索云图，否则没有必要 
        x[t] = false;
        Backtrack(t + 1, n, pn);
    }
}

void get_graph(){
	cin >> n;
    memset(G, 0, sizeof(G));
    for (int i = 1; i <= n; i++) {		//构建图 
        for (int j = 1; j <= n; j++) {
            cin >> G[i][j];
        }
    }
}

void solve(){
	get_graph();	 
	bestn = 0;						//初始化最大团节点 
    memset(x, false, sizeof(x));
    Backtrack(1, n, 0);				 
    cout << bestn << endl;
}*/


































