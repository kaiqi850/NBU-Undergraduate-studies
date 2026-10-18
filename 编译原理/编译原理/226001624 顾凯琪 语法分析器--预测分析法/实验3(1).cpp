#include<stdio.h>
#include<iostream>
#include<string>
#include<stack>
#include<stdlib.h>
using namespace std;
#define MAX_1 1000
#define MAX_2 100000

//产生式的左右部以及右部的长度
typedef struct production
{
	int left;
	int right[MAX_1];
	int length;
}PRO;

//程序每个字符的对应内码以及所在行数
typedef struct character
{
	string ch;
	int code;
	int row;
}CHAR;

//词法分析时发现的错误
typedef struct error
{
	char ch;
	int row;
}ERR;

//集合结构
typedef struct aggregate
{
	int str[MAX_1];
	int len;
}AGG;

PRO *p=new PRO[MAX_1];//产生式
CHAR chara[MAX_2];//程序字符流
ERR error[MAX_2];//词法分析时发现的错误
AGG First[MAX_1];//用于存放每个非终结符的First集
AGG Follow[MAX_1];//用于存放每个非终结符的Follow集
int NONE[MAX_1]={0};//求每个非终结符的Follow集时避免死循环的变量
AGG Pro_First[MAX_1];//用于存放每个产生式右部的First集
int Table[MAX_1][MAX_1];//预测分析表,-1表示不匹配，-2表示同步符号synch
int N;//产生式的个数
char set[MAX_2];//用于存储初始代码
char str[MAX_2];//用于存储初步处理后的代码
int errorNum=0;//词法分析发现错误数
int errorNum2=0;//语法分析发现错误数
int k=0;//程序字符流数
int Program_row=1;//程序初始行数
stack<int> Stack;//符号栈

//非终结符
string key[15]={"PROGRAM","CONST","VAR","INTEGER","LONG","PROCEDURE","IF","THEN","WHILE","DO","READ","WRITE","BEGIN","END","ODD"};
string punctuation[17]={"+","-","*","/","=","<>","<","<=",">",">=",".",",",";",":",":=","(",")"};

//判断字符串是否是关键字，若是，则返回该关键字对应的内码；若不是，则返回0
int IsKeyWord(string c)
{
	int i;
	for(i=0;i<15;i++)
	{
		if(key[i].compare(c)==0)
			return i+1;
	}
	return 0;
}

//判断字符串c是否是符号，若是，则返回该符号对应的内码；若不是，则返回0
int IsPunctuation(string c)
{
	int i;
	for(i=0;i<17;i++)
	{
		if(punctuation[i].compare(c)==0)
			return i+16;
	}
	return 0;
}

//判断字符c是否是字母，若是，则返回true；若不是，则返回false
bool IsLetter(char c)
{
	if((c>='a'&&c<='z')||(c>='A'&&c<='Z'))
		return true;
	else
		return false;
}

//判断字符c是否是数字，若是，则返回true；若不是，则返回false
bool IsFigure(char c)
{
	if(c>='0'&&c<='9')
		return true;
	else
		return false;
}

//判断该词法错误是否已被检测
bool test(int errorNum,int row,char ch)
{
	int i;
	for(i=0;i<errorNum;i++)
		if(error[i].row ==row&&error[i].ch ==ch)
			return false;
	return true;
}

