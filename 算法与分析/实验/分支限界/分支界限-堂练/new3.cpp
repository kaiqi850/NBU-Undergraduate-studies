#include <bits/stdc++.h>
using namespace std;

int n,m;
vector<string> g;
int dx[4]={-1,1,0,0}, dy[4]={0,0,-1,1};

bool in(int x,int y){
  return x>=0&&x<n&&y>=0&&y<m;
}

int main(){
  cin>>n>>m;
  g.resize(n);
  for(int i=0;i<n;i++) cin>>g[i];
  int sx,sy,bx,by,tx,ty;
  sx=sy=bx=by=tx=ty=-1;
  for(int i=0;i<n;i++)for(int j=0;j<m;j++){
    char c=g[i][j];
    if(c=='M'){sx=i;sy=j;g[i][j]='w';}
    else if(c=='P'){bx=i;by=j;g[i][j]='w';}
    else if(c=='K'){tx=i;ty=j;g[i][j]='w';}
  }
  if(bx==tx&&by==ty){
    cout<<0;
    return 0;
  }
  vector<vector<array<bool,4>>> seen(n, vector<array<bool,4>>(m));
  queue<tuple<int,int,int,int>> q; 

  for(int d=0;d<4;d++){
    int px=bx-dx[d], py=by-dy[d];
    int nbx=bx+dx[d], nby=by+dy[d];
    if(!in(px,py)||!in(nbx,nby)) continue;
    if(g[nbx][nby]=='S') continue;

    vector<vector<char>> vis(n, vector<char>(m));
    queue<pair<int,int>> qq;
    vis[sx][sy]=1; qq.emplace(sx,sy);
    while(!qq.empty()){
      auto [x,y]=qq.front();qq.pop();
      for(int i=0;i<4;i++){
        int nx=x+dx[i], ny=y+dy[i];
        if(!in(nx,ny)||vis[nx][ny]) continue;
        if(nx==bx&&ny==by) continue;
        if(g[nx][ny]=='S') continue;
        vis[nx][ny]=1;
        qq.emplace(nx,ny);
      }
    }
    if(!vis[px][py]) continue;
    seen[nbx][nby][d]=1;
    q.emplace(nbx,nby,d,1);
  }
  while(!q.empty()){
    auto [x,y,dir,step]=q.front();q.pop();
    if(x==tx&&y==ty){
      cout<<step;
      return 0;
    }
    int px=x-dx[dir], py=y-dy[dir];

    vector<vector<char>> vis(n, vector<char>(m));
    queue<pair<int,int>> qq;
    vis[px][py]=1; qq.emplace(px,py);
    while(!qq.empty()){
      auto [ux,uy]=qq.front();qq.pop();
      for(int i=0;i<4;i++){
        int vx=ux+dx[i], vy=uy+dy[i];
        if(!in(vx,vy)||vis[vx][vy]) continue;
        if(vx==x&&vy==y) continue;
        if(g[vx][vy]=='S') continue;
        vis[vx][vy]=1;
        qq.emplace(vx,vy);
      }
    }
    for(int d=0;d<4;d++){
      int nx=x+dx[d], ny=y+dy[d];
      int reqx=x-dx[d], reqy=y-dy[d];
      if(!in(nx,ny)||!in(reqx,reqy)) continue;
      if(g[nx][ny]=='S') continue;
      if(!vis[reqx][reqy]) continue;
      if(seen[nx][ny][d]) continue;
      seen[nx][ny][d]=1;
      q.emplace(nx,ny,d,step+1);
    }
  }
  cout<<"No solution£¡";
  return 0;
}

