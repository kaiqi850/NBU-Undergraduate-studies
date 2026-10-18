#include<stdio.h>
#include <string.h>
#include <stdlib.h>

char code_word[11000][20] = {
    "PROGRAM", "CONST", "VAR", "INTEGER",
    "LONG", "PROCEDURE", "IF", "THEN",
    "WHILE", "DO", "READ", "WRITE",
    "BEGIN", "END", "ODD", "+",
    "-", "*", "/", "=",
    "<>", "<", "<=", ">",
    ">=", ".", ".", ";",
    ":", ":=", "(", ")",
     " "," ","#"
};

int code_length(){
	int i;
	for(i = 0;code_word[i][0]!='\0';i++){
	}
	return i;
}

void my_strcpy(char *dest, const char *src) {
    while ((*dest = *src) != '\0') {
        printf("%c %c\n", *dest,*src); // 输出复制的字符
        dest++; // 移动到下一个目标字符位置
        src++;  // 移动到下一个源字符位置
        printf("down\n");
    }
    
}


void show(){
	for(int i =0;code_word[i][0]!='\0';i++){
	   printf("%d %s\n",i+1,code_word[i]);
	}
}

int row = 1,column = 0,flag1 = 0;

char Fgetc(FILE* filename){
	char n;
	n = fgetc(filename);
	if(n == '\n'){
		column = 0;
		row = row+1;
	}
	else
	column = column+1;
	return n;
}

int IsDigt(char d){
	if(d>='0'&&d<='9'){
		return 1;
	}
	else
	return 0;
}

int IsAlph(char d){
	if(d>='a'&&d<='z'||d>='A'&&d<='Z'){
		return 1;
	}
	else
	return 0;
}

int IsSpace(char d){
	if(d == ' '){
		return 1;
	}
	else
	return 0;
}

int IsSinglechar(char d){
	if(!IsAlph(d)&&!IsDigt(d)&&!IsSpace(d)&&d!='\n')
	return 1;
	else
	return 0;
}

int IsDoublechar(char d,FILE* filename){
	char c;
	if(IsSinglechar(d)){
		c = Fgetc(filename);
		if(IsSinglechar(c)){
			return 1;
		}
		else{
			return 0;
		}
	}
	else
	return 0;
}

int IsKey(char *n){
	for(int i =1;code_word[i-1][0]!='\0';i++){
		if(!strcmp(n,code_word[i-1])){
		 	return i; 
		}
	}
	return 0;
}

void Wrong(char d){
	printf("出错行：%d  出错列: %d  出错元素:%c\n",row,column,d);
}

char* double_to_char_array(double number) {
    // 分配足够大的内存来存储转换后的字符串
    char* buffer = (char*)malloc(64 * sizeof(char)); // 假设最多需要64个字符存储转换结果

    if (buffer == NULL) {
        printf("内存分配失败！\n");
        exit(1);
    }

    // 使用sprintf函数将double数转换为字符串，%.0lf表示不显示小数部分
    sprintf(buffer, "%.0lf", number);

    return buffer;
}