//词法分析
void lexical_analysis()
{
	FILE *f;
	string tem="";
	char ch;
	int n=0,m=0;//程序代码储存数
	int i;
	if((f=fopen("test.txt","r"))==NULL)
    {
        printf("can not open the file!\n");
        exit(0);
    }
	else
	{
		while(!feof(f))
		{
			ch=getc(f);//getc函数带回一个字符，赋给ch
			set[n]=ch;//将文件的每一个字符都放入set[]数组中
			n++;
		}
	}
	fclose(f);//关闭文件
	set[n-1]='\0';
	i=0;
	while(set[i]!='\0')
	{
		if(set[i]==' ')
		{
			while(set[i]==' ')//扫描到有连续的空格
				i++;
			str[m]=' ';//用一个空格代替扫描到的连续空格放入str[]
			m++;
		}
		else if(set[i]=='\n')
		{
			while(set[i]=='\n')//扫描到有连续的换行符
				i++;
			str[m]='\n';//用一个换行符代替扫描到的连续换行符放入str[]
			m++;
		}
		else
		{
			//若当前字符不为空格或换行符就直接放入str[]
			if(set[i]>='a'&&set[i]<='z')
				str[m]=set[i]-32;
			else
				str[m]=set[i];
			m++;
			i++;
		}
	}
	str[m]='\0';
	//显示源程序
	printf("\n---------------------------源程序显示---------------------------\n\n");
	for(i=0;i<m;i++)
		printf("%c",str[i]);
	printf("\n");
	i=0;
	//将源程序转换成字符流
	for(i=0;i<m;i++)
	{
		tem="";
		if(IsLetter(str[i])||str[i]=='_')
		{
			while(IsLetter(str[i])||IsFigure(str[i])||str[i]=='_')
			{
				tem=tem+str[i];
				i++;
			}
			if(IsKeyWord(tem)>0)
			{
				chara[k].ch=tem;
				chara[k].code=IsKeyWord(tem);
				chara[k].row =Program_row;
				k++;
			}
			else
			{
				chara[k].ch =tem;
				chara[k].code =34;
				chara[k].row =Program_row;
				k++;
			}
		}
		else if(IsFigure(str[i]))
		{
			while(IsFigure(str[i]))
			{
				tem=tem+str[i];
				i++;
			}
			if(IsLetter(str[i]))
			{
				error[errorNum].row=Program_row;
				error[errorNum].ch =str[i];
				errorNum++;
			}
			else
			{
				chara[k].ch=tem;
				chara[k].code=33;
				chara[k].row =Program_row;
				k++;
			}
		}
		tem="";
		tem=tem+str[i];
		switch(str[i])
		{
		case':':
		case'>':
			i++;
			if(str[i]=='=')
				tem=tem+str[i];
			else
				i--;
			chara[k].ch =tem;
			chara[k].code =IsPunctuation(tem);
			chara[k].row =Program_row;
			k++;
			break;
		case'<':
			i++;
			if(str[i]=='='||str[i]=='>')
				tem=tem+str[i];
			else
				i--;
			chara[k].ch =tem;
			chara[k].code =IsPunctuation(tem);
			chara[k].row =Program_row;
			k++;
			break;
		case';':
		case',':
		case'.':
		case'(':
		case')':
		case'+':
		case'-':
		case'*':
		case'/':
		case'=':
			chara[k].ch =tem;
			chara[k].code =IsPunctuation(tem);
			chara[k].row =Program_row;
			k++;
			break;
		case'#':
			chara[k].ch =tem;
			chara[k].code =35;
			chara[k].row =Program_row;
			k++;
			break;
		case' ':
			break;
		case'\n':
			Program_row++;
			break;
		default:
			if(test(errorNum,Program_row,str[i]))
			{
				error[errorNum].row =Program_row;
				error[errorNum].ch =str[i];
				errorNum++;
			}
		}
	}
}

