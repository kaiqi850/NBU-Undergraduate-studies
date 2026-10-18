#include<bits/stdc++.h>
using namespace std;

int n,ar,ac,br,bc;
char place[101][101];
int dir[4][2] = {{-1,0},{1,0},{0,-1},{0,1}};
bool visited[101][101] = {false};
bool flag = false;

void dfs(int x,int y){
	if(flag) return;
	if(visited[x][y]) return;
	if(x == br &&y == bc){
		cout<<"YES"<<endl;
		flag = true;
		return;
	}
	
	visited[x][y] = true;
	for(int i =0;i<4;i++){
			int newx = x + dir[i][0];
			int newy = y + dir[i][1];
			
			if(newx>=0 &&newx <n &&newy >=0 &&newy <n&& place[newx][newy] == '^' &&flag == false){
				dfs(newx,newy);
			}
		}
	//visited[x][y] = false;
}

int main(){
	int k;
	cin>>k;
	while(k--){
		flag = false;
		
		cin>>n;
		for(int i =0;i<n;i++){
			for(int j = 0;j<n;j++){
				cin>>place[i][j];
				visited[i][j] = false;
			}
		}
		cin>>ar>>ac>>br>>bc;
		if(place[ar][ac] == '^' && place[br][bc] == '^'){
			dfs(ar, ac);
		}
 		if(!flag){
   		 cout<<"NO"<<endl;
  			}		
	}
}
