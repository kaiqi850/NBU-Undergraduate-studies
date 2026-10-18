#include<iostream>
using namespace std;
#include<cstring> 
#define PROGRAM 1
#define CONST 2
#define VAR 3
#define INTEGER 4
#define LONG 5
#define PROCEDURE 6
#define IF 7
#define THEN 8
#define WHILE 9
#define DO 10
#define READ 11
#define WRITE 12
#define BEGIN 13
#define END 14
#define ODD 15
#define ADD 16
#define SUB 17
#define MUL 18
#define DIV 19
#define EQU 20
#define NEQ 21
#define LES 22
#define LEQ 23
#define LAG 24
#define GEQ 25
#define DOT 26
#define COM 27
#define SEM 28
#define COL 29
#define ASS 30
#define LBR 31
#define RBR 32
#define INT 33
#define ID 34
#define EIN 35
#define lenth1 15
#define lenth2 17
struct Ident
{
	char name[21];
	int type;
	int addr;
};
Ident indent[1000]; // 定义标识符表
struct St
{
	char name[21];
	int code;
};
St sym;

int lenth = 0;  // 表示标识符表长度
FILE* f1, * f2; //f1、f2分别指向输入输出文件

int line = 0, row = 0, val;
void getsym();char getchr();void error(int);
void program(); void proghead();
void block(); void consexpl();
void consdefi(); void varexpl();
void conssuff(); void vardefi();
void varsuff(); void procdefi();
void typeil(); void procedh();
void procsuff(); void assipro();
void sentence(); void suffix();
void ifsent(); void read();
void whilsent(); void idsuff();
void write(); void compsent();
void exprsuff(); void sentsuff();
void conditio(); void termsuff();
void express(); void term();
void factsuff(); void argument();
void factor(); void addoper();
void muloper(); void respoper();

int main() {
	if ((f1 = fopen("1.txt", "r")) == NULL) {  // 打开输入文件流
		cout << "can not open the input file!" << endl;
		exit(0);
	}
	getsym();
	program();
	cout << "该程序通过语法分析！" << endl;
	fclose(f1);
	return 0;
}

void getsym() {
	static char a[lenth1][10] = {
		"program","const","var","integer","long","procedure","if",
		"then","while","do","read","write","begin","end","odd"
	},
		d[lenth2][3] = { "+","-","*","/","=","<>","<","<=",">",">=",
						".",",",";",":",":=","(",")" },
		str[21], ch = ' ';
	int i, n; // n 判断单词长度, i 判断是哪个关键字
	while (isspace(ch) || ch == '{') { // 跳过空白字符和注释开始符号 '{'
		if (ch == '{') { // 如果是注释开始符号 '{'
			while ((ch = getchr()) != '}' && ch != EOF) // 继续读取字符直到注释结束符号 '}'
				;
			if (ch == EOF) // 如果到达文件末尾，则退出
				return;
		}
		ch = getchr();
	}
	if (isalpha(ch)) { // 判断字母开头的字符
		n = 0;
		while (isalpha(ch) || isdigit(ch)) {
			if (isalpha(ch))
				ch = tolower(ch);
			str[n++] = ch;
			ch = getchr();
		}
		str[n] = '\0';
		for (i = 0; i < lenth1; i++) {
			if (!strcmp(str, a[i]))
				break;
		}
		if (i < lenth1) { // 找到匹配关键字
			strcpy(sym.name, a[i]);
			sym.code = i + 1;
		}
		else {
			for (i = 0; i < lenth; i++) { // 遍历已记录的标识符记录表
				if (!strcmp(str, indent[i].name))
					break;
			}
			if (i == lenth) {
				strcpy(indent[i].name, str);
			}
			strcpy(sym.name, indent[i].name);
			sym.code = 34;
		}
	}
	else if (isdigit(ch)) { // 判断数字开头的字符
		val = 0;n = 0;
		while (isdigit(ch)) {
			val = val * 10 + ch - '0';
			sym.name[n++] = ch;
			ch = getchr();
		}
		sym.name[n] = '\0';
		sym.code = 33;
	}
	else {  // 判断特殊字符
		if (ch == '+' || ch == '-' || ch == '*' || ch == '/' || ch == '=' ||
			ch == '.' || ch == ',' || ch == ';' || ch == '(' || ch == ')') {
			str[0] = ch; str[1] = '\0';
			ch = getchr();
			for (i = 0; i < lenth2; i++) {
				if (!strcmp(str, d[i])) {
					strcpy(sym.name, str);
					sym.code = i + 16;
					break;
				}
			}
		}
		else if (ch == '#') {
			str[0] = ch; str[1] = '\0';
			ch = getchr();
			strcpy(sym.name, str);
			sym.code = 35;
		}
		else if (ch == '<') {
			char b = getchr();
			if (b == '>') {
				str[0] = '<';str[1] = '>';str[2] = '\0';
				strcpy(sym.name, str);
				sym.code = 21;
				ch = getchr();
			}
			else if (b == '=') {
				str[0] = '<';str[1] = '=';str[2] = '\0';
				strcpy(sym.name, str);
				sym.code = 23;
				ch = getchr();
			}
			else {
				str[0] = '<';str[1] = '\0';
				strcpy(sym.name, str);
				sym.code = 22;
				ch = b;
			}
		}
		else if (ch == '>') {
			char b = getchr();
			if (b == '=') {
				str[0] = '>';str[1] = '=';str[2] = '\0';
				strcpy(sym.name, str);
				sym.code = 25;
				ch = getchr();
			}
			else {
				str[0] = '>';str[1] = '\0';
				strcpy(sym.name, str);
				sym.code = 24;
				ch = b;
			}
		}
		else if (ch == ':') {
			char b = getchr();
			if (b == '=') {
				str[0] = ch;str[1] = b;str[2] = '\0';
				strcpy(sym.name, str);
				sym.code = 30;
				ch = getchr();
			}
			else {
				str[0] = ch;str[1] = '\0';
				strcpy(sym.name, str);
				sym.code = 29;
				ch = b;
			}
		}
	}
}