//所有产生式
void production()
{
	N=67;//产生式共有67个
	//128→129 130 26 0
	p[0].left=128;
	p[0].right[0]=129;
	p[0].right[1]=130;
	p[0].right[2]=26;
	p[0].length=3;

	//129→1 34 28 0
	p[1].left=129;
	p[1].right[0]=1;
	p[1].right[1]=34;
	p[1].right[2]=28;
	p[1].length=3;

	//130→131 134 138 150 0
    p[2].left=130;
	p[2].right[0]=131;
	p[2].right[1]=134;
	p[2].right[2]=138;
	p[2].right[3]=150;
	p[2].length=4;

	//131→2 132 133 28 0
	p[3].left=131;
	p[3].right[0]=2;
	p[3].right[1]=132;
	p[3].right[2]=133;
	p[3].right[3]=28;
	p[3].length=4;

	//131→0
	p[4].left=131;
	p[4].right[0]=0;
	p[4].length=1;

	//132→34 20 33 0
	p[5].left=132;
	p[5].right[0]=34;
	p[5].right[1]=20;
	p[5].right[2]=33;
	p[5].length=3;

	//133→27 132 133 0
	p[6].left=133;
	p[6].right[0]=27;
	p[6].right[1]=132;
	p[6].right[2]=133;
	p[6].length=3;

	//133→0
	p[7].left=133;
	p[7].right[0]=0;
	p[7].length=1;

	//134→3 135 136 0
	p[8].left=134;
	p[8].right[0]=3;
	p[8].right[1]=135;
	p[8].right[2]=136;
	p[8].length=3;

	//134→0
	p[9].left=134;
	p[9].right[0]=0;
	p[9].length=1;

	//135→34 147 29 137 28 0
	p[10].left=135;
	p[10].right[0]=34;
	p[10].right[1]=147;
	p[10].right[2]=29;
	p[10].right[3]=137;
	p[10].right[4]=28;
	p[10].length=5;

	//136→135 136 0
	p[11].left=136;
	p[11].right[0]=135;
	p[11].right[1]=136;
	p[11].length=2;

	//136→0
	p[12].left=136;
	p[12].right[0]=0;
	p[12].length=1;

	//137→4 0
	p[13].left=137;
	p[13].right[0]=4;
	p[13].length=1;

	//137→5 0
	p[14].left=137;
	p[14].right[0]=5;
	p[14].length=1;

	//138→139 130 28 140 0
	p[15].left=138;
	p[15].right[0]=139;
	p[15].right[1]=130;
	p[15].right[2]=28;
	p[15].right[3]=140;
	p[15].length=4;

	//138→0
	p[16].left=138;
	p[16].right[0]=0;
	p[16].length=1;

	//139→ 6 34 158 28 0
	p[17].left=139;
	p[17].right[0]=6;
	p[17].right[1]=34;
	p[17].right[2]=158;
	p[17].right[3]=28;
	p[17].length=4;

	//140→139 130 28 140 0
	p[18].left=140;
	p[18].right[0]=139;
	p[18].right[1]=130;
	p[18].right[2]=28;
	p[18].right[3]=140;
	p[18].length=4;

	//140→0
	p[19].left=140;
	p[19].right[0]=0;
	p[19].length=1;

	//141→142 0
	p[20].left=141;
	p[20].right[0]=142;
	p[20].length=1;

	//141→144 0
	p[21].left=141;
	p[21].right[0]=144;
	p[21].length=1;

	//141→145 0
	p[22].left=141;
	p[22].right[0]=145;
	p[22].length=1;

	//141→146 0
	p[23].left=141;
	p[23].right[0]=146;
	p[23].length=1;

	//141→148 0
	p[24].left=141;
	p[24].right[0]=148;
	p[24].length=1;

	//141→150 0
	p[25].left=141;
	p[25].right[0]=150;
	p[25].length=1;

	//141→0
	p[26].left=141;
	p[26].right[0]=0;
	p[26].length=1;

	//142→34 143 0
	p[27].left=142;
	p[27].right[0]=34;
	p[27].right[1]=143;
	p[27].length=2;

	//143→30 153 0
	p[28].left=143;
	p[28].right[0]=30;
	p[28].right[1]=153;
	p[28].length=2;

	//143→31 153 32 0
	p[29].left=143;
	p[29].right[0]=31;
	p[29].right[1]=153;
	p[29].right[2]=32;
	p[29].length=3;

	//143→0
	p[30].left=143;
	p[30].right[0]=0;
	p[30].length=1;

	//144→7 152 8 141 0
	p[31].left=144;
	p[31].right[0]=7;
	p[31].right[1]=152;
	p[31].right[2]=8;
	p[31].right[3]=141;
	p[31].length=4;

	//145→9 152 10 141 0
	p[32].left=145;
	p[32].right[0]=9;
	p[32].right[1]=152;
	p[32].right[2]=10;
	p[32].right[3]=141;
	p[32].length=4;

	//146→11 31 34 147 32 0
	p[33].left=146;
	p[33].right[0]=11;
	p[33].right[1]=31;
	p[33].right[2]=34;
	p[33].right[3]=147;
	p[33].right[4]=32;
	p[33].length=5;

	//147→27 34 147 0
	p[34].left=147;
	p[34].right[0]=27;
	p[34].right[1]=34;
	p[34].right[2]=147;
	p[34].length=3;

	//147→0
	p[35].left=147;
	p[35].right[0]=0;
	p[35].length=1;

	//148→12 31 153 149 32 0
	p[36].left=148;
	p[36].right[0]=12;
	p[36].right[1]=31;
	p[36].right[2]=153;
	p[36].right[3]=149;
	p[36].right[4]=32;
	p[36].length=5;

	//149→27 153 149 0
	p[37].left=149;
	p[37].right[0]=27;
	p[37].right[1]=153;
	p[37].right[2]=149;
	p[37].length=3;

	//149→0
	p[38].left=149;
	p[38].right[0]=0;
	p[38].length=1;

	//150→13 141 151 14 0
	p[39].left=150;
	p[39].right[0]=13;
	p[39].right[1]=141;
	p[39].right[2]=151;
	p[39].right[3]=14;
	p[39].length=4;

	//151→28 141 151 0
	p[40].left=151;
	p[40].right[0]=28;
	p[40].right[1]=141;
	p[40].right[2]=151;
	p[40].length=3;

	//151→0
	p[41].left=151;
	p[41].right[0]=0;
	p[41].length=1;

	//152→153 161 153 0
	p[42].left=152;
	p[42].right[0]=153;
	p[42].right[1]=161;
	p[42].right[2]=153;
	p[42].length=3;

	//152→15 153 0
	p[43].left=152;
	p[43].right[0]=15;
	p[43].right[1]=153;
	p[43].length=2;

	//153→16 155 154 0
	p[44].left=153;
	p[44].right[0]=16;
	p[44].right[1]=155;
	p[44].right[2]=154;
	p[44].length=3;

	//153→17 155 154 0
	p[45].left=153;
	p[45].right[0]=17;
	p[45].right[1]=155;
	p[45].right[2]=154;
	p[45].length=3;

	//153→155 154 0
	p[46].left=153;
	p[46].right[0]=155;
	p[46].right[1]=154;
	p[46].length=2;

	//154→159 155 154 0
	p[47].left=154;
	p[47].right[0]=159;
	p[47].right[1]=155;
	p[47].right[2]=154;
	p[47].length=3;

	//154→0
	p[48].left=154;
	p[48].right[0]=0;
	p[48].length=1;

	//155→157 156 0
	p[49].left=155;
	p[49].right[0]=157;
	p[49].right[1]=156;
	p[49].length=2;

	//156→160 157 156 0
	p[50].left=156;
	p[50].right[0]=160;
	p[50].right[1]=157;
	p[50].right[2]=156;
	p[50].length=3;

	//156→0
	p[51].left=156;
	p[51].right[0]=0;
	p[51].length=1;

	//157→34 0
	p[52].left=157;
	p[52].right[0]=34;
	p[52].length=1;

	//157→33 0
	p[53].left=157;
	p[53].right[0]=33;
	p[53].length=1;

	//157→31 153 32 0
	p[54].left=157;
	p[54].right[0]=31;
	p[54].right[1]=153;
	p[54].right[2]=32;
	p[54].length=3;

	//158→31 34 29 137 32 0
	p[55].left=158;
	p[55].right[0]=31;
	p[55].right[1]=34;
	p[55].right[2]=29;
	p[55].right[3]=137;
	p[55].right[4]=32;
	p[55].length=5;

	//158→0
	p[56].left=158;
	p[56].right[0]=0;
	p[56].length=1;

	//159→16 0
	p[57].left=159;
	p[57].right[0]=16;
	p[57].length=1;

	//159→17 0
	p[58].left=159;
	p[58].right[0]=17;
	p[58].length=1;

	//160→18 0
	p[59].left=160;
	p[59].right[0]=18;
	p[59].length=1;

	//160→19 0
	p[60].left=160;
	p[60].right[0]=19;
	p[60].length=1;

	//161→20 0
	p[61].left=161;
	p[61].right[0]=20;
	p[61].length=1;

	//161→21 0
	p[62].left=161;
	p[62].right[0]=21;
	p[62].length=1;

	//161→22 0
	p[63].left=161;
	p[63].right[0]=22;
	p[63].length=1;

	//161→23 0
	p[64].left=161;
	p[64].right[0]=23;
	p[64].length=1;

	//161→24 0
	p[65].left=161;
	p[65].right[0]=24;
	p[65].length=1;

	//161→25 0
	p[66].left=161;
	p[66].right[0]=25;
	p[66].length=1;
}

