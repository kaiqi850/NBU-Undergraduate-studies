/*
输入有一行，先输入数字串m，再输入k，如描述所示。
保证数字串m没有前导0。

输出有两行，第一行按顺序输出从左到右删除的k个数字，用空格隔开。
注：第一行里的输出顺序是按照被删除数字在原数中的顺序排列的，而不是按照删除的顺序排列的
第二行输出删除k个数字后剩下的数字组成的新数，并换行。
*/
#include <iostream>
#include <string>
using namespace std;


void solve(){
	string num,num1;	//num用于存储原始数字串，num1用于存储原始数字串的副本 
	int ans;			//ans表示每次要删除的数字个数 
	int cnt=0;			//cnt用来计算每次已经删除的数字个数 
	while(cin>>num>>ans)
    {
        num1=num;
        cnt=0;//计数要减的个数
        int t;
        while(cnt<ans)	 
        {
            int flag=0;
            for(int i=0; i<num.size()-1; i++)	//遍历数字串，寻找可删除的数字 
            {

                if(num[i]>num[i+1])				//有递减则删除前一个大数 
                {
                    cnt++;
                    num.erase(i,1);
                    flag=1;
                    break;
                }
            }
            if(flag==0)				//全都一样或全部递增，去除末尾
            {
                cnt++;
                num=num.erase(num.size()-1,1);
            }
        }
        int i = 0;
        for(int j=0; j<num1.size(); j++) //遍历num1副本来输出已经删除的数 
        {
            if(i<num.size()&&num[i]==num1[j])	//num1中的数字在当前num中也存在 
            {
                i++;
            }
            else
            {
                if(cnt==1)		//如果只剩下一个数字， 则直接输出该数字并进行换行 
                    cout<<num1[j]<<endl;
                else			//否则，则空格输出，并将cnt的值减一 
                    cout<<num1[j]<<" ",cnt--;
            }
        }
        cout<<num<<endl;	//输出删除k个数字后剩下的数字 
    }
}

int main()
{
	solve();
	return 0;
}


