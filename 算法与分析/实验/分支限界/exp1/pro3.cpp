/*#include<bits/stdc++.h>
using namespace std;
struct people{	//结构体用来存储当前节点的坐标、生命值、步数 
	int x,y;
	int life;
	int step;
};
people que[40000];	//定义的队列 
int m,n,t;			//代表地图规格大小和生命值 
char map[201][201];		//用于存储输入的地图 
int dx[4] = {-1,0,1,0}; //下右上左 
int dy[4] = {0,-1,0,1};
int visited[201][201][10];	//判断节点是否被访问，节点一共包含x,y,life三个标记值 
int bfs(int x,int y){	
	memset(visited,0,sizeof(visited));
	int head=0,tail=0;
	que[tail].x = x;		//初始化起始点 
	que[tail].y = y;
	que[tail].life = t;
	que[tail++].step = 0;	 
	visited[x][y][t]=1;		//标记为已访问 
	while(head<tail){
		people temp = que[head++];	//出队 
		if(map[temp.x][temp.y] == '+')	//判断是否为终点 
			return temp.step;
		for(int i=0;i<4;i++){		//四个方向遍历 
			int temp_x = temp.x + dx[i];
			int temp_y = temp.y + dy[i];
			if(temp_x>=0 && temp_y>=0 &&temp_x<m && temp_y<n){	//剪枝判断是否超出地图大小 
				if(map[temp_x][temp_y]!='w'&& !visited[temp_x][temp_y][temp.life]){		//判断是否为通路且不是已访问点 
					que[tail].x = temp_x;
					que[tail].y = temp_y;
					que[tail].life = temp.life;
					que[tail++].step = temp.step+1;		//入队 
					visited[temp_x][temp_y][temp.life] = 1;		//标记为访问 
				}
				if(map[temp_x][temp_y] =='w' && temp.life > 1){		//若为地刺则要进行生命值的判断 
					int temp_t=temp.life-1;							//生命值减一 
					if(!visited[temp_x][temp_y][temp_t]){			 //判断是否为已访问点 
						que[tail].x = temp_x;
						que[tail].y = temp_y;
						que[tail].life = temp_t;
						que[tail++].step = temp.step+1;				//入队 
						visited[temp_x][temp_y][temp_t] = 1;		//标记为已访问 
					}
		        }
			}
		
		}
	}
	return -1;
}

int main(){
	cin>>m>>n>>t;
	for(int i=0;i<m;i++){
		for(int j=0;j<n;j++){	//地图初始化 
			cin>>map[i][j];
		}
	}
	for(int i=0;i<m;i++){		//寻找起点 
		for(int j=0;j<n;j++){
			if(map[i][j]=='!')
				cout<<bfs(i,j)<<endl;
		}
	}
	return 0;
}*/

#include<bits/stdc++.h>
using namespace std;

class people{
	public:
		int x;
		int y;
		int hp;
		int step;

};

int m,n,t;
char map1[201][201];
queue<people> q;
int dir[4][2] = {{-1,0},{1,0},{0,1},{0,-1}};
int maxstep = 999999999;
bool visited[201][201][10] = {false};

void bfs(int x,int y,int hp){
	people p;
	p.x = x;
	p.y = y;
	p.hp = t;
	p.step = 0;
	visited[p.x][p.y][p.hp] = true;
	q.push(p);
	while(!q.empty()){
		p = q.front();
		q.pop();
		
		if(map1[p.x][p.y] == '+'){
			if(p.step < maxstep){
				maxstep = p.step;
			}
			return;
		}
		
		for(int i = 0;i<4;i++){
			people temp;
			temp.x = p.x + dir[i][0];
			temp.y = p.y + dir[i][1];
			temp.hp = p.hp;
			if(!(temp.x>0 && temp.x<m &&temp.y>0 &&temp.y<n)){
				continue;
			}
			if(map1[temp.x][temp.y] == 'w' ){   //遇到障碍 
				temp.hp -= 1;
			}
			if(temp.hp>=1 && visited[temp.x][temp.y][temp.hp] == false){
				temp.step = p.step+1;
				q.push(temp);
			} 
		}
	}
	
	
	
}


int main(){
	cin>>m>>n>>t;
	for(int i=0;i<m;i++){
		for(int j=0;j<n;j++){	//地图初始化 
			cin>>map1[i][j];
		}
	}
	for(int i=0;i<m;i++){		//寻找起点 
		for(int j=0;j<n;j++){
			if(map1[i][j]=='!')
				bfs(i,j,t);
		}
	}
	cout<<maxstep<<endl;
	return 0;
}
































