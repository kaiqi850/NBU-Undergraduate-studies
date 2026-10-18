#include<cstdio>
#include<cstring>

int main()
{
   int i,x,j,n,dig[10]={0};
   scanf("%d",&n);
   for(i=0;i<n;i++)
   {
   	scanf("%d",&x);
   	dig[x]++;
   } 
   
   for(i=1;i<10;i++)
   if(dig[i]>0)
   {
   printf("%d",i);
   dig[i]--;
   break;}
   for(i=0;i<n-1;i++)
   {
   	for(j=0;j<10;j++)
   	{
   		if(dig[j]>0)
   		{
   		   printf("%d",j);
			  dig[j]--;
			  break;	
		}
	}
   }
   printf("\n"); 
    return 0;
}
 
 
