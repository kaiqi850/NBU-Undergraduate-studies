/*
  
  
*/
#include<bits/stdc++.h> //
using namespace std;  
#define int long long
//#define ull unsigned long long 
#define endl '\n'
#define IOS ios_base::sync_with_stdio(0),cin.tie(0),cout.tie(0);
const int maxn=1e3+10; 
const int INF=1e9+10;
const int mod=1e9+7;
int m,k;
int x,y;
int n;
int a[maxn][maxn];
void func(int x,int y,int length)
{
	if(length==1) return;
	
	int temp=length/2;
	//left top
	func(x,y,temp);
	
	//left bottom
	a[x+temp][y]=a[x][y]+temp;
	func(x+temp,y,temp);
	
	a[x][y+temp]=a[x][y]+temp;
	func(x,y+temp,temp);
	
	a[x+temp][y+temp]=a[x][y];
	func(x+temp,y+temp,temp);
	
	
}
void solve()
{
	cin>>k;
	n=(1<<k);//00010   00100 
	a[0][0]=1;
	func(0,0,n);
	
	for(int i=0;i<n;i++)
	{
		for(int j=0;j<n-1;j++)
		{
			cout<<a[i][j]<<" ";
		}
		cout<<a[i][n-1]<<endl;
	}
}

signed main(){
//	IOS
    int T;
    T=1;
    //cin>>T;
    while(T--)
    {
    	solve();
	}
    return 0;
}

