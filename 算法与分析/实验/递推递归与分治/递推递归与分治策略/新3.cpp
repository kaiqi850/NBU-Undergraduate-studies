/*#include <iostream>
using namespace std;

class Pos {
public:
    int x;
    int y;

    // 构造函数
    Pos(int xVal = 0, int yVal = 0) : x(xVal), y(yVal) {}

};

int play(const Pos& p1, const Pos& p2) {
    
}

int main() {
    int x1, y1, x2, y2;
    cin >> x1 >> y1 >> x2 >> y2;

    Pos B(x1, y1); // 创建第一个点
    Pos C(x2, y2); // 创建第二个点


    return 0;
}*/

/*
#include<bits/stdc++.h>
using namespace std;
long long  mp[20][20];
int check(int i, int j, int x, int y){//判断马点
    return (abs(i-x) + abs(j-y) == 3 && i != x && j != y) || (i == x && j == y);
}
long long solve(int n, int m, int x, int y){
    mp[0][0] = 1;
    for(int i = 1; i <= n; ++i){//初始化第一列
        mp[i][0] = (check(i, 0, x, y)? 0 : mp[i-1][0]);    
    }
    for(int j = 1; j <=m; ++j){//初始化第一行
        mp[0][j] = (check(0,j,x,y)? 0 : mp[0][j-1]);
    }
    for(int i = 1; i <= n; ++i){
        for(int j = 1; j <= m; ++j){//状态转移计算
            mp[i][j] = (check(i,j,x,y)? 0:mp[i-1][j] + mp[i][j-1]);
        }
    }
    return mp[n][m];
}
int main(){
    int n,m, x, y;
    cin>>n>>m>>x>>y;
    cout<<solve(n,m,x,y)<<endl;
    return 0;
}*/

#include <iostream>
#include <cstdio>
#include <cstring>

using namespace std;

int main() {
    int n, m, x, y;
    cin >> n >> m >> x >> y;
    long long dp[n + 1][m + 1];
    memset(dp, -1, sizeof(dp));
    dp[0][0] = 1;
    if(x <= n && y <= m) {
        dp[x][y] = 0;
    }
    int change[8][2] = {{-2,1},{-1,2},{1,2},{2,1},{2,-1},{1,-2},{-1,-2},{-2,-1}};
    for(int i = 0; i < 8; ++i) {
        int temp_x = x + change[i][0];
        int temp_y = y + change[i][1];
        if(temp_x >= 0 && temp_y >= 0 && temp_x <= n && temp_y <= m) {
            dp[temp_x][temp_y] = 0;
        }
    }
    for(int j = 1; j <= m; ++j) {
        if(dp[0][j] != 0) {
            dp[0][j] = dp[0][j - 1];
        }
    }
    for(int i = 1; i <= n; ++i) {
        if(dp[i][0] != 0) {
            dp[i][0] = dp[i - 1][0];
        }
    }
    for(int i = 1; i <= n; ++i) {
        for(int j = 1; j <= m; ++j) {
            if(dp[i][j] != 0) { //可能是马可以到达的点
                dp[i][j] = dp[i - 1][j] + dp[i][j - 1];
            }
        }
    }
    cout << dp[n][m] << endl;
    return 0;
}

