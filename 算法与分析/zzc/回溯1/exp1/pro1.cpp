/*
在一张N*N的国际象棋棋盘上，放置N个皇后，使得所有皇后都无法互相直接攻击得到，
输入：一个数n，该棋局在一个n*n的棋盘中进行
输出：前三行分别输出每一种解决方案中皇后所在的行数
最后一行输出总共解决方案 
*/ 

#include<iostream>
#include<cstring>
using namespace std;

int q[20];  // 每个皇后所在的列数
int solves = 0;  //解法 

void queen(int i, int n)
{
	if(i < n+1){  
		for(int col=1; col<=n; col++){  // 遍历第i行的每一列，找到可以放置皇后的位置 
			bool flag = true;
			for(int j=1; j<i; j++){  // 遍历前i行，判断列col是否冲突 
				if(col==q[j] || i+col==j+q[j] || i-col==j-q[j]){	//分别判断是否在同一列，是否在左下至右上列，是否在左上至右下列 
					flag = false; 
					break;
				}	
			}
			
			if(flag){
				q[i] = col;
				queen(i+1, n);
			}
		}
	}
	
	else{	// 所有行全部走完，成功找到一种解法 
		solves++;
		if(solves <= 3){  // 只输出前三个解 
			for(int j=1; j<=n; j++){
				if(j == n){  // 格式控制，保证输出每行结尾处没有空格 
					cout << q[j];
					cout << endl;
				}	
				else
					cout << q[j] << " ";	
			}	
		}
		return ; 
	}

}

void Solve(){
	int n;
	memset(q,20,sizeof(q));
	cin >> n;
	queen(1, n);
	cout << solves << endl;
}

int main()
{
		Solve();
		return 0;
}