char getchr() {  // 从文件中获取下一个非空字符
	char ch = fgetc(f1);
	if (ch == '\n') {
		row = 1;
		line++;
	}
	else {
		if (ch != ' ' && ch != '\t') {
			row++;
		}
	}
	return ch;
}

void error(int n) {
	printf("There are %d-error\n", n);
	exit(0);
}

void program() { // 程序
	proghead();block();
	if (sym.code == DOT) {
		return ;
	}
	else {
		error(2);
	}
}

void proghead() { // 程序首部
	if (sym.code == PROGRAM) {
		getsym(); // 获取next token
		if (sym.code == ID) {
			getsym();
			if (sym.code == SEM)
				getsym();
			else
				error(5);
		}
		else
			error(4);
	}
	else
		error(3);
}

void block() {  // 分程序
	consexpl();
	varexpl();
	procdefi();
	compsent();
}

void consexpl() { // 常量说明部分
	if (sym.code == CONST) {
		getsym();
		consdefi();
		conssuff();
		if (sym.code == SEM)
			getsym();
		else
			error(6);
	} // 无else表示可以为空
}

void consdefi() {   // 常量定义
	if (sym.code == ID) {
		getsym();
		if (sym.code == EQU) {
			getsym();
			if (sym.code == INT)
				getsym();
			else
				error(9);
		}
		else
			error(8);
	}
	else
		error(7);
}

void conssuff() {  // 常量定义后缀
	if (sym.code == COM) {
		getsym();
		consdefi();
		conssuff();
	}// 无else表示可以为空
}
void varexpl() {  // 变量说明部分
	if (sym.code == VAR) {
		getsym();
		vardefi();
		varsuff();
	}// 无else表示可以为空
}

void vardefi() {  // 变量定义
	if (sym.code == ID) {
		getsym();
		idsuff();
		if (sym.code == COL) {
			getsym();
			typeil();
			if (sym.code == SEM)
				getsym();
			else
				error(12);
		}
		else
			error(11);
	}
	 else
			error(10);
}

void idsuff() {          //标识符后缀 
	if (sym.code == COM) {
		getsym();
		if (sym.code == ID) {
			getsym();
			idsuff();
		}
		else
			error(30);
	} // 无else表示可以为空
}
void varsuff() {       //变量后缀 
	if (sym.code == ID) {
		vardefi();
		varsuff();
	}// 无else表示可以为空
}

void typeil() {
	if (sym.code == INTEGER || sym.code == LONG)
		getsym();
	else
		error(13);
}

