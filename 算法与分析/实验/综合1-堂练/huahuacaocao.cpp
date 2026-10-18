#include<bits/stdc++.h>
using namespace std;

int M;
vector<vector<int>> place;
vector<vector<bool>> visited;
int dir[4][2] = {{-1,0},{1,0},{0,-1},{0,1}};
queue<pair<int,int>> qu;

void bfs(int x,int y){
	visited[x][y] = true;
	qu.push({x,y});
	
	while(!qu.empty()){
		pair<int,int> temp = qu.front();
		qu.pop();
		
		for(int i =0;i<4;i++){
			int newx = temp.first + dir[i][0];
			int newy = temp.second + dir[i][1];
			
			if(newx>=0 &&newx <M &&newy >=0 &&newy <M &&visited[newx][newy] == false && place[newx][newy] == 1){
				qu.push({newx,newy});
				visited[newx][newy] = true;
			}
		}
	}
}

int main(){
	cin>>M;
	place = vector<vector<int>>(M, vector<int>(M));
    visited = vector<vector<bool>>(M, vector<bool>(M, false));
	int count = 0;
	for(int i = 0;i<M;i++){
		for(int j =0;j<M;j++){
			cin>>place[i][j];
			visited[i][j] = false;
		}
	}
	for(int i = 0;i<M;i++){
		for(int j =0;j<M;j++){
			if(place[i][j] == 1 && visited[i][j] == false){
				bfs(i,j);
				count++;
			}
		}
	}	
	cout<<count<<endl;
	
}
