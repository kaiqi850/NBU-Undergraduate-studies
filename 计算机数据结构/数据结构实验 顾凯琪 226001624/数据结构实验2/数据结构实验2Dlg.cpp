
// 数据结构实验2Dlg.cpp: 实现文件
//
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <math.h>
#include "pch.h"
#include "framework.h"
#include "数据结构实验2.h"
#include "数据结构实验2Dlg.h"
#include "afxdialogex.h"
#include <stdexcept>

#ifdef _DEBUG
#define new DEBUG_NEW
#endif


// 用于应用程序“关于”菜单项的 CAboutDlg 对话框

class CAboutDlg : public CDialogEx
{
public:
	CAboutDlg();

// 对话框数据
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_ABOUTBOX };
#endif

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV 支持

// 实现
protected:
	DECLARE_MESSAGE_MAP()
};

CAboutDlg::CAboutDlg() : CDialogEx(IDD_ABOUTBOX)
{
}

void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialogEx)
END_MESSAGE_MAP()


// C数据结构实验2Dlg 对话框



C数据结构实验2Dlg::C数据结构实验2Dlg(CWnd* pParent /*=nullptr*/)
	: CDialogEx(IDD_MY2_DIALOG, pParent)
	, Expression(_T(""))
	, Result(_T(""))
{
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void C数据结构实验2Dlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
	DDX_Text(pDX, IDC_EDIT1, Expression);
	DDX_Text(pDX, IDC_EDIT2, Result);
}

BEGIN_MESSAGE_MAP(C数据结构实验2Dlg, CDialogEx)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_BN_CLICKED(IDC_BUTTON14, &C数据结构实验2Dlg::OnBnClickedButton14)
	ON_BN_CLICKED(IDC_BUTTON11, &C数据结构实验2Dlg::OnBnClickedButton11)
	ON_BN_CLICKED(IDC_BUTTON5, &C数据结构实验2Dlg::OnBnClickedButton5)
	ON_BN_CLICKED(IDC_BUTTON7, &C数据结构实验2Dlg::OnBnClickedButton7)
	ON_BN_CLICKED(IDC_BUTTON8, &C数据结构实验2Dlg::OnBnClickedButton8)
	ON_BN_CLICKED(IDC_BUTTON9, &C数据结构实验2Dlg::OnBnClickedButton9)
	ON_BN_CLICKED(IDC_BUTTON10, &C数据结构实验2Dlg::OnBnClickedButton10)
	ON_BN_CLICKED(IDC_BUTTON16, &C数据结构实验2Dlg::OnBnClickedButton16)
	ON_BN_CLICKED(IDC_BUTTON15, &C数据结构实验2Dlg::OnBnClickedButton15)
	ON_BN_CLICKED(IDC_BUTTON1, &C数据结构实验2Dlg::OnBnClickedButton1)
	ON_BN_CLICKED(IDC_BUTTON3, &C数据结构实验2Dlg::OnBnClickedButton3)
	ON_BN_CLICKED(IDC_BUTTON4, &C数据结构实验2Dlg::OnBnClickedButton4)
	ON_BN_CLICKED(IDC_BUTTON6, &C数据结构实验2Dlg::OnBnClickedButton6)
	ON_BN_CLICKED(IDC_BUTTON12, &C数据结构实验2Dlg::OnBnClickedButton12)
	ON_BN_CLICKED(IDC_BUTTON13, &C数据结构实验2Dlg::OnBnClickedButton13)
	ON_BN_CLICKED(IDC_BUTTON17, &C数据结构实验2Dlg::OnBnClickedButton17)
	ON_BN_CLICKED(IDC_BUTTON18, &C数据结构实验2Dlg::OnBnClickedButton18)
	ON_BN_CLICKED(IDC_BUTTON19, &C数据结构实验2Dlg::OnBnClickedButton19)
	ON_BN_CLICKED(IDC_BUTTON20, &C数据结构实验2Dlg::OnBnClickedButton20)
	ON_BN_CLICKED(IDC_BUTTON21, &C数据结构实验2Dlg::OnBnClickedButton21)
	ON_BN_CLICKED(IDC_BUTTON22, &C数据结构实验2Dlg::OnBnClickedButton22)
	ON_BN_CLICKED(IDC_BUTTON23, &C数据结构实验2Dlg::OnBnClickedButton23)
	ON_EN_CHANGE(IDC_EDIT1, &C数据结构实验2Dlg::OnEnChangeEdit1)
	ON_BN_CLICKED(IDC_BUTTON24, &C数据结构实验2Dlg::OnBnClickedButton24)
	ON_BN_CLICKED(IDC_BUTTON2, &C数据结构实验2Dlg::OnBnClickedButton2)
