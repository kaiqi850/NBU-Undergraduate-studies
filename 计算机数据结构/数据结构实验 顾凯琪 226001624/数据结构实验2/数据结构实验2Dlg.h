
// 数据结构实验2Dlg.h: 头文件
//

#pragma once


// C数据结构实验2Dlg 对话框
class C数据结构实验2Dlg : public CDialogEx
{
// 构造
public:
	C数据结构实验2Dlg(CWnd* pParent = nullptr);	// 标准构造函数
	CString str;
	typedef struct symstack {
		char sym[1000];
		int pos;
	}symstack;

	typedef struct numstack {
		int num[1000];
		int pos;
	}numstack;
// 对话框数据
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_MY2_DIALOG };
#endif

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV 支持


// 实现
protected:
	HICON m_hIcon;

	// 生成的消息映射函数
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	DECLARE_MESSAGE_MAP()
public:
	afx_msg void OnBnClickedButton14();
	afx_msg void OnBnClickedButton11();
	afx_msg void OnBnClickedButton5();
	afx_msg void OnBnClickedButton7();
	afx_msg void OnBnClickedButton8();
	afx_msg void OnBnClickedButton9();
	afx_msg void OnBnClickedButton10();
	afx_msg void OnBnClickedButton16();
	afx_msg void OnBnClickedButton15();
	afx_msg void OnBnClickedButton1();
	afx_msg void OnBnClickedButton3();
	afx_msg void OnBnClickedButton4();
	afx_msg void OnBnClickedButton6();
	afx_msg void OnBnClickedButton12();
	afx_msg void OnBnClickedButton13();
	afx_msg void OnBnClickedButton17();
	afx_msg void OnBnClickedButton18();
	afx_msg void OnBnClickedButton19();
	afx_msg void OnBnClickedButton20();
	afx_msg void OnBnClickedButton21();
	afx_msg void OnBnClickedButton22();
	afx_msg void OnBnClickedButton23();
	afx_msg void OnEnChangeEdit1();
	CString Expression;
	afx_msg void OnBnClickedButton24();

	int precedence(char op);
	double applyOp(double a, double b, char op);
	double evaluate(char* expression);
	CString Result;
	afx_msg void OnBnClickedButton2();
};
