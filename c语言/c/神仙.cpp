#include<stdio.h>
int main()
{
	char o[14];
	int sum=0,i,n,j=1;
	while(gets(o))
	{
		sum=0;
		j=1;
		for(i=0;i<12;i++)
		{
			if(o[i]!='-')
			{
				sum=sum+(o[i]-'0')*j++;
			}
		}
		sum=sum%11;
	
		if(sum==10)
		{
			if(o[12]=='X')
			{
				printf("Right\n");
			}
			else
			{
				printf("X\n");
			}
		}
		else
		{
			if(o[12]-'0'==sum)
			{
				printf("Right\n");
			}
			else
			{
				printf("%d\n",sum);
			}
		}
	}
	
	return 0;
}

