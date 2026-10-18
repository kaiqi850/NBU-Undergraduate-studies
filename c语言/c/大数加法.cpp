#include<stdio.h>
#include<stdlib.h>
#include<time.h>
#include<math.h>
#define N 5
#include<string.h>
int main()
{ 
    char sa[1002],sb[1002];
    int a[1002]={0},b[1002]={0};
    int i,j,lena,lenb,len,c=0;
    
    gets(sa); gets(sb);
    lena=strlen(sa);
    lenb=strlen(sb);
    j=0;
    for(i=lena-1;i>=0;i--)
    a[j++]=sa[i]-'0';
    j=0;
    for(i=lenb-1;i>=0;i--)
    b[j++]=sb[i]-'0';
    if(lena>=lenb)
    len=lena;
    else
    len=lenb;
    
    for(i=0;i<len;i++)
    {
    	a[i]=a[i]+b[i]+c;
    	if(a[i]>=10)
    	{
    		a[i]=a[i]%10;
    		c=1;
		}
		else c=0;
	}
	if(c==1)
	{
		a[len]=1;
		len++;
	}
	
	for(i=len-1;i>=0;i--)
	{
		printf("%d",a[i]);
	}
    return 0;
}
