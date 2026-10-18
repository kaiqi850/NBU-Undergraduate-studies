/*
设A、B、C是3 个塔座。开始时，在塔座A 上有一叠共n 个圆盘，这些圆盘自下而上，由大到小地叠在一起。各圆盘从小到大编号为1，2，……，n，奇数号圆盘着蓝色，偶数号圆盘着红色，如图所示。现要求将塔座A 上的这一叠圆盘移到塔座B 上，并仍按同样顺序叠置。在移动圆盘时应遵守以下移动规则： 


      规则(1)：每次只能移动1 个圆盘； 


      规则(2)：任何时刻都不允许将较大的圆盘压在较小的圆盘之上； 


      规则(3)：任何时刻都不允许将同色圆盘叠在一起； 


      规则(4)：在满足移动规则(1)-(3)的前提下，可将圆盘移至A，B，C 中任一塔座上。
      
      给定的正整数n
      
*/

#include<iostream>
using namespace std;

void Move(int cnt,char src, char dest){
	cout<<cnt<<" "<<src<<" "<<dest<<endl; 		//将第cnt块圆盘从源位置移动至目标位置 
}

void Hanoi(int cnt,char src,char mid, char dest){
	if(cnt==1)
	{//如果只有一个圆盘，则直接从源位置移动到目标位置 
		Move(1,src,dest);
		return;
	}
	Hanoi(cnt-1,src,dest,mid);	//首先将n-1片移动至中间位置 
	Move(cnt,src,dest);			//再将最大片移动至目标位置 
	Hanoi(cnt-1,mid,src,dest);		//最后再将中间位置的n-1片移动至目标位置 
}


int main(){ 
	int n;
	cin>>n;  //总共有几片 
	Hanoi(n,'A','C','B');	//B未目标位置 
}



//#include<iostream>
//using namespace std;
//void Hannoi(int,char,char,char,int*);
//int num[3];//num[3]为ABC最上方的圆盘编号 
//int main()
//{
///*
//我们为了验证前面的想法，加上一个记录数组，用来记录每挪动
//一次后ABC三个塔座最上方的圆盘编号。如果塔座上没有圆盘，
//则记录为0。
//*/
//	int n;
//	cin>>n;
//	num[0]=1;
//	num[1]=0;
//	num[2]=0;
//	Hannoi(n,'A','B','C',num);
//	return 0;
//} 
//void Move(int i,char M,char N)
//{   //把第i层塔从M位置移动到N位置
//	cout<<i<<' '<<M<<' '<<N<<' ';  
//}
///*
//1、在递归函数里加判断。添加的地方为每次调用Move函数之
//后，即每输出一次挪动记录之后。
//2、因为相同颜色的圆盘的序号都为奇数或者都为偶数，则两个
//颜色相同的圆盘序号相加必为偶数，而两个颜色不同的圆盘序号
//数相加必为奇数。
//3、所以只需要判断圆盘本身的序号数加上要移动到的塔座最上
//方的圆盘序号是否为偶数即可。如果为偶数，就说明此解法错
//误，输出false。此判断还有一个特殊情况就是如果要移动到的塔
//座上没有圆盘，就不用输出false，这是个特例。
//*/
//void Hannoi(int n,char A,char B,char C,int* num)
//{
//	if(n==1)
//	{
//		Move(1,A,B);
//		if((num[A-'A']+num[B-'A'])%2==0&&num[B-'A']!=0){
//			cout<<"false"<<endl;
//		}
//		
//		else{
//			cout<<"true"<<endl;
//		}
//		
//		num[A-'A']=0;
//		num[B-'A']=1;
//		return;
//	}
//	n--;
//	Hannoi(n,A,C,B,num);
//	Move(n+1,A,B);
//	if((num[A-'A']+num[B-'A'])%2==0&&num[B-'A']!=0){
//		cout<<"false"<<endl;
//	}
//	else{
//		cout<<"true"<<endl;
//	}
//	num[A-'A']=0;
//	num[B-'A']=n+1;
//	Hannoi(n,C,B,A,num);
//}