//在str[]中查找t,若找到t,则返回t所在的数组下标;否则返回大数，设定该大数为MAX
int search(AGG set,int t)
{
	int i;
	for(i=0;i<set.len;i++)
	{
		if(set.str[i]==t)
			return i;
	}
	return MAX_1;
}

//对每个非终结符A求First集
AGG Character_First(PRO *p,int code)
{
	int k,flag=1;//若某个产生式的右侧字符均为非终结符，且所有非终结符的First集中均含有ε，则flag的值为1

	//遍历所有产生式求该非终结符A的First集
    for(int i=0;i<N;i++)
    {
        if(p[i].left==code)//在产生式的左部找到该非终结符A
        {
            if(p[i].right[0]>=1&&p[i].right[0]<=35)//该非终结符A所在的产生式的右侧第一个字符是终结符，则将此终结符加入该非终结符的First集
            {
				if(search(First[code],p[i].right[0])==MAX_1)//该非终结符A的First集无此终结符，则将此终结符加入该非终结符的First集
                {
					First[code].str[First[code].len]=p[i].right[0];
					First[code].len++;
				}
            }
			if(p[i].right[0]==0)//该非终结符所在的产生式的右侧是ε，则将此终结符加入该非终结符的First集
            {
				if(search(First[code],p[i].right[0])==MAX_1)
                {
					First[code].str[First[code].len]=p[i].right[0];
					First[code].len++;
				}
            }
            if(p[i].right[0]>=128&&p[i].right[0]<=161)//该非终结符A所在的产生式的右侧第一个字符是非终结符
            {
                if(p[i].length==1)//该非终结符A所在的产生式的右侧仅有一个非终结符B,则将非终结符B的First集加入到非终结符A的First集
                {
                    AGG set1;
					set1.len=0;
                    set1=Character_First(p,p[i].right[0]);
                    for(int j=0;j<set1.len;j++)
                    {
						if(search(First[code],set1.str[j])==MAX_1)
						{
							First[code].str[First[code].len]=set1.str[j];
							First[code].len++;
						}
                    }
                }
                else//该非终结符A所在的产生式的右侧符号数大于1
                {
                    for(int j=0;j<p[i].length;j++)
                    {
                        AGG set;
						set.len=0;
                        if(p[i].right[j]>=128&&p[i].right[j]<=161)//该非终结符A所在的产生式的右侧第j符号为非终结符
                        {
                            set=Character_First(p,p[i].right[j]);
                            if(search(set,0)<MAX_1)//非终结符p[i].right[j]的First集中含有ε
                            {
                                for(k=0;k<set.len;k++)
                                {
                                    if(search(First[code],set.str[k])==MAX_1&&set.str[k]!=0)//将非终结符p[i].right[j]的First集中除ε之外的元素均加入所求非终结符A的First集中
									{
										First[code].str[First[code].len]=set.str[k];
										First[code].len++;
									}
                                }
                            }
                            else//非终结符p[i].right[j]的First集中不含ε
                            {
                                flag=0;
                                for(k=0;k<set.len;k++)
                                {
                                    if(search(First[code],set.str[k])==MAX_1)//将非终结符p[i].right[j]的First集中所有元素均加入所求非终结符A的First集中
                                    {
										First[code].str[First[code].len]=set.str[k];
										First[code].len++;
									}
                                }
                                break;
                            }
                        }
                        else//该非终结符所在的产生式的右侧符号中遇到终结符
                        {
                            flag=0;
                            if(search(First[code],p[i].right[j])==MAX_1)
							{
								First[code].str[First[code].len]=p[i].right[j];
								First[code].len++;
							}
                            break;
                        }
                    }

					//该非终结符所在的产生式的右侧符号均为非终结符，且所有非终结符的First集中均含有ε，则将0加入该非终结符的First集中,其中0表示空集ε
                    if(flag==1)
					{
						First[code].str[First[code].len]=0;
						First[code].len++;
					}
                }
            }
        }
    }
	return First[code];
}

