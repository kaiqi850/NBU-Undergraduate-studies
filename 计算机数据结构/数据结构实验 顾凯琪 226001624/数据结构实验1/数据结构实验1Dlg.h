
// 数据结构实验1Dlg.h: 头文件
//

#pragma once



// C数据结构实验1Dlg 对话框
class C数据结构实验1Dlg : public CDialogEx
{
// 构造
public:
	C数据结构实验1Dlg(CWnd* pParent = nullptr);	// 标准构造函数

// 对话框数据
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_MY1_DIALOG };
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
	CString name;
	int nummber;
	double score;
	CString picture;
	CImage m_image;       
	CImage m_loadedImage;//dawdadawda
	afx_msg void OnClickedAdd();
	int position;
	afx_msg void OnBnClickedButton1();
	afx_msg void OnClickedButton1();
	afx_msg void OnClickedButton2();
	afx_msg void OnClickedPushBackButton2();
	int Q_number;
	double Q_score;
	afx_msg void OnClickedButton3();
	afx_msg void OnClickedPushBackButton();
	CString Q_name;
	CString Q_picture;
	CImage m_Image;
	CString LoadAndDisplayImage(int newWidth, int newHeight, int posX, int posY);
	void DisplayImage(int newWidth, int newHeight, int posX, int posY,CString picture);
	afx_msg void OnClickedButton4();
	afx_msg void OnChangeEdit10();
	afx_msg void OnClickedButton5();
};
