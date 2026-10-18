#include<iostream>
#include <cmath>
using namespace std;

int a[100][100];


void fun1(int k){
	int n = 2,i,j;
	int temp;
	a[1][1] = 1;
	a[1][2] = 2;
	a[2][1] = 2;
	a[2][2] = 1;
	if(k == 1){
		return;
	}
	else{
		for(int t = 1;t<k;t++){
		temp = n;
		n *=2;
		//×óÉÏ½Ç
		//×óÏÂ½Ç
		for(int i = temp+1 ; i<=n; i++){
			for(int j = 1;j<=n/2;j++){
				a[i][j] = a[i-temp][j]+temp;
			}
		}
		//ÓÒÉÏ½Ç
		for(int i = 1 ; i<=n/2; i++){
			for(int j =temp+1 ; j<=n ; j++){
				a[i][j] = a[i+temp][j-temp];
			}
		}
		//ÓÒÏÂ½Ç 
		for(int i = temp+1 ; i<=n;i++){
			for(int j = temp+1;j<=n;j++){
				a[i][j] = a[i-temp][j-temp];
			}
		}
		}
	}
	
}

void show(int n){
	int i,j;
	for(int i = 1 ; i<=n ; i++){
		for(j = 1 ; j<n ; j++){
			cout<<a[i][j]<<" ";
		} 
		cout<<a[i][j]<<endl;
	}
}

int main(){
	int n,k;
	cin>>k;
	n = pow(2,k);
	fun1(k);
	show(n);
}
