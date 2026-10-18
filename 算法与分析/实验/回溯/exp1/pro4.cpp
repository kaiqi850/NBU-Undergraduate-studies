/*
n个人参加某项特殊考试。
为了公平，要求任何两个认识的人不能分在同一个考场。
求至少需要分几个考场才能满足条件。


#include<iostream>
#include<string.h>
 
using namespace std;

int M[101][101]={0};	//关系矩阵 
int room[101][101]={0};	//考场矩阵 
int ans=99999;	//存放最优解 
int n,m;

void dfs(int num,int kc);


int main()
{
	cin>>n>>m;	//n代表参加考试的人数,m代表接下来输入m行数据来代表两两间关系 
	int a,b;
	for(int i=0;i<m;i++){
		cin>>a>>b;
		M[a][b]=1;
		M[b][a]=1;
	}
	dfs(1,1);
	cout<<ans<<endl;
	return 0;
}

void dfs(int num,int kc) //num表示当前正在考虑的学生编号，kc表示当前的考场数 
{
	if(kc>=ans)return ;	//剪枝 
	if(num>n){	//更新 
		ans=kc;
	}
	else{
		for(int i=1;i<=kc;i++){
			int k=0;
			while(room[i][k]&&M[num][room[i][k]]==0){ //该位置有人且该人与当前学生没有关系则继续找空位  
				k++;
			}
			if(room[i][k]==0){	//在该考场中没有关系且找到空位 
				room[i][k]=num;//入考场 
				dfs(num+1,kc);//递归 
				room[i][k]=0;//回溯 
			}//如果有关系就不能在一个考场，跳出循环找下一个考场
		}
		room[kc+1][0]=num;//所有考场中都存在具有关系的人，则需要新开设一个考场 
		dfs(num+1,kc+1);//递归 
		room[kc+1][0]=0;//回溯 
	}
}*/

#include<bits/stdc++.h>
using namespace std;

int n,m;
int place[100][100] = {0};
int part[101] = {0};    //所在位置索引 
int sum = 0;
int min1 = 101;

void traceback(int i,int maxcl){
	// if(maxcl > min1) return;
	if(i <=n){
		for(int col = 1;col<=n;col++){    //i遍历每个位置  (i,col)
			bool flag = true;
			for(int j = 1;j<i;j++){      //前i行 
				if(part[j] == col && place[i][j] == 1){
					flag = false;
					break;
				}
			}
			if(flag){
				part[i] = col;
				if(col >maxcl){   //安排新教室 
					maxcl++;
				}
				traceback(i+1,maxcl);
				// part[i] = 0;
			}
		}
	}
	else {         //
		if(maxcl <min1){
			min1 = maxcl;
		}
		return;
	}
}

int main(){
	cin >> n>>m;
	for(int i = 0;i<m;i++){
		int a,b;
		cin >> a >>b;
		place[a][b] = 1;
		place[b][a] = 1;
	}
	traceback(1,1);
	cout<<min1<<endl; 
}


