//求每个非终结符A的Follow集
AGG Character_Follow(PRO *p,int code)
{
	int t,k,flag=1;//若该非终结符A的右侧字符均为非终结符，且所有非终结符的First集中均含有ε，则flag的值为1
	NONE[code]++;//避免死循环的变量值自增
	if(NONE[code]==2)//当出现所求非终结符的Follow集需要将自身加入时，将避免死循环的变量值设为0，并跳出死循环
    {
		NONE[code]=0;
		return Follow[code];
    }

	//遍历所有产生式求该非终结符A的Follow集
    for(int i=0;i<N;i++)
    {
		for(int j=0;j<p[i].length;j++)
		{
			if(p[i].right[j]==code)//在产生式的右部找到该非终结符A
			{
				if(j+1==p[i].length)//该非终结符A在其所在的产生式的最右侧
				{
					AGG set1;
					set1.len=0;
					set1=Character_Follow(p,p[i].left);
					for(k=0;k<set1.len;k++)
					{
 					if(search(Follow[code],set1.str[k])==MAX_1)//该非终结符A的Follow集无此终结符，则将此终结符加入该非终结符A的Follow集
						{
							Follow[code].str[Follow[code].len]=set1.str[k];
							Follow[code].len++;
						}
					}
				}
				else//该非终结符A不在其所在的产生式,即非终结符A的右侧还有符号
				{
					AGG set2;
					set2.len=0;
					for(int q=j+1;q<p[i].length;q++)
					{
						AGG set3;
						set3.len=0;
						if(p[i].right[q]>=1&&p[i].right[q]<=35)//该非终结符A右侧的符号是终结符
						{
							flag=0;
							if(search(set2,p[i].right[q])==MAX_1)
							{
								set2.str[set2.len]=p[i].right[q];
								set2.len++;
							}
							break;
						}
						else if(p[i].right[q]>=128&&p[i].right[q]<=161)//该非终结符A右侧的符号是非终结符
						{
							set3=Character_First(p,p[i].right[q]);
							if(search(set3,0)<MAX_1)//该非终结符A右侧的非终结符p[i].right[q]的First集中含有ε
							{
								for(t=0;t<set3.len;t++)
								{
									if(search(set2,set3.str[t])==MAX_1&&set3.str[t]!=0)//将非终结符p[i].right[q]的First集中除ε之外的元素均加入set2集中
									{
										set2.str[set2.len]=set3.str[t];
										set2.len++;
									}
								}
							}
							else//该非终结符A右侧的非终结符p[i].right[q]的First集中不含有ε
							{
								flag=0;
								for(t=0;t<set3.len;t++)
								{
									if(search(set2,set3.str[t])==MAX_1)//将非终结符p[i].right[q]的First集中所有元素均加入set2集中
									{
										set2.str[set2.len]=set3.str[t];
										set2.len++;
									}
								}
								break;
							}
						}
					}

					//该非终结符所在的产生式的右侧符号均为非终结符，且所有非终结符的First集中均含有ε，则将0加入set2集中,其中0表示空集ε
					if(flag==1)
					{
						set2.str[set2.len]=0;
						set2.len++;
					}
					if(search(set2,0)==MAX_1)//set2集中不含ε，则将set2集中的所有元素均加入该非终结符A的Follow集中
					{
						//B->aAC,把First(C)去掉ε加入到Follow(A)中(First(C)不含ε)
						for(k=0;k<set2.len;k++)
						{
							if(search(Follow[code],set2.str[k])==MAX_1)
							{
								Follow[code].str[Follow[code].len]=set2.str[k];
								Follow[code].len++;
							}
						}
					}
					else//set2集中含有ε，则将set2集中除ε之外的元素均加入该非终结符A的Follow集中
					{
						//B->aAC,把First(C)去掉ε加入到Follow(A)中(First(C)含ε)
						for(k=0;k<set2.len;k++)
						{
							if((search(Follow[code],set2.str[k])==MAX_1)&&set2.str[k]!=0)
							{
								Follow[code].str[Follow[code].len]=set2.str[k];
								Follow[code].len++;
							}
						}
						//B->aAC,ε在First(C)中，把Follow(B)加入到Follow(A)中
						AGG set4;
						set4.len=0;
						set4=Character_Follow(p,p[i].left);
						for(k=0;k<set4.len;k++)
						{
							if(search(Follow[code],set4.str[k])==MAX_1)
							{
								Follow[code].str[Follow[code].len]=set4.str[k];
								Follow[code].len++;
							}
						}
					}
				}
			}
		}
	}
	return Follow[code];
}

