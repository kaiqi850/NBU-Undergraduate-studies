#include<stdio.h>
#include<string.h>
# define N 10
int main(){
    int n,o[N],i,temp,j;
    for(i=0;i<N;i++)
    {
    	scanf("%d",&o[i]);
	}
	for(i=0;i<N-1;i++)
	{
		for(j=0;j<N-1-i;j++)
		{
			if(o[j]<o[j+1])
			{
				temp=o[j];
				o[j]=o[j+1];
				o[j+1]=temp;
			}
		}
	}
	for(i=0;i<N;i++)
	{
		printf("%d ",o[i]);
	}
	return 0;
}

