/* 
第一行有2个整数T(1≤T≤1000)和M(1≤M≤100)，
一个空格隔开，T代表总共能够用来采药的时间，M代表山洞里的草药的数目。
接下来的M行每行包括两个在1到100之间包括1和100）的整数，分别表示采摘某株草药的时间和这株草药的价值。
*/

//#include<iostream>
//using namespace std;
//int bag[1001][101]={0};
//int T,M;
//void Findmax(int Tmax,int *t,int *v){
//	for (int i = 0; i < M; i++) {
//		for (int j = 0; j < Tmax; j++) {
//			if (j < t[i])
//				bag[i][j] = bag[i - 1][j];
//			else
//				bag[i][j] = max(bag[i - 1][j], bag[i - 1][j - t[i]] + v[i]);
//		}	
//}
//}
//int main(){
//	int t[101],v[101];
//	cin>>T>>M;
//	for(int i=0; i<M; i++){
//		cin>>t[i];
//		cin>>v[i];
//	}
//	Findmax(T,t,v);
//	cout<<bag[T-1][M-1]<<endl;
//	return 0;
//} 


#include<iostream>
#include <algorithm>
using namespace std;

int bag[101][1001] = {0};	//开辟一个100行1000列的一个数组，用于进行动态规划的存储，列数递增表示采摘时间增加，行数递增表示药品种类增加 
int T, M;	//T表示总共的采药时间，M表示药品种类 

int max(int a,int b){	//找大数 
	if(a>b)
		return a;
	else
		return b;
}

void Findmax(int Tmax, int* t, int* v) {  //背包问题求解 
    for (int i = 1; i <= M; i++) {		//外层循环表示药品种类，逐渐增加 
        for (int j = 1; j <= Tmax; j++) {	//内层循环表示采药时间，逐渐增加 
            if (j < t[i])					//若采药时间不足，则价值等于上一行 
                bag[i][j] = bag[i - 1][j];
            else							//否则，比较该药品是否值得采，放入表格 
                bag[i][j] = max(bag[i - 1][j], bag[i - 1][j - t[i]] + v[i]);
        }
    }	//循环全部完成后我们得到了动态规划建立的表 
}

int main() {
    int t[101] = {0}, v[101] = {0};
    cin >> T >> M;
    for (int i = 1; i <= M; i++) {
        cin >> t[i];
        cin >> v[i];
    }
    Findmax(T, t, v);
    cout << bag[M][T] << endl;
    return 0;
}
