#include <stdio.h>
#include <string.h>
#include<iostream>
#include <queue>
#include<math.h>
#include <cstdlib>
using namespace std;
const int N = 55;
 
int map[N][N][N];
int vis[N][N][N];
int dx[] = {1,-1,0,0,0,0};
int dy[] = {0,0,1,-1,0,0};
int dz[] = {0,0,0,0,1,-1};
int a,b,c,t,ans;
 
struct Node
{
    int x,y,z,step;
};
 
int check(int i,int j,int k)//ÅÐ¶ÏÊÇ·ñ¿ÉÐÐ
{
    if(i<0 || j<0 || k<0 || i>=a || j>=b || k>=c || map[i][j][k])
    return 0;
    return 1;
}
 
int bfs(int x,int y,int z)
{
    int i;
    queue<Node> Q;
    Node p,q;
    p.x = x;
    p.y = y;
    p.z = z;
    p.step = 0;
    vis[x][y][z] = 1;
    Q.push(p);
    while(!Q.empty())
    {
        p = Q.front();
        Q.pop();
        if(p.x == a-1 && p.y == b-1 && p.z==c-1 && p.step<=t)
        return p.step;
        for(i = 0;i<6;i++)
        {
            q = p;
            q.x+=dx[i];
            q.y+=dy[i];
            q.z+=dz[i];
            if(!vis[q.x][q.y][q.z] && check(q.x,q.y,q.z))
            {
                q.step++;
                vis[q.x][q.y][q.z] = 1;
                if(abs(q.x-a+1)+abs(q.y-b+1)+abs(q.z-c+1)+q.step>t)
                continue;
                Q.push(q);
            }
        }
    }
    return -1;
}

void map_generate() {
	scanf("%d%d%d%d",&a,&b,&c,&t);
    memset(map,0,sizeof(map));
    memset(vis,0,sizeof(vis));
    for(int i = 0;i<a;i++)
    for(int j = 0;j<b;j++)
    for(int k = 0;k<c;k++)
    scanf("%d",&map[i][j][k]);
}

int main()
{
    int cas;
    scanf("%d",&cas);
    while(cas--)
    {
    	map_generate();
        ans = bfs(0,0,0);
        cout<<ans<<endl;
    }
 
    return 0;
}
