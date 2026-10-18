#include<iostream>
using namespace std;
int n,m;				//代表n行m列的海洋地图 
int state[10001][3];	//记录每个访问状态下的特征，分别包括坐标和转弯数 
int head,tail;			//用于对队列进行控制 
int c,s;				//c代表输入的图,s代表转弯计数值。 
int x,y;				//现在判断点的坐标 
int x2,y2;				//终点坐标 
bool ok[101][101],a[101][101];
int dx[4]={0,0,1,-1},dy[4]={1,-1,0,0};//拓展方向
void bfs()
{
	head=0;
	tail=1;
	while(head<tail)//空队退出
		{
			head++;//出队
			for (int i=0;i<4;i++)//4个方向
			{
				x=state[head][0];y=state[head][1];
				int j=1;
				while (!a[x+dx[i]*j][y+dy[i]*j] && x+dx[i]*j<=n && y+dy[i]*j<=m && x+dx[i]*j>0 && y+dy[i]*j>0)
				//如果碰到墙或边缘就结束拓展
				{
				  if (!ok[x+dx[i]*j][y+dy[i]*j])
				  //如果已经走过的路线就不入队
				  {
				  	if (x+dx[i]*j==x2 && y+dy[i]*j==y2)//结束判断
					  	{
					  		s=state[head][2];
					  		return;
					  	}
				  	tail++;//入队
				  	state[tail][0]=x+dx[i]*j;
				  	state[tail][1]=y+dy[i]*j;//储存位置
				  	state[tail][2]=state[head][2]+1;//储存转弯数
				  	ok[x+dx[i]*j][y+dy[i]*j]=true;//已经走过该地
				  }
				  j++;//下一个拓展
				}
			}
		}
}

void map_generate() {	//初始化构建图例 
	cin>>n>>m;		
	for (int i=1;i<=n;i++)
	{
	  for (int j=1;j<=m;j++)
	  {
	  	cin>>c;
	  	if (c!=0) a[i][j]=true;
	  }
	}
	cin>>state[1][0]>>state[1][1]>>x2>>y2;
}

int main()
{
	map_generate();
	bfs();
	cout<<s<<endl;
}