END_MESSAGE_MAP()


// C数据结构实验2Dlg 消息处理程序

BOOL C数据结构实验2Dlg::OnInitDialog()
{
	CDialogEx::OnInitDialog();

	// 将“关于...”菜单项添加到系统菜单中。

	// IDM_ABOUTBOX 必须在系统命令范围内。
	ASSERT((IDM_ABOUTBOX & 0xFFF0) == IDM_ABOUTBOX);
	ASSERT(IDM_ABOUTBOX < 0xF000);

	CMenu* pSysMenu = GetSystemMenu(FALSE);
	if (pSysMenu != nullptr)
	{
		BOOL bNameValid;
		CString strAboutMenu;
		bNameValid = strAboutMenu.LoadString(IDS_ABOUTBOX);
		ASSERT(bNameValid);
		if (!strAboutMenu.IsEmpty())
		{
			pSysMenu->AppendMenu(MF_SEPARATOR);
			pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
		}
	}

	// 设置此对话框的图标。  当应用程序主窗口不是对话框时，框架将自动
	//  执行此操作
	SetIcon(m_hIcon, TRUE);			// 设置大图标
	SetIcon(m_hIcon, FALSE);		// 设置小图标

	// TODO: 在此添加额外的初始化代码

	return TRUE;  // 除非将焦点设置到控件，否则返回 TRUE
}

void C数据结构实验2Dlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	if ((nID & 0xFFF0) == IDM_ABOUTBOX)
	{
		CAboutDlg dlgAbout;
		dlgAbout.DoModal();
	}
	else
	{
		CDialogEx::OnSysCommand(nID, lParam);
	}
}

// 如果向对话框添加最小化按钮，则需要下面的代码
//  来绘制该图标。  对于使用文档/视图模型的 MFC 应用程序，
//  这将由框架自动完成。

void C数据结构实验2Dlg::OnPaint()
{
	if (IsIconic())
	{
		CPaintDC dc(this); // 用于绘制的设备上下文

		SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

		// 使图标在工作区矩形中居中
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// 绘制图标
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialogEx::OnPaint();
	}
}

//当用户拖动最小化窗口时系统调用此函数取得光标
//显示。
HCURSOR C数据结构实验2Dlg::OnQueryDragIcon()
{
	return static_cast<HCURSOR>(m_hIcon);
}






void C数据结构实验2Dlg::OnBnClickedButton5()             //数字1
{
	str += '1';
	Expression = str;
	UpdateData(FALSE);
}


void C数据结构实验2Dlg::OnBnClickedButton7()            //数字2
{
	str += '2';
	Expression = str;
	UpdateData(FALSE);
}


void C数据结构实验2Dlg::OnBnClickedButton8()            //数字3
{
	str += '3';
	Expression = str;
	UpdateData(FALSE);
}


void C数据结构实验2Dlg::OnBnClickedButton9()             //数字4
{
	str += '4';
	Expression = str;
	UpdateData(FALSE);
}


void C数据结构实验2Dlg::OnBnClickedButton10()            //数字5
{
	str += '5';
	Expression = str;
	UpdateData(FALSE);
}

void C数据结构实验2Dlg::OnBnClickedButton11()            //数字6
{
	str += '6';
	Expression = str;
	UpdateData(FALSE);
}


