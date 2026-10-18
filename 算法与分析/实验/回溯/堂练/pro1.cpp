/*
迷宫可以看成是由n * n的格点组成，每个格点只有2种状态：^ 和 # ；前者表示可以通行后者表示不能通行。
她只能移动到东南西北(或者说上下左右)四个方向之一的相邻格点上，
*

#include <iostream>
using namespace std;

int graph[101][101];
int n = 0;

//把字符图转成数字图储存起来
void get_graph(){
    for(int i = 0; i < n; i++){
        for(int j = 0; j < n; j++){
            char a;
            cin >> a;
            if(a == '^') graph[i][j] = 1;
            else if(a == '#') graph[i][j] = 0;
        }
    }
}

//爆搜一下，你就知道
bool dfs(int x1, int y1, int x2, int y2){
	int a[4] = {-1, 0, 1, 0};
	int b[4] = {0, -1, 0, 1};
    graph[x1][y1] = -1;		//-1代表这个格子位于已经走过的路途上 
    if(x1 == x2 && y1 == y2) return true;
    for(int i = 0; i < 4; i++){		//i分别表示向左，向下，向右，向上移动 
        if(x1 + a[i] >= 0 && x1 + a[i] < n && y1 + b[i] >= 0 && y1 + b[i] < n && graph[x1 + a[i]][y1 + b[i]] == 1)	//若移动方向非越界并且并且可通行 
            if(dfs(x1 + a[i], y1 + b[i], x2, y2)) return true;
    }
    graph[x1][y1] = 1;	//回溯，将这一部分重置为可通行 
    return false;
}


int main(){
    int k = 0;
    cin >> k;
    //读入K组数据并给出相应结果
    for(int i = 0; i < k; i++){
        cin >> n;
        get_graph();
        int x1, y1, x2, y2;
	    cin >> x1 >> y1 >> x2 >> y2;
	    if(!graph[x1][y1] || !graph[x2][y2]){	//起点或者终点有一个不可通行则返回false 
	    	cout<<"NO"<<endl;
		}else if(dfs(x1, y1, x2, y2)) {		//深搜，若成功返回yes 
	    	cout<<"YES"<<endl;
		}else{
	    	cout<<"NO"<<endl;
		}
    }
    return 0;
}*/


#include<bits/stdc++.h>
using namespace std;

char forest[100][100] = {""};
int k,n;
int ar,ac,br,bc;
int dir[4][2] = {{0,1},{0,-1},{-1,0},{1,0}};
bool visited[100][100] = {false};
bool flag = false;

void traceback(int x,int y){
	if(x>=n || y>=n || x<0 || y<0) return;
	if(visited[x][y] == true) return;  //已经访问过 
	visited[x][y] = true; 
	if(x == br && y == bc){
		cout<<"YES"<<endl;
		flag = true;
		return;
	}
	else{
		for(int i = 0;i<4;i++){
			int newx = x+dir[i][0];
			int newy = y+dir[i][1];
			if(forest[newx][newy] != '#'){
				traceback(newx,newy);	
			}
		}
	}
	visited[x][y] = false;
}


int main(){
	cin>>k;
	while(k--){
		flag = false;
		cin>>n;
		for(int i = 0;i<n;i++){
			for(int j = 0;j<n;j++){
				cin>>forest[i][j];
			}
		}
		cin>>ar>>ac>>br>>bc;
		if(forest[ar][ac] == '#' ||forest[br][bc] == '#'){
			cout<<"NO"<<endl;
			continue;
		}
		
		traceback(ar,ac);
		
		if(flag == false){
			cout<<"NO"<<endl;
		}
	}	
}























