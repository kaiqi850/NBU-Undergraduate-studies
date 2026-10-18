#include<iostream>
using namespace std;
int w[210];//每个节点的金矿数 
int a[210][210]={0};//记录是否有通路 
int dp[210];//每个出发点能得到的最大的金矿数 
int pre[210]={0};//记录上一个节点 
int n,k;//n表示宝藏数,k表示能获得金矿数最大的下一个节点 

void generate(){
	cin>>n;
	for(int i=1;i<=n;i++){
		cin>>w[i];
	}
	int b,c;
	while(cin>>b>>c){
		if(b==0 && c==0)
			break;
		a[b][c]=1;
	}
	dp[n]=w[n];     //题目中b>c初始状态 所以不存在n不存在通路 
}

int main(){
	generate();
    for(int i=n-1;i>=1;i--){  
        int l=0,k=0;  
        for(int j=i+1;j<=n;j++){  //得到每个出发点最大的金矿数 
            if((a[i][j])&& dp[j]>l){  
                l=dp[j];  
                k=j;  
            }  
        }  
        dp[i]=w[i]+l;  
        pre[i]=k;  
    }   
    k=1;  
    for(int i=1;i<=n;i++)
    	k=(dp[i]>dp[k]) ? i:k;
//        if(dp[i]>dp[k]) 
//				k=i;  
		
    int maxn=dp[k];  
    cout<<k;  
    k=pre[k];  
    while(k!=0)//找到后面的节点  
    {  
        cout<<"-"<<k;  
        k=pre[k];  
    }  
    cout<<endl;
    cout<<maxn<<endl;
} 
