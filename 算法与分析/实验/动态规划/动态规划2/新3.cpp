/*#include<bits/stdc++.h>
#define INF 0x3f3f3f3f
#define MAXN 105
using namespace std;

struct Node {
    int x, y, fuel;
};

int N, K, A, B, C;
int grid[MAXN][MAXN];
int dp[MAXN][MAXN][11];
bool visited[MAXN][MAXN][11];
int dir[4][2] = {{0, -1}, {-1, 0}, {0, 1}, {1, 0}};

void bfs() {
    memset(dp, INF, sizeof(dp));
    queue<Node> q;
    
    dp[1][1][K] = 0;
    visited[1][1][K] = true;
    q.push({1, 1, K});
    
    while (!q.empty()) {
        Node curr = q.front();
        q.pop();
        visited[curr.x][curr.y][curr.fuel] = false;
        
        for (int i = 0; i < 4; i++) {
            int nx = curr.x + dir[i][0];
            int ny = curr.y + dir[i][1];
            if (nx < 1 || nx > N || ny < 1 || ny > N) continue;
            
            int cost = dp[curr.x][curr.y][curr.fuel];
            int fuelLeft = curr.fuel - 1;
            
            if (i < 2) cost += B;
            if (grid[nx][ny] == 1) {
                cost += A;
                fuelLeft = K;
            }
            if (fuelLeft == 0 && (nx != N || ny != N)) {
                cost += A + C;
                fuelLeft = K;
            }
            
            if (cost < dp[nx][ny][fuelLeft]) {
                dp[nx][ny][fuelLeft] = cost;
                if (!visited[nx][ny][fuelLeft]) {
                    q.push({nx, ny, fuelLeft});
                    visited[nx][ny][fuelLeft] = true;
                }
            }
        }
    }
}

int main() {
    cin >> N >> K >> A >> B >> C;
    for (int i = 1; i <= N; i++)
        for (int j = 1; j <= N; j++)
            cin >> grid[i][j];
    
    bfs();
    int ans = INF;
    for (int i = 0; i <= K; i++)
        ans = min(ans, dp[N][N][i]);
    
    cout << ans << endl;
    return 0;
}*/

#include<bits/stdc++.h>
#define INF 0x3f3f3f3f   //极大值 
#define MAXN 105
using namespace std;

int N, K, A, B, C;
int dp[MAXN][MAXN][2], steps[MAXN][MAXN], grap[MAXN][MAXN];
int dir[4][3] = {{0, -1, B}, {-1, 0, B}, {0, 1, 0}, {1, 0, 0}}; //上 左 下 右 

int main() {
    cin >> N >> K >> A >> B >> C;
    for (int i = 1; i <= N; i++)
        for (int j = 1; j <= N; j++)
            cin >> grap[i][j];
    
    memset(dp, INF, sizeof(dp));
    dp[1][1][0] = 0;
    dp[1][1][1] = K;
    
    bool updated = true;
    while (updated) {
        updated = false;
        for (int i = 1; i <= N; i++) {
            for (int j = 1; j <= N; j++) {
                if (i == 1 && j == 1) continue;  //跳过头
                int cost = dp[i][j][0];   //当前花费 
                int you = dp[i][j][1];  //剩余耗油 				 
                for (int k = 0; k < 4; k++) {  //四个方向 
                    int dx = i + dir[k][0], dy = j + dir[k][1];
                    if (dx < 1 || dx > N || dy < 1 || dy > N) continue;
                	
                	cost = dp[dx][dy][0] +dir[k][2];
					you = dp[dx][dy][1] -1; 
                    
                    if (grap[i][j]) {
                        cost += A;
                        you = K;
                    }
                    if (you == 0 && (i != N || j != N)) {  //用完油 
                        cost += (A + C);
                        you = K;
                    }
                    if (cost < dp[i][j][0]) {  //更新 
                        dp[i][j][0] = cost;
                        dp[i][j][1] = you;
                        updated = true;
                    }
                }
            }
        }
    }
    cout << dp[N][N][0]<<endl;;
}