//求所有非终结符的First集
void Keep_Character_First()
{
	int i=0;
	for(i=128;i<=161;i++)
	{
		AGG set;
		set.len=0;
        set=Character_First(p,i);
	}
}

//求所有非终结符的Follow集
void Keep_Character_Follow()
{
	int i;
	for(i=128;i<=161;i++)
	{
		AGG set;
		set.len=0;
        set=Character_Follow(p,i);
	}
}

//求每个产生式右部的First集
void Production_First()
{
	int i,j,k;
	int flag=1;
	//遍历所有产生式,求每个产生式右部的First集
	for(i=0;i<N;i++)
	{
		Pro_First[i].len=0;
		int flag=0;//求Pro_First集结束标志,flag=1表示Pro_First集已经求完

		//遍历产生式p[i]的所有右部
		for(j=0;j<p[i].length;j++)
		{
			if(p[i].right[j]>=1&&p[i].right[j]<=35)//p[i].right[j]符号是终结符
			{
				if(search(Pro_First[i],p[i].right[j])==MAX_1)
				{
					Pro_First[i].str[Pro_First[i].len]=p[i].right[j];
					Pro_First[i].len++;
				}
				flag=1;
			}
			else//p[i].right[j]符号是非终结符或ε
			{
				//将非终结符p[i].right[j]的First集中除ε之外的元素均加入该产生式p[i]右部的Pro_First集中
				for(k=0;k<First[p[i].right[j]].len;k++)
				{
					if(First[p[i].right[j]].str[k]!=0)
					{
						if(search(Pro_First[i],First[p[i].right[j]].str[k])==MAX_1)
						{
							Pro_First[i].str[Pro_First[i].len]=First[p[i].right[j]].str[k];
							Pro_First[i].len++;
						}
						flag=1;
					}
					else
						flag=0;
				}
			}
			if(flag==1)
				break;
			if(flag==0&&j==p[i].length-1)//该产生式p[i]的最右部为非终结符且该非终结符的First集含ε或该产生式p[i]的最右部为ε
			{
				Pro_First[i].str[Pro_First[i].len]=0;
				Pro_First[i].len++;
			}
		}
	}
}

