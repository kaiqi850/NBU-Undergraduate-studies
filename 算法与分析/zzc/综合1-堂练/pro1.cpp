#include<cstdio>
#include<cmath>
#include<iostream> 
#include<cstring>
#include<algorithm>
using namespace std;
 
int h[101];
bool dp[101][10001];
 
int main()
{
    int n, ret;
    cin>>n;
	ret = 10000;
    int i, j, k, cnt, sum;
    for(k = 0; k < n; k++)
    {
        cnt = sum = 0;
        while(1)
        {
        	cin>>h[cnt];
            if(h[cnt] == -1) break;
            sum += h[cnt++];
        }

        dp[k][0] = true;
        for(i = 0; i < cnt; i++)
            for(j = sum; j >= h[i]; j--)
                dp[k][j] = (dp[k][j] || dp[k][j-h[i]]);
        for(i = sum; !dp[k][i]; i--);
        ret = min(ret, i);
    }

    for(i = ret; i >= 0; i--)
    {
        bool flag = true;
        for(j = 0; j < n; j++)
            if(dp[j][i] == false) {flag = false; break; }
        if(flag == true) { ret = i; break;}
    }
    cout<<ret<<endl;
    return 0;
}
