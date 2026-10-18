/*
第1行包括一个整数w，为每组模拟成绩之和的上限；
第2行为一个整数n，表示参加模拟测试的学生总数；
第3-n+2行每行包含一个正整数g (0 <= g <= 100)表示所对应学生的模拟测试成绩。

仅1行，包含一个整数，表示最少的分组数目
*/ 

#include<iostream>
#include<algorithm>
using namespace std;
int num[30010];	 //定义数组用于存储学生成绩 
int main(){
    int w,n,ans=0;	//w为成绩合上限，n为学生数，ans为分组数 
    cin>>w>>n;			//输入数据 
    for(int i=0;i<n;i++)
        cin>>num[i];
    sort(num,num+n);	//按学生成绩进行排序 
    int i=0,j=n-1;	//初始化两个指针，一个指向成绩最低的学生，一个指向成绩最高的学生 
    while (i<=j){	//遍历所有学生 
        if(num[j]+num[i]<=w){	//判断二者之和是否超过上限 
            ans++;	//若未超过则分组数增加，两个指针同时向中间移动 
            j--;
            i++;
        }else{		//若超过则仅仅只移动成绩高的指针，分组数增加 
            ans++;
            j--;
        }
    }
    cout<<ans<<endl;
    return 0;
}

