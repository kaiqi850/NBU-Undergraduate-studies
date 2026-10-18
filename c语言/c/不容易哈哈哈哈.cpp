#include<cstdio>
#include<cmath>
#include<cstring>
#include<cctype>
int pan(int x,int *p,int n)
{
	int i,j,flag=0;
	for(i=0;i<n;i++)
	{
		if(x==p[i])
		{
			return 0;
			
		}
		
		
		
	}
	if(flag==0)
	return 1;
}
int main()
{
   int j,m,temp,o[1000],b[100],i=0,count=0,*p=b;
   scanf("%d",&o[0]);
   while(o[i]!=0)
   {
   	  count++;
   	  
   	  scanf("%d",&o[++i]);
   }
   for(i=0,j=0;i<count;i++)
   {
   	   if(pan(o[i],b,j))
   	   {
   	   	b[j++]=o[i];
		  }
   }
   
   for(i=0;i<j;i++)
   {
   	
   	for(m=0;m<j-i-1;m++)
   	{
   		if(b[m]>b[m+1])
   		{
   			temp=b[m];
   			b[m]=b[m+1];
   			b[m+1]=temp;
   			
		   }
	   }
   }
   for(i=0;i<j;i++)
   {
   	printf("%d\n",b[i]);
   }
}
 