void C数据结构实验2Dlg::OnBnClickedButton16()            //数字7
{
	str += '7';
	Expression = str;
	UpdateData(FALSE);
}


void C数据结构实验2Dlg::OnBnClickedButton15()    
{                                                         //数字8
	str += '8';
	Expression = str;
	UpdateData(FALSE);
}

 
void C数据结构实验2Dlg::OnBnClickedButton14()            //数字9
{
	str += '9';
	Expression = str;
	UpdateData(FALSE);
}

void C数据结构实验2Dlg::OnBnClickedButton1()              //数字0
{
	str += '0';
	Expression = str;
	UpdateData(FALSE);
}


void C数据结构实验2Dlg::OnBnClickedButton3()               //符号.
{

	str += '.';
	Expression = str;
	UpdateData(FALSE);
}


void C数据结构实验2Dlg::OnBnClickedButton6()              //符号+
{
	str += '+';
	Expression = str;
	UpdateData(FALSE);
}


void C数据结构实验2Dlg::OnBnClickedButton12()              //符号-
{
	str += '-';
	Expression = str;
	UpdateData(FALSE);
}


void C数据结构实验2Dlg::OnBnClickedButton13()              //符号x
{
	str += '*';
	Expression = str;
	UpdateData(FALSE);
}


void C数据结构实验2Dlg::OnBnClickedButton17()              //符号➗
{
	str += '/';
	Expression = str;
	UpdateData(FALSE);
}

 
void C数据结构实验2Dlg::OnBnClickedButton18()             //符号开根号
{
	str += "√";
	Expression = str;
	UpdateData(FALSE);
}


void C数据结构实验2Dlg::OnBnClickedButton19()            //符号平方
{
	str += "^";
	Expression = str;
	UpdateData(FALSE);
}


void C数据结构实验2Dlg::OnBnClickedButton20()              //符号(
{
	str += '(';
	Expression = str;
	UpdateData(FALSE);
}

void C数据结构实验2Dlg::OnBnClickedButton24()                 //符号）
{
	str += ')';
	Expression = str;
	UpdateData(FALSE);
}



void C数据结构实验2Dlg::OnBnClickedButton21()            //符号整除
{
	str += '%';
	Expression = str;
	UpdateData(FALSE);
}


void C数据结构实验2Dlg::OnBnClickedButton22()            //符号清空全部
{
	str.Empty();
	Expression.Empty();
	Result.Empty();
	UpdateData(FALSE);
}


void C数据结构实验2Dlg::OnBnClickedButton23() // 符号清空一个
{
	// 如果字符串不为空，删除最后一个字符
	if (!str.IsEmpty())
	{
		str.Delete(str.GetLength() - 1);
	}
	Expression = str;
	// 更新文本框中的内容
	UpdateData(FALSE);
}



void C数据结构实验2Dlg::OnEnChangeEdit1()
{
    // 获取编辑框的控件指针
    CEdit* pEdit = (CEdit*)GetDlgItem(IDC_EDIT1);
    if (pEdit)
    {
        // 创建字体对象
        CFont font;
        font.CreateFont(
            18,                     // 字体高度，单位为逻辑单位
            0,                      // 字体宽度
            0,                      // 字体倾斜角度
            0,                      // 字体方向
            FW_NORMAL,              // 字体粗细
            FALSE,                  // 是否是斜体
            FALSE,                  // 是否有下划线
            0,                      // 是否有删除线
            DEFAULT_CHARSET,        // 字符集
            OUT_DEFAULT_PRECIS,     // 输出精度
            CLIP_DEFAULT_PRECIS,    // 裁剪精度
            DEFAULT_QUALITY,        // 输出质量
            DEFAULT_PITCH | FF_SWISS, // 字体族
            _T("Arial")             // 字体名称
        );

        // 设置编辑框的字体
        pEdit->SetFont(&font);
    }
}




void C数据结构实验2Dlg::OnBnClickedButton4() // 符号=
{
	CStringA strA(Expression);
	char* charStr = strA.GetBuffer(strA.GetLength() + 1);
	if (charStr == NULL) {
		return;
	}
	double n = evaluate(charStr);
	str = Expression;
	Result.Format(_T("%lf"), n);
	UpdateData(FALSE);
}


