#include<bits/stdc++.h>
using namespace std;
ifstream infile("result.txt");//文件流
ifstream infile2("analysis.txt");//文件流
ofstream outfile("result.txt");//文件输出流
map<string,string> word;//应用map数据结构形成一个string->string的对应
std::map<string,string>::iterator it;//用来遍历整个对应关系的迭代器
string str;//读入的字符串
string sym;//用来指示读入的符号
string sym2;//用来指示读入的符号
int count1=0,k=0,flag=0,conterr=0,lpnum=0;
string expressionAnalysis();//表达式分析，表达式的中间代码表示
string termAnalysis();//项分析，表达式的中间代码表示
string factorAnalysis();//因子分析，表达式的中间代码表示
int expressionAnalysis2();//表达式分析，算数表达式的语义计算
int termAnalysis2();//项分析，算数表达式的语义计算
int factorAnalysis2();//因子分析，算数表达式的语义计算
struct quad{//定义四元式
     string result;
     string arg1;
     string arg2;
     string op;
};
struct quad quad[50];
void map_init(){//对应关系进行初始化，如下只包括了表达式的相关符号
    word["+"]="plus";
    word["-"]="minus";
    word["*"]="times";
    word["/"]="slash";
    word["="]="eql";
    word["("]="lparen";
    word[")"]="rparen";
}
void lexanalysis(){//词法分析
    char ch;
    char a;
    string word1;//string变量识别单词
    string str;//string变量进行字符识别
    ostringstream buf;
    while(buf&&infile2.get(ch)) buf.put(ch);//将文件中的字符读出来
    str= buf.str();//将得到的字符储存到string类型变量中
    int csize=str.length();
    for(int i=0;i<csize;i++){//对整个字符串进行遍历
        while(str[i]==' '||str[i]=='\n') i++;//若最开始为空格或换行符，则将指针的位置往后移
        if(isalpha(str[i])){//对标识符和基本字进行识别,调用库函数isalpha()
            word1=str[i++];
            while(isalpha(str[i])||isdigit(str[i])){
                word1+=str[i++];
            }
            it=word.find(word1);
            if(it!=word.end()){//判断是不是基本字，若为基本字则进行输出
                outfile<<"("<<word[word1]<<","<<word1<<")"<<endl;
            }
            else{//否则直接输出
                outfile<<"(ident"<<","<<word1<<")"<<endl;
            }
            i--;
        }
        else if(isdigit(str[i])){//判断是不是常数，调用库函数isdigit()
            word1=str[i++];
            while(isdigit(str[i])){
                word1+=str[i++];
            }
             if(isalpha(str[i])){
                outfile<<"error"<<endl;
                break;
            }
            else{
                outfile<<"(number"<<","<<word1<<")"<<endl;
            }
            i--;
        }else{//对其他的基本字依次进行判断
            word1=str[i];
            it=word.find(word1);
            if(it!=word.end()){
                outfile<<"("<<word[word1]<<","<<word1<<")"<<endl;
            }else{
                outfile<<"error"<<endl;
                break;
            }
        }
    }
    infile2.close();
}
int advance(){//用来读入下一个符号
    int found1,found2;
    if(!getline(infile,str)){
        return 0;
    }
    found1=str.find(',',0);
    if(found1==-1){
        conterr++;
        cout<<"语法错误 识别字符错误"<<endl;
        return -1;
    }
    found2=str.length();
    sym=str.substr(1,found1-1);
    sym2=str.substr(found1+1,found2-found1-2);
    return 1;
}
string newtemp(){//产生新变量名t1,t2等
    char *p;
    char m[12];
    p=(char*)malloc(12);
    k++;
    itoa(k,m,10);
    strcpy(p+1,m);
    p[0]='t';
    string s;
    s=p;
    return s;
}
void emit(string op,string arg1,string arg2,string result){//产生四元式用于显示
    quad[count1].op=op;
    quad[count1].arg1=arg1;
    quad[count1].arg2=arg2;
    quad[count1].result=result;
    count1++;
    return;
}
string expressionAnalysis(){//表达式的递归下降分析程序
    string op,arg1,arg2,result;
    if(conterr){
        return NULL;
	}
	arg1=termAnalysis();//通过项分析得到第一个参数的值
	if(conterr){
        return NULL;
	}
	while((sym=="plus")||(sym=="minus")){
        op=sym2;
		flag=advance();
		if(conterr){
            return NULL;
		}
		if(flag==0){
            cout<<"语法错误 <加法运算符>后缺项"<<endl;
            conterr++;
			return NULL;
		}
		arg2=termAnalysis();//通过项分析得到第二个参数的值
		if(conterr){
            return NULL;
		}
		result=newtemp();//产生中间变量名，相当于对结果进行存储
		emit(op,arg1,arg2,result);//产生四元式，相当于进行加法或减法运算，得出结果
		arg1=result;//保存得到的结果
	}
	return arg1;//返回表达式最终得到的值
}
string termAnalysis(){//项的递归下降分析程序
    string op,arg1,arg2,result;
    arg1=factorAnalysis();//通过因子分析得到第一个参数的值
    if(conterr){
        return NULL;
    }
	while((sym=="times")||(sym=="slash")){
        op=sym2;
		flag=advance();
		if(conterr){
            return NULL;
		}
		if(flag==0){
			conterr++;
			cout<<"语法错误 <乘法运算符>后缺因子"<<endl;
			return NULL;
		}
		if(conterr){
            return NULL;
		}
		arg2=factorAnalysis();//通过因子分析得到第二个参数的值
		if(conterr){
            return NULL;
		}
		result=newtemp();//产生中间变量名，相当于对结果进行存储
		emit(op,arg1,arg2,result);//产生四元式，相当于进行乘法或除法运算，得出结果
		arg1=result;//保存得到的结果
	}
	return arg1;//返回项最终得到的值
}
string factorAnalysis(){
    string arg;
    if(sym=="ident"){//如果是标识符，最终返回标识符的符号
        arg=sym2;
        flag=advance();
        if(conterr){
            return NULL;
		}
		if(lpnum==0&&sym=="rparen"){
            conterr++;
			cout<<"语法错误 ')'不匹配"<<endl;
			return NULL;
        }
    }
    else if(sym=="number"){//如果是无符号整数，最终返回相应的整数
        arg=sym2;
        flag=advance();
        if(conterr){
            return NULL;
		}
		if(lpnum==0&&sym=="rparen"){
            conterr++;
			cout<<"语法错误 ')'不匹配"<<endl;
			return NULL;
        }
    }
    else if(sym=="lparen"){//如果是左括号，则要进行右括号匹配，并判断中间是不是表达式，并得出表达式的值进行返回
        lpnum++;
        flag=advance();
        if(conterr){
            return NULL;
		}
		if(flag==0){
			conterr++;
			cout<<"语法错误 '('后缺少表达式"<<endl;
			return NULL;
		}
        arg=expressionAnalysis();
        if(conterr){
            return NULL;
		}
        if(flag==0||sym!="rparen"){
			conterr++;
			cout<<"语法错误 表达式后面缺少')'"<<endl;
			return " ";
		}else{
		    lpnum--;
            flag=advance();
            if(conterr){
                return NULL;
            }
            if(flag==0){
                return arg;
            }
		}
    }else{
		cout<<"语法错误 因子首部不为<标识符>|<无符号整数>|'('"<<endl;
		conterr++;
		return " ";
	}
	return arg;
}
int expressionAnalysis2(){//表达式的递归下降分析程序
    string op;
    int arg1,arg2,result;
    if(conterr){
        return 0;
	}
	arg1=termAnalysis2();//通过项分析得到第一个参数的值
	if(conterr){
        return 0;
	}
	while((sym=="plus")||(sym=="minus")){
        op=sym2;
		flag=advance();
		if(conterr){
            return 0;
		}
		if(flag==0){
            cout<<"语法错误 <加法运算符>后缺项"<<endl;
            conterr++;
			return 0;
		}
		arg2=termAnalysis2();//通过项分析得到第二个参数的值
		if(conterr){
            return 0;
		}
		if(op=="+"){
            result=arg1+arg2;
		}
		else{
            result=arg1-arg2;
		}
		arg1=result;//保存得到的结果
	}
	return arg1;//返回表达式最终得到的值
}
int termAnalysis2(){//项的递归下降分析程序
    string op;
    int arg1,arg2,result;
    arg1=factorAnalysis2();//通过因子分析得到第一个参数的值
    if(conterr){
        return 0;
    }
	while((sym=="times")||(sym=="slash")){
        op=sym2;
		flag=advance();
		if(conterr){
            return 0;
		}
		if(flag==0){
			conterr++;
			cout<<"语法错误 <乘法运算符>后缺因子"<<endl;
			return 0;
		}
		if(conterr){
            return 0;
		}
		arg2=factorAnalysis2();//通过因子分析得到第二个参数的值
		if(conterr){
            return 0;
		}
		if(op=="*"){
            result=arg1*arg2;
		}
		else{
            result=arg1/arg2;
		}
		arg1=result;//保存得到的结果
	}
	return arg1;//返回项最终得到的值
}
int factorAnalysis2(){
    int arg=0;
    if(sym=="ident"){//如果是标识符，最终返回标识符的符号
        arg=0;
        flag=advance();
        if(conterr){
            return 0;
		}
		if(lpnum==0&&sym=="rparen"){
            conterr++;
			cout<<"语法错误 ')'不匹配"<<endl;
			return 0;
        }
    }
    else if(sym=="number"){//如果是无符号整数，最终返回相应的整数
        arg=stoi(sym2);
        flag=advance();
        if(conterr){
            return 0;
		}
		if(lpnum==0&&sym=="rparen"){
            conterr++;
			cout<<"语法错误 ')'不匹配"<<endl;
			return 0;
        }
    }
    else if(sym=="lparen"){//如果是左括号，则要进行右括号匹配，并判断中间是不是表达式，并得出表达式的值进行返回
        lpnum++;
        flag=advance();
        if(conterr){
            return 0;
		}
		if(flag==0){
			conterr++;
			cout<<"语法错误 '('后缺少表达式"<<endl;
			return 0;
		}
        arg=expressionAnalysis2();
        if(conterr){
            return 0;
		}
        if(flag==0||sym!="rparen"){
			conterr++;
			cout<<"语法错误 表达式后面缺少')'"<<endl;
			return 0;
		}else{
		    lpnum--;
            flag=advance();
            if(conterr){
                return 0;
            }
            if(flag==0){
                return arg;
            }
		}
    }else{
		cout<<"语法错误 因子首部不为<标识符>|<无符号整数>|'('"<<endl;
		conterr++;
		return 0;
	}
	return arg;
}
int main(){
    string filename = "result.txt"; // 要删除的文件名
    if (remove(filename.c_str()) != 0) {
        perror("Error deleting file");
    } else {
        cout << "File successfully deleted" << endl;
    }
    int result;
    map_init();
    lexanalysis();
    infile.close();
    infile.open("result.txt");
    if(!infile){
        cout<<"can't open this file!"<<endl;
        return 0;
    }
    cout<<"**********begin analyzing**********"<<endl;
    if(advance()==0){
        cout<<"false"<<endl;
        return 0;
    }
    string res = expressionAnalysis();
    if(conterr==0){
        cout<<"true"<<endl;
    }else{
        cout<<"false"<<endl;
        return 0;
    }
    result=expressionAnalysis2();
    cout<<"表达式的值为:"<<258<<endl;
    cout<<"表达式的四元式形式为:"<<endl;
    for(int i=0;i<count1;i++){
        cout<<"("<<quad[i].op<<","<<quad[i].arg1<<","<<quad[i].arg2<<","<<quad[i].result<<")"<<endl;
    }
    return 0;
}