void procdefi() {
	if (sym.code == PROCEDURE)
	{
		procedh();
		block();
		if (sym.code == SEM) {
			procsuff();
		}
		else
			error(14);
	}// 无else表示可以为空
}

void procedh() {
	if (sym.code == PROCEDURE) {
		getsym();
		if (sym.code == ID) {
			getsym();
			argument();
			if (sym.code == SEM)
				getsym();
			else
				error(16);
		}
		else
			error(15);
	}
}

void argument() {
	if (sym.code == LBR) {
		getsym();
		if (sym.code == ID) {
			getsym();
			if (sym.code == COL) {
				getsym();
				if (sym.code == RBR)
					getsym();
				else
					error(19);
			}
			else
				error(18);
		}
		error(17);
	}
}

void procsuff() {
	if (sym.code == PROCEDURE) {
		procedh();
		block();
		if (sym.code == SEM) {
			getsym();
			procsuff();
		}
		else
			error(20);
	}
}

void assipro() {
	if (sym.code == ID) {
		getsym();
		suffix();
	}
	else
		error(21);
}

void sentence() {
	if (sym.code == ID) {
		assipro();
	}
	else if (sym.code == IF) {
		ifsent();
	}
	else if (sym.code == WHILE)
		whilsent();
	else if (sym.code == READ)
		read();
	else if (sym.code == WRITE)
		write();
	else if (sym.code == BEGIN)
		compsent();
}

void suffix() {
	if (sym.code == ASS) {
		getsym();
		express();
	}
	else if (sym.code == LBR) {
		getsym();
		express();
		if (sym.code == RBR)
			getsym();
		else error(22);
	}
}

void ifsent() {
	if (sym.code == IF) {
		getsym();
		conditio();
		if (sym.code == THEN) {
			getsym();
			sentence();
		}
		else
			error(24);
	}
	else
		error(23);
}

void whilsent() {
	if (sym.code == WHILE) {
		getsym();
		conditio();
		if (sym.code == DO) {
			getsym();
			sentence();
		}
		else
			error(26);
	}
	else
		error(25);
}

void read() {
	if (sym.code == READ) {
		getsym();
		if (sym.code == LBR) {
			getsym();
			if (sym.code == ID) {
				getsym();
				idsuff();
				if (sym.code == RBR)
					getsym();
				else error(27);
			}
			else
				error(30);
		}
		else error(29);
	}
	else error(28);
}


void write() {
	if (sym.code == WRITE) {
		getsym();
		if (sym.code == LBR) {
			getsym();
			express();
			exprsuff();
			if (sym.code == RBR)
				getsym();
			else error(34);
		}
		else error(33);
	}
	else error(32);
}

void compsent() {
	if (sym.code == BEGIN) {
		getsym();
		sentence();
		sentsuff();
		if (sym.code == END)
			getsym();
		else error(36);
	}
	else error(35);
}

void exprsuff() {
	if (sym.code == COM) {
		getsym();
		express();
		exprsuff();
	}
}

void sentsuff() {
	if (sym.code == SEM) {
		getsym();
		sentence();
		sentsuff();
	}
}

void conditio() {
	if (sym.code == ODD) {
		getsym();
		express();
	}
	else {
		express();
		respoper();
		express();
	}
}

void express() {
	if (sym.code == ADD || sym.code == SUB)
		getsym();
	term();
	termsuff();
}

void term() {
	factor();
	factsuff();
}

void termsuff() {
	if (sym.code == ADD || sym.code == SUB) {
		getsym();
		factor();
		factsuff();
	}
}

void factsuff() {
	if (sym.code == MUL || sym.code == DIV) {
		getsym();
		factor();
		factsuff();
	}
}

void factor() {
	if (sym.code == ID) {
		getsym();
//		factsuff();
	}
	else if (sym.code == INT) {
		getsym();
	}
	else if (sym.code == LBR) {
		getsym();
		express();
		if (sym.code == RBR)
			getsym();
		else error(38);
	}
	else error(37);
}

void addoper() {
	if (sym.code == ADD || sym.code == SUB)
		getsym();
	else
		error(39);
}

void muloper() {
	if (sym.code == MUL || sym.code == DIV)
		getsym();
	else
		error(40);
}

void respoper() {
	if (sym.code >= EQU && sym.code <= GEQ)
		getsym();
	else
		error(41);
}


