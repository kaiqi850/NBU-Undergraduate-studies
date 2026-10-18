#include<iostream>
using namespace std;
int bag[100+5][100+5]={0};
int main(){
	int m,n;
	cin>>m>>n;//m次传递，n个同学
	bag[1][1] = 1;
	for(int i=2;i<=m;i++){
		for(int j=1;j<=n;j++){
			if(j==1)
				bag[i][j] = bag[i-1][n] + bag[i-1][j+1];
			else if(j==n)
				bag[i][j] = bag[i-1][j-1] + bag[i-1][1];
			else
				bag[i][j] = bag[i-1][j-1] + bag[i-1][j+1];
		}
	}
	cout<<bag[m][1]<<endl;
	return 0; 
}




