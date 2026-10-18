//#include<iostream>
//#include<cmath>
//using namespace std;
//long long calculate(int n){
//	if (n == 1)
//		return 1;
//	else if (n == 2)
//		return 2;
//	else if (n==3)
//		return 4;
//	else 
//		return calculate(n-1)+calculate(n-2)+calculate(n-3);
//}
//int main(){
//	int n;
//	cin>>n;
//	cout<<calculate(n)<<endl;
//}  


//#include<iostream>
//using namespace std;
//int main()
//{
//	int i;
//	int p, q;
//	int s = 0;//判断第一个输出的数
//	cin >> i;
//	int n[1000][100] = { 0 };  //1000行 100列，每列存放五位长的数字
//	n[0][99] = 1;
//	n[1][99] = 2;
//	n[2][99] = 4;
//	int m;
//	for (p = 3; p < i; p++)
//	{
//		m = n[p - 3][99] + n[p - 2][99] + n[p - 1][99];   //计算最低五位数
//		n[p][99] = m % 10000;    //计算结果取余最低五位存放在数组中
//		for (q = 98; q >= 0; q--)
//		{
//			m = n[p - 3][q] + n[p - 2][q] + n[p - 1][q] + m / 100000; //计算第q位的五位数字（第q位的计算结果加上第五位的进位）
//			n[p][q] = m % 100000;  //计算结果取余第五位存放在数组中
//		}
//	}
//
//	for (int j = 0; j < 100; j++)   //循环输出
//	{
//		if (n[i - 1][j] != 0 && s == 0)  //第一个输出的不为0的数，不按照五位输出
//		{
//			cout << n[i - 1][j];
//			s = 1;
//		}
//		else if (n[i - 1][j] != 0 && s == 1)   //其他按照五位固定输出
//		{
//			printf("%05d", n[i - 1][j]);
//			s = 1;
//		}
//	}
//	cout << endl;
//	system("pause");
//	return 0;
//}

#include<iostream>
using namespace std;
int main(){
	int n;
	int p,q;
	int s = 0;
	int a[1000][100]= {0};
	a[0][99] = 1;
	a[1][99] = 2;
	a[2][99] = 4;
	int m;
	cin>>n;
	for(p = 3; p < n; p++){
		m = a[p-3][99] + a[p-2][99] + a[p-1][99];
		a[p][99] = m % 100000;
		for (q = 98; q >= 0; q--){
			m = a[p - 3][q] + a[p - 2][q] + a[p - 1][q] + m / 100000; //计算第q位的五位数字（第q位的计算结果加上第五位的进位）
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
	return 0;
}



