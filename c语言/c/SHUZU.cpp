#include<stdio.h>
#include<string.h>
# define N 5
int main(){
    int j,i,n,key,o[N];
    for(i=0;i<N;i++)
    scanf("%d",&o[i]);
    while(scanf("%d",&key)!=EOF)
    {
    	
    for(i=0;i<N&&o[i]!=key;i++);
    if(i==N){
	
    printf("not found\n");
    return 0;}
    else
    for(j=i;j<N-1;j++)
    {
    	o[j]=o[j+1];
	}
	for(i=0;i<N-1;i++)
	{
		printf("%d ",o[i]);
	}
	printf("\n");	
	}
    
	return 0;
}

