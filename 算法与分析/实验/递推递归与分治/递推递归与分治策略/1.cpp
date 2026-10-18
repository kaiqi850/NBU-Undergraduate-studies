#include<iostream>
#include <iomanip> // 包含 setw 和 setfill 操纵符
using namespace std;

int a[1000][100]={0};

void fun(int n){
	int i,q,j;
	a[0][99] = 1;
	a[1][99] = 2;
	a[2][99] = 4;
	for(i = 3;i<n;i++){	
		j = a[i-3][99] + a[i-2][99] + a[i-1][99];
		a[i][99] = j%100000; //留下后五位 
		for(q=98;q>=0;q-- ){
			j = a[i-3][q] + a[i-2][q] + a[i-1][q] + j/100000;
			a[i][q] = j%100000;
		}
	}
}
int main(){
	int n;
	cin>>n; 
	int j,s=0;
	fun(n);
	for (int j = 0; j < 100; j++)   //循环输出
	{
		if (a[n - 1][j] != 0 && s == 0)  //第一个输出的不为0的数，不按照五位输出
		{
			cout << a[n - 1][j];
			s = 1;
		}
		else if (s == 1)   //其他按照五位固定输出
		{
			cout << setw(5) << setfill('0') << a[n - 1][j];
		}
	}
	cout << endl;
	return 0;
}
