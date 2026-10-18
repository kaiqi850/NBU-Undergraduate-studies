

#include <bits/stdc++.h>
using namespace std;
int n=4,m=8; 
int a[100][10];	  
int i=1;
void dfs(int y,int x)
{
    if(y<0||y>n||x>m){	 
    	return;
	}
    if(y==n&&x==m){	 
    	for(int j=1;j<i;j++){
    		cout<<a[j][1]<<","<<a[j][2]<<"->";
		}
    	cout<<"4,8"<<endl;
	}
    else
    {
    	a[i][1]=y;	
    	a[i][2]=x;
    	i++;
        dfs(y+2,x+1);
        dfs(y+1,x+2);
        dfs(y-1,x+2);
        dfs(y-2,x+1);
        a[i][1]=0;	
    	a[i][2]=0;
    	i--;
    }
}

int main()
{
    dfs(0, 0);
    return 0;
}
/*
#include<bits/stdc++.h>
using namespace std;

int board[5][9];
vector<pair<int,int>> path;
int endx = 8;
int endy = 4;
int dir[2][2] = {{2,1},{1,2}};
int x =0,y =0; 

void traceback(int x,int y){
	if(x>endx || y>endy){
		return;
	}
	
	path.push_back({x,y});   //0,0 2,1 4,2 6.3
	
	if(x == endx && y == endy){
		int i;
		for(auto p:path){
			cout<<"("<<p.first<<","<<p.second<<")";;
		 }
		// cout<<"("<<8<<","<<4<<")"<<endl;
		// path.pop_back();
		return;
	}
	
	for(int way = 0;way<2;way++){ //两种方式 
		traceback(x + dir[way][0],y + dir[way][1]);   //2,1 4,2 6,3 8.4
	}
	
	path.pop_back();
	
}

int main(){
	traceback(0,0);	
}*/




































