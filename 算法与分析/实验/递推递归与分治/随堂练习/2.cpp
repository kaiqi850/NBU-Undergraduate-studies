#include<iostream>

using namespace std;


void move(int n,char scr,char dst){
	cout<<n<<" "<<scr<<" "<<dst<<endl;
}


void hanoi(int n,char src,char dst,char mid){
	if(n == 1){
		move(1,src,dst);
	}
	else{
		hanoi(n-1,src,mid,dst);   //前n-1个移动到中间位置 
		move(n,src,dst);    //将最后一个移动到目标
		hanoi(n-1,mid,dst,src);   //将n-1个移动到目标 
	}
}

int  main(){
	int n;
	cin>>n;
	hanoi(n,'A','B','C');
}
