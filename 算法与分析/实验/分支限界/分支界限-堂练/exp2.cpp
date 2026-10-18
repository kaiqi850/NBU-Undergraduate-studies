/*#include<bits/stdc++.h>
using namespace std;
int Map[21][21] = { 0 }; // 记录区域可通行情况
int m, n;				//区域的行数m和区域的列数n 
int sx, sy, ex, ey;   // 起点终点坐标
queue <int > q; 
int num = 1; // 记录当前是第几轮搜索
void bfs(int x, int y, int ex, int ey) {
	int dir[4][2] = { {-1,0},{1,0},{0,-1},{0,1} }; // 上下左右四个方向
	q.push(x);q.push(y);							//入队 
	while (!q.empty()) {
		int s = q.size() / 2; // 当前搜索轮次有几个点
		for (int k = 0;k < s;k++) {
			int cur_x = q.front();
			q.pop();					//出队 
			int cur_y = q.front();	
			q.pop();					//出队 
			for (int i = 0;i < 4;i++) { // 遍历搜索四个方向
				int now_x = cur_x + dir[i][0];
				int now_y = cur_y + dir[i][1];
				if (now_x == ex && now_y == ey)  // 判断是否到终点
					return;

				if (0 <= now_x && now_x < n && 0 <= now_y && now_y < m && Map[now_x][now_y] == 0) { // 判断当前点是否符合条件
					q.push(now_x);q.push(now_y);		//入队 
					Map[now_x][now_y] = num; // 标记当前点的搜索轮次
				}
			}
		}
		num++;
	}
}


void map_generate() {	//初始化图 
	cin >> m >> n;
	cin >> sx >> sy >> ex >> ey;
	for (int i = 0;i < m;i++)
		for (int j = 0;j < n;j++)
			cin >> Map[i][j];
}


void prit() {  // 格式化输出函数
	for (int i = 0;i < m;i++) {
			for (int j = 0;j < n;j++) {
				if (i == sx && j == sy) // 起点
					cout << "  a";
				else if (i == ex && j == ey) //终点
					cout << "  b";
				else if (Map[i][j] == num) //与b同层的点
					cout << "  0";
				else {// 其余点
					if (Map[i][j] < num) 
						printf("%3d", Map[i][j]);
				}
			}
			cout << endl;
		}
}

int main() {
	map_generate();
	bfs(sx, sy, ex, ey);//调用bfs函数求解
	prit();
	return 0;
}*/




#include<bits/stdc++.h>
using namespace std;

int map1[21][21];
int m,n;
int sx,sy,ex,ey;
bool visited[21][21];
int step[21][21];
queue<pair<int,int>> q;
int dir[4][2] = {{-1,0},{1,0},{0,-1},{0,1}};
int maxnum;

void init() {
    while (!q.empty()) q.pop();
    maxnum = 999999;
    memset(visited, false, sizeof(visited));
    memset(step, 0x3f, sizeof(step));
}

void bfs(int x,int y){
    visited[x][y] = true;
    step[x][y] = 0;
    q.push({x, y});
    
    while(!q.empty()){
        auto cur = q.front();
        q.pop();
        for(int i = 0;i<4;i++){
            int newx = cur.first + dir[i][0];
            int newy = cur.second + dir[i][1];
            if(newx == ex && newy == ey){
                if(step[cur.first][cur.second] + 1 < maxnum){
                    maxnum = step[cur.first][cur.second] + 1;
                }
                return;
            }
            if(newx < 0 || newx >= m || newy < 0 || newy >= n || visited[newx][newy] || map1[newx][newy] == -1){
                continue;
            }
            visited[newx][newy] = true;
            step[newx][newy] = step[cur.first][cur.second] + 1;
            q.push({newx, newy});
        }
    }
}

void show() {
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            if (i == sx && j == sy) {
                cout << setw(3) << "a";
            }
            else if (i == ex && j == ey) {
                cout << setw(3) << "b";
            }
            else if (map1[i][j] == -1) {
                cout << setw(3) << -1;
            }
            else if (step[i][j] >= maxnum) {
                cout << setw(3) << 0;
            }
            else {
                cout << setw(3) << step[i][j];
            }
            //if (j != n - 1) cout << " "; 
        }
        cout << endl; 
    }
    cout << endl;
}

int main() {
    while (cin >> m >> n) {
        cin >> sx >> sy >> ex >> ey;
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                cin >> map1[i][j];
            }
        }
        init();
        bfs(sx, sy);
        show();
    }
    return 0;
}





























