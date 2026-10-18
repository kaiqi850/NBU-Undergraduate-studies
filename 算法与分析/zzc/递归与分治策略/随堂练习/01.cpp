/* 
粗心的助手却把请柬全装错了信封。请问：助手会有多少种装错的可能呢？
首先自底向上，若是一个信封则情况为零，若是两个信封则只有一种情况；
接着在自顶向下，假设现在A信错装进了B信封，有以下两种情况：
1.B信正好装进了A信封，则剩余数目为f(n-2);
2.B信未装进A信封，则B信与A信封为一组，二者不能装在一起，则剩余数目为f(n-1);
又因为A信可任意错装进剩余信封， 
故f(n)=(n-1)*(f(n-1)+f(n-2)) 
*/ 
#include<iostream> 
using namespace std;
int Count(int n){
	if(n == 1)	//递归初始值 
		return 0;
	if(n == 2)
		return 1;
	else 
		return (n-1)*(Count(n-1) + Count(n-2));		//递归 
}

int main(){
	int n;
	while(cin>>n){
		cout<<Count(n)<<endl;
	}
	return 0;
}
