#include<iostream>
using namespace std;
#define maxn 30
int a[maxn][maxn],n;
int dx[4]={1,0,-1,0};
int dy[4]={0,1,0,-1};
int tmd;
void dfc(int x,int y){
	a[x][y]=0;
	for(int i=0;i<4;i++){
		int ux = x+dx[i],uy = y+dy[i];
		if(ux>=0 and ux<=n+1 and uy>=0 and uy<=n+1 and a[ux][uy]==2){
			dfc(ux,uy);
		}
	}
}
int main(){
	cin>>n;
	for(int i=1;i<=n;i++){
		for(int j=0;j<=n;j++){
			a[i][j]=2;
		}
	}
		
	for(int i=1;i<=n;i++){
		for(int j=1;j<=n;j++){
			cin>>tmd;
			if(tmd==1)
				a[i][j]=1;
		}
	}
	dfc(0,0);
	for(int i=1;i<=n;i++){
		for(int j=1;j<=n;j++){
			cout<<a[i][j]<<" ";
		}
		if(i!=n)cout<<endl;
	}
	return 0;
}
