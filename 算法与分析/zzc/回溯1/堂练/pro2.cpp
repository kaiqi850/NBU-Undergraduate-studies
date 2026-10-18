/*
第一行是顶点的个数n（2≤n≤8），颜色数m（1≤m≤n）。

接下来是顶点之间的连接关系：a b；表示a和b相邻。顶点从1开始计。

当a，b同时为0时表示输入结束。

输出着色方案总数和最少颜色数。如果无可行方案，颜色数为0。
*/ 

#include <iostream>
#include <cstdio>
#include <algorithm>
 
using namespace std;
 
int n,m;
int a=1,b=1;
int cou=0;
int graph[20][20]={0};
int color[20]={0};
int dif[20]={0};
int mini;
 
bool ok(int c)
{
    for(int k=1;k<=n;k++)
    {
        if(graph[c][k]&&color[c]==color[k])	//进行剪枝判断，如果图中两个点之间有联系并且颜色一致 
        {
            return false;
        }
    }
    return true;
}
 
void backtrack(int cur) 	//cur表示当前着色点的位置 
{
    if(cur>n)				//一种方案生成 
    {
    	int j=1,cnt=1;
    	for(int i=1;i<=n;i++){		//从color数组中寻找存在几种不同的颜色 
    		bool flag=true;				//flag判断两个数组之间颜色是否有重叠 
    		for(int j=1;j<=cnt;j++){	//cnt代表不重叠颜色数 
    			if(dif[j]==color[i]){	//一旦有相同颜色，则退出循环，并将flag赋值为false 
    			flag = false;
    			break;
				}		
			}
			if(flag){		//如果flag为true，则添加该颜色，并将计数值+1 
				dif[j]=color[i];
				cnt++;
			}
		}
		mini = min(mini,cnt);
        cou++;
    }
    else				//进行递归回溯 
    {
        for(int i=1;i<=m;i++)
        {
            color[cur]=i;
            if(ok(cur))		//如果符合条件，则往深处进行递归 
            {
                backtrack(cur+1);
            }
            color[cur]=0;		//不符合条件则进行回溯 
        }
    }
}

void get_graph(){	//生成图例 
	cin>>n>>m;
	mini = m;
	while(cin>>a>>b && a!=0 && b!=0){
		 graph[a][b]=1;
	     graph[b][a]=1;
	}
}
 
int main()
{
    get_graph();
    backtrack(1);
    if(cou==0)
    	cout<<0<<" "<<0<<endl;
    else	
    	cout<<cou<<" "<<mini<<endl;
    return 0;
}
