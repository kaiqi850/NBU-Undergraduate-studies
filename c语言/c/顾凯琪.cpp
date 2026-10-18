#include<stdio.h>
#include<math.h>
#include<string.h>
#include<time.h>
#include<stdlib.h>
int main()
{
	int n,a,b,i,c,m,bai=0,flag=0,lag=0;
	double count=0;
	srand((unsigned)time(NULL));     //以时间作为随机数，保证随机 
	printf("****四则运算--小学生版****\n");
	printf(" \n");
	
	while(1){
	printf("1.简单的加法运算\n");
	printf("2.简单的减法运算\n");
	printf("3.简单的乘法运算\n");
	printf("4.简单的除法运算\n"); 
	printf("5.我不玩啦\n"); 
	printf(" \n");
	printf("请在1~5中做出你的选择\n");    //主菜单界面，利用while确保循环 
	
	scanf("%d",&n);  //用户输入选项 
	printf(" \n");
	
	switch(n)
	{
		case 1:
			printf("请华丽地进行加法运算\n");
			printf("\n"); 
			n=rand() % 10+1;   //产生随机n道题目 
			printf("本次的题目共有%d道呦\n",n);  //提示用户题目数量 
			for(i=1;i<=n;i++)
			{
			a = rand() % 100;
			b = rand() % 100;    //产生a和b两个随机数作为题目题干 
			c=a+b;    //自行计算题目结果 
		    printf("%d+%d=\n",a,b);
		    scanf("%d",&m);   
		    if(m==c)
		      {
		    	printf("斯国一,Very Good\n");
		    	printf(" \n");
		    	count+=1.0;    //比较用户的答案和正确答案 
			  }
			else
			  {printf("\n");
			  	printf("就差一点了，再试一次呗\n");
			  	printf("%d+%d=\n",a,b);
		        scanf("%d",&m);   //给予用户第二次计算机会 
		        if(m==c)
		        {
		        	printf("斯国一,Very Good\n");
		        	printf(" \n");
		        	count+=1.0;
				}
				else
				{
					printf("Wrong!!!\n");
					printf(" \n");
				}
			  }
			}
			bai=count/n*100;
			printf("本次的正确率是%%");
			printf("%d\n",bai);
			printf("------------------\n");    //计算本次运算正确率 
			break; 
		case 2:
			printf("请华丽地进行减法运算\n");
			printf("\n"); 
			n=rand() % 10+1;
			printf("本次的题目共有%d道呦\n",n);
			for(i=1;i<=n;i++)
			{
			a = rand() % 100;
			b = rand() % 100;
			c=a-b;
		    printf("%d-%d=\n",a,b);
		    scanf("%d",&m);
		    if(m==c)
		      {
		    	printf("斯国一,Very Good\n");
		    	printf(" \n");
		    	count+=1.0;
			  }
			else
			  { printf(" \n");
			  	printf("就差一点了，再试一次呗\n");
			  	printf("%d-%d=\n",a,b);
		        scanf("%d",&m);
		        if(m==c)
		        {
		        	printf("斯国一,Very Good\n");
		        	printf(" \n");
		        	count+=1.0;
				}
				else
				{
					printf("Wrong!!!\n");
					printf(" \n");
				}
			  }
			}
			bai=count/n*100;
			printf("本次的正确率是%%");
			printf("%d\n",bai);
			printf("------------------\n");
			break; 
		case 3:
			printf("请华丽地进行乘法运算\n");
			printf("\n"); 
			n=rand() % 10+1;
			printf("本次的题目共有%d道呦\n",n);
			for(i=1;i<=n;i++)
			{
			a = rand() % 100;
			b = rand() % 100;
			c=a*b;
		    printf("%d*%d=\n",a,b);
		    scanf("%d",&m);
		    if(m==c)
		      {
		    	printf("斯国一,Very Good\n");
		    	printf(" \n");
		    	count+=1.0;
			  }
			else
			  {printf(" \n");
			  	printf("就差一点了，再试一次呗\n");
			  	printf("%d*%d=\n",a,b);
		        scanf("%d",&m);
		        if(m==c)
		        {
		        	printf("斯国一,Very Good\n");
		        	printf(" \n");
		        	count+=1.0;
				}
				else
				{
					printf("Wrong!!!\n");
					printf(" \n");
				}
			  }
			}
			bai=count/n*100;
			printf("本次的正确率是%%");
			printf("%d\n",bai);
			printf("------------------\n");
			break; 
		case 4:
			printf("请华丽地进行除法运算\n");
			printf("\n"); 
			printf("温馨提示：无法整除时，仅需输入整数部分\n");
			n=rand() % 10+1;
			printf("本次的题目共有%d道呦\n",n);
			for(i=1;i<=n;i++)
			{
			a = rand() % 100;
			b = rand() % 9+1;  //+1操作保证分母不为0，且分母为1~9的个位数 
			c=a/b;
		    printf("%d/%d=\n",a,b);
		    scanf("%d",&m);
		    if(m==c)
		      {
		    	printf("斯国一,Very Good\n");
		    	printf(" \n");
		    	count+=1.0;
			  }
			else
			  {printf(" \n");
			  	printf("就差一点了，再试一次呗\n");
			  	printf("%d/%d=\n",a,b);
		        scanf("%d",&m);
		        if(m==c)
		        {
		        	printf("斯国一,Very Good\n");
		        	printf(" \n");
		        	count+=1.0;
				}
				else
				{
					printf("Wrong!!!\n");
					printf(" \n");
				}
			  }
			}
			bai=count/n*100;
			printf("本次的正确率是%%");
			printf("%d\n",bai);
			printf("------------------\n");
			break; 
		case 5:
			lag=1;
			break;   //以lag作为标志符号，若输入5，则退出程序 
		default:
		    printf("请输入正确数字\n");   //若输入其他数字，则提醒用户重新输入 
	}
	   if(lag)
	   break;   //退出程序 
	}
	
	return 0;
}

