#include <iostream>
using namespace std;
int a[100][10];
int count;

void print(int j){
	count++;
	for(int i=1;i<=j-1;i++)
		cout<<a[i][1]<<","<<a[i][2]<<"->";
	cout<<"4,8"<<endl;

}

void solve(int i){
    int x[4]={2,1,-1,-2};
    int y[4]={1,2,2,1};
	for(int j=0;j<=3;j++){
		if(a[i-1][1]+x[j]>=0&&a[i-1][1]+x[j]<=4&&a[i-1][2]+y[j]>=0&&a[i-1][2]+y[j]<=8){
			a[i][1]=a[i-1][1]+x[j];
			a[i][2]=a[i-1][2]+y[j];
			if(a[i][1]==4&&a[i][2]==8) print(i);
			else solve(i+1);
		}
	}

}

int main() {
	a[1][1]=0;
	a[1][2]=0;
	solve(2);
	return 0;
}