//构造预测分析表
void Structura_Table()
{
	int i,j,k,t,q;
	int flag;//标志，flag=0表示产生式的First集中不包含ε
	//初始化
	for(i=0;i<=34;i++)
		for(j=0;j<=35;j++)
			Table[i][j]=-1;
	//预测表的第一行为终结符的内码
	for(i=1;i<=35;i++)
		Table[0][i]=i;
	//预测表的第一列为非终结符的内码
	for(j=1;j<=34;j++)
		Table[j][0]=j+127;
 	for(k=0;k<N;k++)
	{
		flag=0;
		for(t=0;t<Pro_First[k].len;t++)
		{
			if(Pro_First[k].str[t]!=0)  //若产生式k的First集中的第t个元素α不是ε，则在预测表中该产生式左部的非终结符A对应的α列下填上该产生式k
				Table[p[k].left-127][Pro_First[k].str[t]]=k;
			else   //若产生式k的First集中的第t个元素α是ε，则需参考该产生式左部的非终结符A的Follow集
			{
				flag=1;
				for(q=0;q<Follow[p[k].left].len;q++)//该产生式左部的非终结符A的Follow集的第q个元素β，在预测表中该产生式左部A的非终结符对应的β列下填上该产生式k
					Table[p[k].left-127][Follow[p[k].left].str[q]]=k;
			}
		}
		//添上同步符号
		if(flag==0)
			for(t=0;t<Follow[p[k].left].len;t++)
				Table[p[k].left-127][Follow[p[k].left].str[t]]=-2;
	}
}