int C数据结构实验2Dlg::precedence(char op) {
	switch (op) {
	case '+':
	case '-':
		return 1;
	case '*':
	case '/':
		return 2;
	case '^':
	case '√':
	case 's':
	case 'S':
		return 3;
	default:
		return 0;
	}
}

double C数据结构实验2Dlg::applyOp(double a, double b, char op) {
	switch (op) {
	case '+': return a + b;
	case '-': return a - b;
	case '*': return a * b;
	case '/': return a / b;
	case '%': return fmod(a, b); // 使用 fmod 函数进行正确的模运算
	case '^': return pow(a, b);
	case '√':
	case 's':
	case 'S': return sqrt(b);
	}
	return 0;
}


double C数据结构实验2Dlg::evaluate(char* expression) {
	int i;
	double numStack[1000]; // 数字栈
	char opStack[1000]; // 运算符栈
	int numTop = -1;    // 数字栈顶指针
	int opTop = -1;     // 运算符栈顶指针
	bool hasDot = false; // 标记当前数字是否有小数点
	double decimal = 0.1; // 小数点的位数

	for (i = 0; expression[i] != '\0'; i++) {
		if (isdigit(expression[i])) {
			double num = 0;
			int dotCount = 0; // 记录小数点数量
			while (isdigit(expression[i]) || (expression[i] == '.' && dotCount == 0)) { // 仅在小数点数量为0时才允许继续读取
				if (expression[i] == '.') {
					dotCount++; // 记录小数点出现
					if (dotCount > 1) { // 如果已经有一个小数点出现了，说明数字非法
						// 报告错误或者抛出异常
						throw std::invalid_argument("Invalid number format: multiple decimal points.");
					}
				}
				
				if (hasDot) {
					num += (expression[i] - '0') * decimal;
					decimal *= 0.1;
				}
				else {
					num = num * 10 + (expression[i] - '0');
				}
				i++;
			}
			numTop++;
			numStack[numTop] = num;
			i--; // 因为for循环会自增，这里需要减1
			hasDot = false; // 重置小数点标记
			decimal = 0.1; // 重置小数点位数
		}
		else if (expression[i] == '(') { // 如果是左括号，压入运算符栈
			opTop++;
			opStack[opTop] = expression[i];
		}
		else if (expression[i] == ')') { // 如果是右括号，弹出运算符栈中的运算符直到遇到左括号
			while (opTop != -1 && opStack[opTop] != '(') {
				double b = numStack[numTop--];
				double a = numStack[numTop--];
				char op = opStack[opTop--];
				numTop++;
				numStack[numTop] = applyOp(a, b, op);
			}
			opTop--; // 弹出左括号
		}
		else if (expression[i] == '+' || expression[i] == '-' ||
			expression[i] == '*' || expression[i] == '/' ||
			expression[i] == '%' || // 添加 '%' 作为整除操作符
			expression[i] == '^' || expression[i] == '√' ||
			expression[i] == 's' || expression[i] == 'S') { // 如果是运算符
			// 如果当前运算符的优先级小于等于栈顶运算符的优先级，先执行栈顶运算符
			while (opTop != -1 && precedence(opStack[opTop]) >= precedence(expression[i])) {
				double b = numStack[numTop--];
				double a = numStack[numTop--];
				char op = opStack[opTop--];
				numTop++;
				numStack[numTop] = applyOp(a, b, op);
			}
			opTop++;
			opStack[opTop] = expression[i];
		}
	}

	// 依次计算剩余的运算符
	while (opTop != -1) {
		double b = numStack[numTop--];
		double a = numStack[numTop--];
		char op = opStack[opTop--];
		numTop++;
		numStack[numTop] = applyOp(a, b, op);
	}

	return numStack[numTop];
}



void C数据结构实验2Dlg::OnBnClickedButton2()
{
	MessageBox(_T("欢~迎~光~临~\n凯琪小屋~~"));
}
