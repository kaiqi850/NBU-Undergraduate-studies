#include<iostream> 

using namespace std;

int a[105];
int n,sum,cnt,avg;

void generate(){
	sum=0;
    cnt=0;
    cin>>n;
    for(int i=0;i<n;i++)
    {
        cin>>a[i];
        sum +=a[i] ;
    }
    avg=sum/n;
    for(int i=0;i<n;i++)
    {
        a[i]=a[i]-avg;
    }
}

int main()
{
	generate();
    for(int i=0;i<n-1;i++)
    {
        if(a[i]!=0)  //如果等于0的话就不用管了；
        {
            a[i+1]=a[i]+a[i+1];
            a[i]=0;
            cnt++;
        }
        else
            continue;
    }
    if(a[n-1]==0)
    	cout<<cnt<<endl;
    else
    	cout<<-1<<endl;
    return 0;
}
