#include<bits/stdc++.h>
using namespace std;
#define int long long
#define IOS ios::sync_with_stdio(false);cin.tie(0);cout.tie(0);
const int N=2e5+5;
const int mod=998244353;
const int inf=0x7fffffff;
const double pi=3.1415926535;
using namespace std;
int flag[35][35];
signed main()
{
    IOS;
    int n,m;
	cin>>n>>m;
	flag[0][1]=1;
	for(int i=1;i<=m;i++)
    {
        for(int j=1;j<=n;j++)
        {
            if(j==1)
            {
                flag[i][j]=flag[i-1][n]+flag[i-1][2];
            }
			else if(j==n)
            {
                flag[i][j]=flag[i-1][1]+flag[i-1][n-1];
            }
			else
            {
                flag[i][j]=flag[i-1][j-1]+flag[i-1][j+1];
            }
        }
    }
    for(int i=0;i<=m;i++){
		for(int j=0;j<=n;j++){
			cout<<flag[i][j]<<" ";
		}
		cout<<endl;
	}
	cout<<flag[m][1]<<endl;
	return 0;
}

