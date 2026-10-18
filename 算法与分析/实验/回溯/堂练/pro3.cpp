/*
数值1表示该区域种着花，数值0表示该区域是草地。
如果花的上下左右也是花，则这些连着的花必须是同一种花，不相连的花的品种不同。
*/ /*
#include <iostream>
using namespace std;

int M;
int lawn[100][100];
int visited[100][100]={0};

void dfs(int row, int col) {		// 深度搜索 
    visited[row][col] = 1;			//代表这个节点被搜索过 
    if (row > 0 && lawn[row - 1][col] == 1 && visited[row - 1][col] == 0) 	//往左侧节点搜索 
		dfs(row - 1, col);
    if (row < M - 1 && lawn[row + 1][col] == 1 && visited[row + 1][col] == 0) 	//往右侧节点搜索 
		dfs(row + 1, col);
    if (col > 0 && lawn[row][col - 1] == 1 && visited[row][col - 1] == 0) 		//往上方节点搜索 
		dfs(row, col - 1);
    if (col < M - 1 && lawn[row][col + 1] == 1 && visited[row][col + 1] == 0) 	//往下方节点搜索 
		dfs(row, col + 1);
}

int main() {
    cin >> M;
    for (int i = 0; i < M; i++) {		//建图 
        for (int j = 0; j < M; j++) {
            cin >> lawn[i][j];
        }
    }
    int count = 0;
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < M; j++) {
            if (lawn[i][j] == 1 && visited[i][j] == 0) {	//如果是花且未被搜索过，则花的品种+1 
                count++;
                dfs(i, j);		//深搜，排除同一种类的花的数量 
            }
        }
    }
    cout << count << endl;
    return 0;
}*/

#include<bits/stdc++.h>
using namespace std;

int M;
int garden[100][100] = {0};
bool visited[100][100] = {false};
int dir[4][2] = {{1,0},{-1,0},{0,1},{0,-1}};
bool flag = false;
int count1 = 0;
void traceback(int x,int y){
		if(visited[x][y]){   //访问过的点坐标 
			return;	
		}
		else{   
			visited[x][y] = true; 
			for(int i =0;i<4;i++){
				int newx = x+dir[i][0];
				int newy = y+dir[i][1];
				if(newx<0 || newx>=M ||newy <0||newy >=M || garden[newx][newy] == 0){
					continue;
				}
				else{
					// cout<<newx<<" "<<newy<<endl;
					// visited[newx][newy] = true;
					traceback(newx,newy);
					// visited[newx][newy] = true;	
						
				}
			}
}}



int main(){
	cin >> M;
    for (int i = 0; i < M; i++) {		//建图 
        for (int j = 0; j < M; j++) {
            cin >> garden[i][j];
        }
    }
	
	for(int i =0;i<M;i++){
		for(int j = 0;j<M;j++){
			if(garden[i][j] == 1 && visited[i][j] == false){
				// cout<<i<<" "<<j<<endl;
				count1++;
				traceback(i,j);
				// visited[i][j] = true;
			}
		}
	}
	cout<<count1<<endl;
	return 0;
		
} 


































