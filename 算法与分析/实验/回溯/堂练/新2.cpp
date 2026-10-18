#include<bits/stdc++.h>
using namespace std;

char st[5][5], tmp[5][5];
int dx[5] = {0, 0, 1, -1, 0};
int dy[5] = {1, -1, 0, 0, 0};
int ans = 1e9;

void flip(int x, int y){
    for(int i = 0; i < 5; i++){
        int nx = x + dx[i];
        int ny = y + dy[i];
        if(nx >= 1 && nx <= 4 && ny >= 1 && ny <= 4){
            tmp[nx][ny] = tmp[nx][ny] == 'b' ? 'w' : 'b';
        }
    }
}

bool check(){
    char c = tmp[1][1];
    for(int i = 1; i <= 4; i++)
        for(int j = 1; j <= 4; j++)
            if(tmp[i][j] != c) return false;
    return true;
}

void dfs(int k, int cnt){
    if(k == 16){
        if(check()) ans = min(ans, cnt);
        return;
    }
    int x = k / 4 + 1;
    int y = k % 4 + 1;

    // 不按当前灯
    dfs(k + 1, cnt);

    // 按当前灯
    flip(x, y);
    dfs(k + 1, cnt + 1);
    flip(x, y); 
}

int main(){
    for(int i = 1; i <= 4; i++)
        for(int j = 1; j <= 4; j++){
            cin >> st[i][j];
            st[i][j] = tolower(st[i][j]);
        }

    memcpy(tmp, st, sizeof(st));
    dfs(0, 0);

    if(ans == 1e9) cout << "Impossible" << endl;
    else cout << ans << endl;

    return 0;
}

