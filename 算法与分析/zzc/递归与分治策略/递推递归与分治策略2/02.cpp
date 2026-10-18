/*
输入一个整数k，k<=5；
输入特殊格子的坐标x，y

输出一个由数值表示的二维矩阵。填充规则如下：

（1）用数值填充方格；

（2）特殊方格数值为0；

（3）从中心点开始；然后左上、右上、左下、右下的计数顺序填数；同一块用相同数值表示；

（4）每个数值占4个位置空间；右对齐，左补空格。
*/

#include<bits/stdc++.h>
#include<cmath>
using namespace std;

int k=0;
int m=0;
int x,y;
int cnt = 0; 
int chess[33][33] = {0};
//其中x,y表示特殊格子的坐标，Sx,Sy表示正方形左上角的坐标（横纵坐标），length表示正方形的边长 
void Cover(int x,int y,int Sx,int Sy,int length){
	if(length == 1)
		return;
	cnt++; //代表骨牌索引值 
	int index = cnt;
	int l = length/2;	//表示分割成四小块的正方形的长度
	if(x<Sx+l && y<Sy+l)		//在左上角则不放入骨牌 
		Cover(x,y,Sx,Sy,l);
	else{						//否则在右下方放入一小块 
		chess[Sx+l-1][Sy+l-1] = index;
		Cover(Sx+l-1,Sy+l-1,Sx,Sy,l);
	} 
	if(x<Sx+l && y>=Sy+l)		//在左下角则不放入骨牌 
		Cover(x,y,Sx,Sy+l,l);
	else{						//否则在右上方放入骨牌 
		chess[Sx+l-1][Sy+l] = index;
		Cover(Sx+l-1,Sy+l,Sx,Sy+l,l);
	} 
	if(x>=Sx+l && y<Sy+l)	//在右上角则不放入骨牌 
		Cover(x,y,Sx+l,Sy,l);
	else{					//否则在左下方放入骨牌 
		chess[Sx+l][Sy+l-1] = index;
		Cover(Sx+l,Sy+l-1,Sx+l,Sy,l);
	} 
	if(x>=Sx+l && y>=Sy+l)	//在右下角则不放入骨牌 
		Cover(x,y,Sx+l,Sy+l,l);
	else{					//否则在左上方放入骨牌 
		chess[Sx+l][Sy+l] = index;
		Cover(Sx+l,Sy+l,Sx+l,Sy+l,l);
	} 
}

int main(){
	cin>>k;
	cin>>x>>y;
	m=pow(2,k);
	Cover(x,y,0,0,m);
	for(int i = 0;i < m; i++){
		for(int j=0; j<m ; j++){
				printf("%4d",chess[i][j]);
		}
		cout<<endl;
	}
	return 0;		
}

