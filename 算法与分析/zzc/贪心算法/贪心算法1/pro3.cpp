#include <bits/stdc++.h>
using namespace std;
typedef struct A	//定义一个结构题，表示当前节水人员的下标以及所需要的时间 
{
    int xb;//下标
    int time;//时间
} A;
    A a[1001];
bool Cmp(A a,A b)	//比通过时间大小进行比较 
{
    return a.time<b.time;
}
void FindMin(int n){
	 	int t=0;
		double sum=0;
        memset(a,0,sizeof(a));	//初始化 
        for(int i=0; i<n; i++)	//输入数据 
        {
            cin>>a[i].time;
            a[i].xb=t++;
        }
        sort(a,a+t,Cmp);	//按所需时间大小进行排列 
        for(int i=0; i<t-1; i++)	//循环t-1次按序输出 
        {
            cout<<a[i].xb+1<<" ";	//输出打水人的索引 
            sum+=a[i].time*(t-1-i); //当前接水时间*当前排队人数
        }
        cout<<a[t-1].xb+1<<endl; //输出最后一个位置的索引 
        printf("%.2lf\n", sum / n);	//打印输出平均消耗时间 
}
int main()
{
	int n;
    while(cin>>n)
    {
       FindMin(n);
    }
}





