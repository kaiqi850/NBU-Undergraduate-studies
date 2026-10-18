/*
现有的地砖只有两种规格分别为1米*1米、2米*2米，
宽度只有3米，长度为N米，请问有几种铺设方案。
*/ 
#include<iostream>
using namespace std;
//用于计算的函数 
void Pave(int n){
		int p,q;	 
		int s = 0;	//用于检测是否为第一个数 
		int a[1000][100]= {0};	//使用数组来解决大数问题 
		//起始状态 
		a[0][99] = 1;	
		a[1][99] = 3;
		a[2][99] = 5;
		int m;
		for(p = 3; p < n; p++){
			m = 2*a[p-2][99] + a[p-1][99];
			a[p][99] = m % 100000;
			for (q = 98; q >= 0; q--){
				m = 2*a[p - 2][q] + a[p - 1][q] + m / 100000; //计算第q位的五位数字（第q位的计算结果加上第五位的进位）
				a[p][q] = m % 100000;  //计算结果取余第五位存放在数组中
			}
			
		}
		
		for (int j = 0; j < 100; j++)   //循环输出
		{
			if (a[n - 1][j] != 0 && s == 0)  //第一个输出的不为0的数，不按照五位输出
			{
				cout << a[n - 1][j];
				s = 1;
			}
			else if (a[n - 1][j] != 0 && s == 1)   //其他按照五位固定输出
			{
				printf("%05d", a[n - 1][j]);
			}
		}
		cout << endl;
}
int main(){
	int C;
	int n;
	cin>>C;
	for(int i=0; i<C; i++){
		cin>>n;
		Pave(n);
	}
	return 0;
}