void GetSym(const char* filename){
	FILE *file = fopen(filename,"r");
	if (file == NULL) {
        perror("Error opening file");
        return;
    }
    
    char n,str[21];
    int flag=0,number = 0;
    int comment_mode = 0; // 注释模式标志，0表示未在注释中，1表示在注释中
    int comment_brace_mode = 0; // 花括号注释模式标志，0表示未在花括号注释中，1表示在花括号注释中
    
    while ((n = Fgetc(file)) != EOF) {
    	flag = 0;
    	flag1 = 0;
        if(IsSpace(n)){                  //空格换下一个单词  
        	continue;
		}
		else if (comment_mode == 0 && (n == '{' || n == '(')) { // 检查是否进入注释模式
            if (n == '{') {
                comment_mode = 1;
            } else if (n == '(') {
                n = Fgetc(file); // 读取下一个字符，检查是否是花括号注释的开始
                if (n == '*') {
                    comment_mode = 1;
                    comment_brace_mode = 1;
                } else {
                    fseek(file, -1, SEEK_CUR); // 将读取的字符放回文件流中
                }
            }
            continue; // 跳过注释符号
        } 
		else if (comment_mode == 1 && comment_brace_mode == 1 && n == '*') { // 花括号注释结束
            n = Fgetc(file);
            if (n == ')') {
                comment_mode = 0; // 退出注释模式
                comment_brace_mode = 0; // 退出花括号注释模式
            }
            continue;
        } 
		else if (comment_mode == 1 && n == '}') { // 大括号注释结束
            comment_mode = 0; // 退出注释模式
            continue;
        }
		else if (comment_mode == 1) { // 在注释中，跳过当前字符
            continue;
        }
		
		else if(IsAlph(n)){
	    	number = 0;              //字母进入判断 
			 while ((IsAlph(n) || IsDigt(n))) {
                str[number++] = n;
                n = Fgetc(file);
                if(number == 20){
                	printf("出错类型：标识符长度过长 ");
                	Wrong(n);
                	flag1 =1;
                	while((n = Fgetc(file)) != EOF && n != ' ' && n != '\n'){
                		continue;
					}
                	break;
				} 
            }
            if(flag1 == 1){
            	continue;
			}
			
            str[number] = '\0';
			flag = IsKey(str); 	 // 添加字符串结束符
            if (flag) {
                printf("(%d,%s)\n",flag,str); // 输出关键词
            }
            else{
                strcpy(code_word[33], str);
                printf("(%d,%s)\n",34,str);    //strcpy(code_word[code_length()], str);
                                                          // printf("(%d,%s)\n",code_length(),str);
			} 
            for(int j =0;j<strlen(str);j++){
            	str[j] = '\0';
			}
		}
		
		
		else  if(IsDigt(n))                           //数字进入判断 
		{
			double val = 0;
			val = val*10+n-'0';
			n = Fgetc(file);
			while(IsDigt(n)){
				val = val * 10 +n -'0';
				n = Fgetc(file);
			} 
			if(n == '.'){
				n = Fgetc(file);
				double i = 0.1;
				while(1){
					if(IsDigt(n)){
						val = val + (n-'0')*i;
					    i = i/10;
					    n = Fgetc(file);
					}
					else if(IsSpace(n) || n == '\n'){
						    break;
					}
					else{
					  printf("数据格式不合法 ");
					  Wrong(n);
				      flag1 = 1;
					  while((n = Fgetc(file)) != EOF && n != ' ' && n != '\n'){
                		continue;
					}
                	continue;
					}
				}
				
			}
        if(flag1 == 0){
        	char *str1 = double_to_char_array(val);
		flag = IsKey(str1); 	 // 添加字符串结束符
            if (flag) {
                printf("(%d,%s)\n",flag,str1); // 输出关键词
            }
            else{
                strcpy(code_word[32], str1);
                printf("(%d,%s)\n",33,str1);
			}
		}
		}
		
		
		else if(IsSinglechar(n)){
		    str[0] = n;
			n = Fgetc(file);
			if(IsSinglechar(n)){
				str[1] = n;
				str[2] = '\0'; 
				flag = IsKey(str);
				if (flag) {
                printf("(%d,%s)\n",flag,str); // 输出关键词
                }
            else{
                printf("不是合法内码 ");
	        	Wrong(n);
			    }
			}
			else{
				str[1] = '\0';
				flag = IsKey(str);
				if (flag) {
                printf("(%d,%s)\n",flag,str); // 输出关键词
                }
                else{
                printf("不是合法标识符 ");
	        	Wrong(str[0]);
			    }
			} 
		} 
		
		continue;
    }

    fclose(file);
}

int main(){
	
	const char *filename = "C:/Users/asus/Desktop/x/试卷卷卷子/编译原理/编译原理/词法分析器/编译原理文本.txt"; // 文件名
	GetSym(filename);
     
}
