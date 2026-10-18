/*#include<bits/stdc++.h>
using namespace std;
int a[35][35] = { 0 };  // 记录方阵初始情况
int n;
int dir[4][2] = { {1, 0}, {-1, 0}, {0, 1}, {0, -1} }; // 上下左右四个方向
int cnt = 0; //记录某一封闭区域的面积
int cnt_max = 0; // 记录最大封闭区域的面积
int id = 3; // 搜索标记
int id_max = id; // 最大封闭区域对应的搜索标记

void dfs(int x, int y)	//将与其邻接的0坐标改为id
{
	int i;

	if (a[x][y] != 0 || x < 0 || x > n + 1 || y < 0 || y > n + 1) { //检查是否符合条件
		return;
	}

	a[x][y] = id;
	cnt++;

	for (i = 0; i < 4; i++) { // 搜索四个方向
		dfs(x + dir[i][0], y + dir[i][1]);
	}
}

void map_generate() {
	int i,j;
	cin >> n;
	for (i = 1; i <= n; i++) { //输入方阵
		for (j = 1; j <= n; j++) {
			cin >> a[i][j];
		}
	}
	//最外围的0不形成封闭区域
	dfs(0, 0);
	id++;
}

void prit() {  // 格式化输出函数
	int i, j;
	for (i = 1; i <= n; i++) {
		for (j = 1; j <= n; j++) {
			if (a[i][j] == 1) {
				cout << a[i][j] << ' ';
			}
			else if (a[i][j] != id_max) {
				cout << '0' << ' ';
			}
			else {
				cout << '2' << ' ';
			}
		}
		cout << endl;
	}
}


void Solve(){
	int i, j;
	map_generate();
	for (i = 2; i < n; i++) {//从第二层开始形成封闭区域
		for (j = 2; j < n; j++) {
			cnt = 0;
			dfs(i, j);
			if (cnt > cnt_max) { // 判断是否为最大封闭区域
				cnt_max = cnt;
				id_max = id;
			}
			id++; // 搜索标记+1
		}
	}
	prit();
}

int main() {
	Solve();
	return 0;
}*/

#include<bits/stdc++.h>
using namespace std;

int n;
int map1[35][35] = {0};
int maxid = -1;
int maxnum = 0;
queue<pair<int,int>> q;
int dir[4][2] = {{-1,0},{1,0},{0,-1},{0,1}};
int visited[35][35] = {0};
int id = 2;

int bfs(int x,int y,int id){
	int cnt = 0;
	pair<int,int> cur;
	cur.first = x;
	cur.second = y;
	visited[x][y] = id;
	q.push(cur);
	while(!q.empty()){
		cur = q.front();
		q.pop();
		
		
		for(int i = 0;i<4;i++){
			pair<int,int> temp;
			temp.first = cur.first+dir[i][0];
			temp.second = cur.second + dir[i][1];
			if(temp.first<0 || temp.first >=n || temp.second<0 || temp.second>=n || visited[temp.first][temp.second] == id || map1[temp.first][temp.second] == 1){
				continue;
			}
			visited[temp.first][temp.second] = id;
			cnt++;
			q.push(temp);
			
		}
	}
	return cnt;	
	
}


void show(){
	for(int i =0;i<n;i++){
		for(int j = 0;j<n;j++){
			if(visited[i][j] == maxid){
				cout<<"2"<<" ";
			}
			else{
				cout<<map1[i][j]<<" ";
			}
		}
		cout<<endl;
	}	
}

int main(){
	cin>>n;
	for(int i =0;i<n;i++){
		for(int j = 0;j<n;j++){
			cin>>map1[i][j];
			if(map1[i][j] == 1) visited[i][j] =1;
		}
	}
	
	for(int i = 0;i<n;i += n-1){
		for(int j =0;j<n;j++){
			if(visited[i][j] == 0 && map1[i][j] == 0)
			bfs(i,j,1);			
		}
	}
	
	for(int j = 0;j<n;j += n-1){
		for(int i =0;i<n;i++){
			if(visited[i][j] == 0 && map1[i][j] == 0)
			bfs(i,j,1);			
		}
	}
	
	for(int i =0;i<n;i++){
		for(int j = 0;j<n;j++){
			if(visited[i][j] == 0){
				int cnt = bfs(i,j,id);
				if(cnt > maxnum){
					maxnum = cnt;
					maxid = id;
				}
				id++;
			}
		}
	}
	
		show();	
	
	
	
}


































