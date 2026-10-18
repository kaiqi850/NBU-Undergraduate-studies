#include<bits/stdc++.h>
#include<cmath>
using namespace std;

int state[100][100];
int cnt = 0; //放置的编号 

void play(int x,int y,int a,int b,int size){   //x和y是特殊点的坐标，a和b是分割的左上角点坐标，size是棋盘边长 
	if(size == 1){
		return;
	} 
	int l = size/2;
	cnt++;
	int index = cnt;
	if(x<a+l&&y<b+l){   //左上角 
		play(x,y,a,b,l);
	}
	else{
		state[a+l-1][b+l-1] = index;
		play(a+l-1,b+l-1,a,b,l);
	}
	if(x<a+l&&y>=b+l){  //左下角 
		play(x,y,a,b+l,l);
	}
	else{
		state[a+l-1][b+l] = index;
		play(a+l-1,b+l,a,b+l,l);
	}
	if(x>=a+l&&y<b+l){  //右上角 
		play(x,y,a+l,b,l);
	}
	else{
		state[a+l][b+l-1] = index;
		play(a+l,b+l-1,a+l,b,l);
	}
	if(x>=a+l&&y>=b+l){  //右下角 
		play(x,y,a+l,b+l,l);
	}
	else{
		state[a+l][b+l] = index;
		play(a+l,b+l,a+l,b+l,l);
	}
}
int main(){
	int k,x,y;
	cin>>k>>x>>y;
	int m = pow(2,k);
	play(x,y,0,0,m);
	for(int i = 0;i < m; i++){
		for(int j=0; j<m ; j++){
				printf("%4d",state[i][j]);
		}
		cout<<endl;
	}
	return 0;
}
