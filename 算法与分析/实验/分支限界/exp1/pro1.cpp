/*#include<bits/stdc++.h>
using namespace std;
int visited[32][32],map1[32][32];
int dx[4]={0,0,1,-1};
int dy[4]={1,-1,0,0};//代表上下左右四个方向啦
int n,i,j;
void dfs(int p,int q)
{
     int i;
     if(p<0||p>n+1||q<0||q>n+1||visited[p][q]==1)
           return;
      //如果搜过了头或者已经被搜过了或者碰到墙则返回
      visited[p][q]=1;//visited数组标记
      for(i=0;i<4;i++)
          dfs(p+dx[i],q+dy[i]);  //向四个方向搜索
}

void map_generate(){
	cin>>n;
    for (i=1;i<=n;i++)
        for (j=1;j<=n;j++)
        {
            cin>>map1[i][j];//输入方阵
            if(map1[i][j]==0)  
                visited[i][j]=0;
            else 
                visited[i][j]=1;//如果方阵中原本的值就为1，则认为被标记
        }
}

int main() 
{
	map_generate();
    dfs(0,0);
    for (i=1;i<=n;i++)
	{
        for (j=1;j<=n;j++)
        {
              if(visited[i][j]==0)
                   cout<<2<<' ';//如果没被标记，说明没搜到，周围有墙，就是被围住的那部分0，输出2
              else
                   cout<<map1[i][j]<<' ';//剩余的原样输出
        }
        cout<<'\n';
	}
	

}*/

#include<bits/stdc++.h>
using namespace std;

int map1[31][31] = {0};
int n;
bool visited[31][31] = {false};
int dir[4][2] = {{1,0},{-1,0},{0,1},{0,-1}};


void bfs(int x,int y){
	queue<pair<int,int>> q;
		visited[x][y] = true;
		q.push({x,y});
		while(!q.empty()){
			pair<int, int> current = q.front();
			q.pop();
			for(int way = 0;way<4;way++){
				int newx = current.first+dir[way][0];
				int newy = current.second+dir[way][1];
				if(newx>=1 && newx <=n && newy >=1 && newy <=n && map1[newx][newy] == 0 && visited[newx][newy] == false){
					visited[newx][newy] = true;
					q.push({newx,newy});	
				}
			}			
		}
	}

void show(){
	for(int i =1;i<=n;i++){
		for(int j=1;j<=n;j++){
			cout<<visited[i][j];
			if(j != n){
				cout<<" ";
			} 
		}
		cout<<endl;
	}
}

int main(){
	cin >> n;
	for(int i = 1;i<=n;i++){
		for(int j = 1;j<=n;j++){
			cin >> map1[i][j];
			if(map1[i][j]) visited[i][j] = true;
		}
	}
	// show();
	
	
	//bfs(1,1);
	
	
    for (int i = 1;i <= n;i = i + n - 1) {//从边缘两行开始遍历
        for (int j = 1; j <= n;j++) {
            if (visited[i][j])
                continue;
            bfs(i, j);
        }
    }

    for (int i = 1;i <= n;i = i + n - 1) {//从边缘两列开始遍历
        for (int j = 1;j <= n;j++) {
            if (visited[j][i])
                continue;
            bfs(j, i);
        }
    }
	
	for(int i =1;i<=n;i++){
		for(int j=1;j<=n;j++){
			if(visited[i][j]){
				cout<<map1[i][j];
			}
			else{
				cout<<"2";
			}
			cout<<" ";
		}
		cout<<endl;
	}
	
}

