//语法分析
void grammatical_analysis()
{
	int a,X,t,i,j;
	Stack.push(35);//'#'入栈
	chara[k].ch ="#";
	chara[k].code =35;
	chara[k].row =Program_row;
	Stack.push(128);//<程序>入栈
	i=0;
	while(!Stack.empty()&&i<=k)
	{
		a=chara[i].code;
		//printf("a=%d ",a);
		X=Stack.top();
		//printf("X=%d ",X);
		Stack.pop();
		
		{
			if(X==a)
			{
				if(X==35)
					return;
				i++;
			}
		
		}
	}
}
int main()
{
	int i,j;
	production();
	Follow[128].str[0]=35;  //初始符的Follow集加入'#',即35
	Follow[128].len =1;
	Keep_Character_First(); //求所有非终结符的First集
	Keep_Character_Follow(); //求所有非终结符的Follow集
    Production_First();  //求每个产生式右部的First集
	Structura_Table();  //构造预测分析表

	printf("---------------------First集----------------------\n");
    for(i=128;i<=161;i++)
    {
		printf("%d={",i);
        for(j=0;j<First[i].len-1;j++)
            printf("%d,",First[i].str[j]);
        printf("%d}\n",First[i].str[First[i].len-1]);
    }

	printf("-----------------------Follow集-----------------------\n");
    for(i=128;i<=161;i++)
    {
		printf("%d={",i);
        for(j=0;j<Follow[i].len-1;j++)
            printf("%d,",Follow[i].str[j]);
        printf("%d}\n",Follow[i].str[Follow[i].len-1]);
    }

	printf("-------------Pro_First集-------------\n");
    for(i=0;i<N;i++)
    {
        printf("%d={",i);
        for(j=0;j<Pro_First[i].len-1;j++)
            printf("%d,",Pro_First[i].str[j]);
        printf("%d}\n",Pro_First[i].str[Pro_First[i].len-1]);
    }
	lexical_analysis();
	/*for(i=0;i<k;i++)
		printf("%d ",chara[i].code);
	printf("\n");*/
	printf("\n---------------------------词法分析---------------------------\n");
	printf("\n词法分析共查找到 %d 个错误\n",errorNum);
	if(errorNum>0){
	}
		
	else
	{
		printf("\n---------------------------语法分析---------------------------\n");
		grammatical_analysis();
		printf("\n语法分析共查找到 0 个错误");
	}
	return 0;
}
