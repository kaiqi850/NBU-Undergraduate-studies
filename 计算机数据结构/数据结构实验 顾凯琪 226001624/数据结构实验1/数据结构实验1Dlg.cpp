
// 数据结构实验1Dlg.cpp: 实现文件
//

#include "pch.h"
#include "framework.h"
#include "数据结构实验1.h"
#include "数据结构实验1Dlg.h"
#include "afxdialogex.h"
#include <atlimage.h>

#ifdef _DEBUG
#define new DEBUG_NEW
#endif
//SendDlgItemMessage

// 用于应用程序“关于”菜单项的 CAboutDlg 对话框
using namespace std;

CString C数据结构实验1Dlg::LoadAndDisplayImage(int newWidth, int newHeight, int posX, int posY)
{
	CString imagePath; // 用于保存图片文件路径

	// 选择图片文件对话框
	CString filter = _T("图片文件(*.bmp;*.jpg;*.gif;*.png)|*.bmp;*.jpg;*.gif;*.png||");
	CFileDialog dlg(TRUE, NULL, NULL, OFN_FILEMUSTEXIST | OFN_HIDEREADONLY, filter, this);
	if (dlg.DoModal() == IDOK)
	{
		// 获取选择的图片文件路径
		imagePath = dlg.GetPathName();

		// 释放之前加载的图片资源
		m_loadedImage.Destroy();

		// 加载图片
		if (m_loadedImage.Load(imagePath) == S_OK)
		{
			// 绘制图片
			CClientDC dc(this);
			CDC memDC;
			memDC.CreateCompatibleDC(&dc);

			// 创建新的位图并调整大小
			CBitmap bmp;
			bmp.CreateCompatibleBitmap(&dc, newWidth, newHeight);
			CBitmap* pOldBmp = memDC.SelectObject(&bmp);

			// 缩放图片
			m_loadedImage.StretchBlt(memDC.m_hDC, 0, 0, newWidth, newHeight);

			// 将缩放后的图片绘制到窗口上
			dc.BitBlt(posX, posY, newWidth, newHeight, &memDC, 0, 0, SRCCOPY);

			// 恢复原来的位图
			memDC.SelectObject(pOldBmp);
		}
		else
		{
			AfxMessageBox(_T("路径不合理，请点击替换照片，重新选择"));
		}
	}

	return imagePath; // 返回选择的图片文件路径
}

void C数据结构实验1Dlg::DisplayImage(int newWidth, int newHeight, int posX, int posY,CString picture)
{
	// 释放之前加载的图片资源
	m_loadedImage.Destroy();

	// 加载图片
	if (m_loadedImage.Load(picture) == S_OK)
	{
		// 绘制图片
		CClientDC dc(this);
		CDC memDC;
		memDC.CreateCompatibleDC(&dc);

		// 创建新的位图并调整大小
		CBitmap bmp;
		bmp.CreateCompatibleBitmap(&dc, newWidth, newHeight);
		CBitmap* pOldBmp = memDC.SelectObject(&bmp);

		// 缩放图片
		m_loadedImage.StretchBlt(memDC.m_hDC, 0, 0, newWidth, newHeight);

		// 将缩放后的图片绘制到窗口上
		dc.BitBlt(posX, posY, newWidth, newHeight, &memDC, 0, 0, SRCCOPY);

		// 恢复原来的位图
		memDC.SelectObject(pOldBmp);
	}
	else
	{
		AfxMessageBox(_T("路径不合理，请点击替换照片，重新选择"));
	}
}



/* void C数据结构实验1Dlg::LoadAndDisplayImage(int newWidth, int newHeight, int posX, int posY, CString Q_picture)
{
	// 检查图片地址是否有效
	if (Q_picture.IsEmpty())
	{
		AfxMessageBox(_T("图片地址为空"));
		return;
	}

	// 加载图片
	if (m_image.Load(Q_picture) == S_OK)
	{
		// 选择图片文件对话框
		CString filter = _T("图片文件(*.bmp;*.jpg;*.gif;*.png)|*.bmp;*.jpg;*.gif;*.png||");
		CFileDialog dlg(TRUE, NULL, NULL, OFN_FILEMUSTEXIST | OFN_HIDEREADONLY, filter, this);
		if (dlg.DoModal() == IDOK)
		{
			// 绘制图片
			CClientDC dc(this);
			CDC memDC;
			memDC.CreateCompatibleDC(&dc);

			// 创建新的位图并调整大小
			CBitmap bmp;
			bmp.CreateCompatibleBitmap(&dc, newWidth, newHeight);
			CBitmap* pOldBmp = memDC.SelectObject(&bmp);

			// 缩放图片
			m_image.StretchBlt(memDC.m_hDC, 0, 0, newWidth, newHeight);

			// 将缩放后的图片绘制到窗口上
			dc.BitBlt(posX, posY, newWidth, newHeight, &memDC, 0, 0, SRCCOPY);

			// 恢复原来的位图
			memDC.SelectObject(pOldBmp);
		}
	}
	else
	{
		AfxMessageBox(_T("无法加载图片"));
	}
}  */


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


// C数据结构实验1Dlg 对话框



C数据结构实验1Dlg::C数据结构实验1Dlg(CWnd* pParent /*=nullptr*/)
	: CDialogEx(IDD_MY1_DIALOG, pParent)
	, name(_T(""))
	, nummber(10)
	, score(150)
	, picture(_T(""))
	, position(1)
	, Q_number(0)
	, Q_score(0)
	, Q_name(_T(""))
	, Q_picture(_T(""))
{
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void C数据结构实验1Dlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
	DDX_Text(pDX, IDC_EDIT3, name);
	DDX_Text(pDX, IDC_EDIT1, nummber);
	DDX_Text(pDX, IDC_EDIT2, score);
	DDX_Text(pDX, IDC_EDIT4, picture);
	DDX_Text(pDX, IDC_EDIT5, position);
	DDX_Text(pDX, IDC_EDIT7, Q_number);
	DDX_Text(pDX, IDC_EDIT9, Q_score);
	DDX_Text(pDX, IDC_EDIT6, Q_name);
	DDX_Text(pDX, IDC_EDIT10, Q_picture);
}

BEGIN_MESSAGE_MAP(C数据结构实验1Dlg, CDialogEx)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_BN_CLICKED(add, &C数据结构实验1Dlg::OnClickedAdd)
	ON_BN_CLICKED(IDC_BUTTON1, &C数据结构实验1Dlg::OnBnClickedButton1)
	ON_BN_CLICKED(IDC_BUTTON1, &C数据结构实验1Dlg::OnClickedButton1)
	ON_BN_CLICKED(IDC_BUTTON2, &C数据结构实验1Dlg::OnClickedButton2)
	ON_BN_CLICKED(push_back_button2, &C数据结构实验1Dlg::OnClickedPushBackButton2)
	ON_BN_CLICKED(IDC_BUTTON3, &C数据结构实验1Dlg::OnClickedButton3)
	ON_BN_CLICKED(push_back_button, &C数据结构实验1Dlg::OnClickedPushBackButton)
	ON_BN_CLICKED(IDC_BUTTON4, &C数据结构实验1Dlg::OnClickedButton4)
	ON_EN_CHANGE(IDC_EDIT10, &C数据结构实验1Dlg::OnChangeEdit10)
	ON_BN_CLICKED(IDC_BUTTON5, &C数据结构实验1Dlg::OnClickedButton5)
END_MESSAGE_MAP()


// C数据结构实验1Dlg 消息处理程序

BOOL C数据结构实验1Dlg::OnInitDialog()
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

void C数据结构实验1Dlg::OnSysCommand(UINT nID, LPARAM lParam)
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

void C数据结构实验1Dlg::OnPaint()
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
HCURSOR C数据结构实验1Dlg::OnQueryDragIcon()
{
	return static_cast<HCURSOR>(m_hIcon);
}

#include<stdio.h>
#include<malloc.h>
#include<string.h>

typedef int EleType;
int system(const char* command);

typedef struct Info {
	int nummber;
	double score;
	CString name;
	CString picture;
}Info;

typedef struct Node {
	Info info;
	struct Node* next;
}Node;

typedef struct List {
	Node* first;
	int  size;
}List;



/*void push_back(List* list)   //尾插 
{
	//获取结点
	Node* s = (Node*)malloc(sizeof(Node));
	//将插入结点与头结点连接
	s->next = list->last->next;
	s->next->prio = s;
	//将插入结点与上一尾结点连接
	s->prio = list->last;
	list->last->next = s;
	//修改双向链表管理结点的尾指针
	list->last = s;
	list->size++;
}

void push_front(List* list) {
	Node* s = (Node*)malloc(sizeof(Node));
	list->last->next = s;
	list->first->prio = s;
	s->next = list->first;
	s->prio = list->last;
	list->first = s;
	list->size++;
}   
int Delet(List* list, int pos) {
	if (pos == 0 || pos >= list->size + 1) {
		return 1;
	}
	Node* s = (Node*)malloc(sizeof(Node));
	s = list->first;
	for (int i = 0; i < pos; i++) {
		s = s->next;
	}
	s->next->prio = s->prio;
	s->prio->next = s->next;
}*/

Node* InitNode(int nummber,double score,CString name,CString picture) {
	Node* t = new Node;
	t->info.nummber = nummber;
	t->info.score = score;
	t->info.name = name;
	t->info.picture = picture;
	t->next = NULL; // New node's next should be NULL initially
	return t;
}

int Insert(List* list, int pos,CString name,int nummber,double score,CString picture) {


	int flag = 0;
	Node* s1 = (Node*)malloc(sizeof(Node));
	s1 = list->first->next;
	Node* t = InitNode(nummber, score,name,picture);

	if (pos == 0 || pos > list->size + 1) {
		return 1;          //位置不合理返回1
	}
	if (nummber == 0 || flag == 1)
	{
		return 2;          //学号不合理返回2
	}

	Node* s = (Node*)malloc(sizeof(Node));
	s = list->first;
	for (int i = 0; i < pos-1; i++) {
		s = s->next;
	}
	if (s->next == NULL) {
		s->next = t;
	}
	else {
		t->next = s->next;
		s->next = t;
	}
	//插入节点
	list->size++;
	return 0;
}

int Insert1(List* list, int pos, CString name, int nummber, double score, CString picture) {          //尾插

	int flag = 0;

	if (pos == 0 || pos > list->size + 1) {
		return 1;          //位置不合理返回1
	}
	if (nummber == 0 || flag == 1)
	{
		return 2;          //学号不合理返回2
	}

	Node* s = (Node*)malloc(sizeof(Node));
	Node* t = InitNode(nummber, score,name,picture);          //赋值
	if (list->first->next == NULL) {
		list->first->next = t;
		list->size++;
	}
	else {
		s = list->first;
		while (s->next != NULL) {
			s = s->next;
		}
		s->next = t;
		list->size++;
	}

	return 0;
}

Node* Get(List* list, int nummber) {

	Node* s = (Node*)malloc(sizeof(Node));
	s = list->first->next;
	while(s!=NULL){
		if (s->info.nummber == nummber) {
			//*score = s->info.score;
			return s;
		}
		s = s->next;
	}
	if (s == NULL) {
		return NULL;              //如果没有查询到，返回1
	}
}


void Initlist1(List* List) {
	Node* s = (Node*)malloc(sizeof(Node));
	if (s == NULL) {
		// 内存分配失败的处理
		fprintf(stderr, "Error: Failed to allocate memory.\n");
		exit(EXIT_FAILURE); // 或者根据情况进行其他错误处理
	}
	if (s != NULL) {
		List->first = s;
		List->first->next = NULL;
		List->size = 0;
	}
}







List* list = (List*)malloc(sizeof(List));

void C数据结构实验1Dlg::OnClickedAdd()          //按位置添加学生
{
	// 获取编辑框中的数值
	UpdateData(TRUE);
	//对链表进行添加
	CString name,picture,picture1;
	GetDlgItemText(IDC_EDIT3, name);
	GetDlgItemText(IDC_EDIT4, picture);
	MessageBox(name);

	if (picture.IsEmpty()) {
		picture1 = LoadAndDisplayImage(240, 350, 1050, 500);
		if (picture1.IsEmpty()) {
			MessageBox(_T("请选择一种照片输入方式"));
			return;
		}
		picture = picture1;
	}
	int jude = Insert(list, position, name, nummber, score, picture);
	if (jude==1) {
		MessageBox(_T("位置不合法"));
	}
	else if (jude == 2) {
		MessageBox(_T("学号不合法或重复"));
	}
	else if (jude == 52) {
		MessageBox(_T("没收到"));
	}
	else {
		MessageBox(_T("成功建立!"));
		
	}
	UpdateData(FALSE);
}


void C数据结构实验1Dlg::OnBnClickedButton1()     //初始化（重置）系统
{
	
	Initlist1(list);

	if(list->first!=NULL){ MessageBox(_T("链表已经建立"), _T("提示"), MB_OK | MB_ICONINFORMATION); }
	
}


void C数据结构实验1Dlg::OnClickedButton1()
{
	// TODO: 在此添加控件通知处理程序代码
}


void C数据结构实验1Dlg::OnClickedButton2()            //学号查询
{
	CString number1;
	GetDlgItemText(IDC_EDIT7, number1);
	int number2 = _ttoi(number1);
	Node* t = Get(list, number2);
	if (t == NULL) {
		MessageBox(_T("学生不存在！"));
	}
	else {
		MessageBox(_T("查询成功！"));
		Q_number = t->info.nummber;
		Q_score = t->info.score;
		Q_picture = t->info.picture;
		Q_name = t->info.name;
	}
	DisplayImage(240, 350, 1050, 500,t->info.picture);
	UpdateData(FALSE);
}


void C数据结构实验1Dlg::OnClickedPushBackButton2()    //查看学生人数
{
	CString strResult;
	strResult.Format(_T("链表大小为：%d"), list->size);

	// 弹出消息框显示结果
	MessageBox(strResult, _T("链表大小"), MB_OK | MB_ICONINFORMATION);
}

void C数据结构实验1Dlg::OnClickedButton3()             //测试
{
	CString strResult;
	strResult.Format(_T("第一个节点的学号为：%d"), list->first->next->info.nummber);

	// 弹出消息框显示结果
	MessageBox(strResult, _T("链表大小"), MB_OK | MB_ICONINFORMATION);
}


void C数据结构实验1Dlg::OnClickedPushBackButton()                  //尾插
{
	// 获取编辑框中的数值
	UpdateData(TRUE);
	//对链表进行添加
	CString name, picture, picture1;
	GetDlgItemText(IDC_EDIT3, name);
	GetDlgItemText(IDC_EDIT4, picture);
	MessageBox(name);

	picture1 = LoadAndDisplayImage(240, 350, 1050, 500);
	if (picture.IsEmpty()) {
		picture = picture1;
	}
	else {
		MessageBox(_T("请只选择一种照片方式"));
		return;
	}

	int jude = Insert1(list, position, name, nummber, score, picture);
	if (jude == 1) {
		MessageBox(_T("位置不合法"));
	}
	else if (jude == 2) {
		MessageBox(_T("学号不合法或重复"));
	}
	else {
		MessageBox(_T("成功建立!"));
	}
	UpdateData(FALSE);
}


void C数据结构实验1Dlg::OnClickedButton4()                      //添加图片按钮
{
	LoadAndDisplayImage(240,350,1050,500);
}


void C数据结构实验1Dlg::OnChangeEdit10()
{

}


void C数据结构实验1Dlg::OnClickedButton5()                       //更换图片
{
	CString number1;
	GetDlgItemText(IDC_EDIT7, number1);
	int number2 = _ttoi(number1);
	Node* t = Get(list, number2);
	t->info.picture = LoadAndDisplayImage(240, 350, 1050, 500);
	if (!t->info.picture.IsEmpty()) {
		MessageBox(_T("替换成功"));
	}
	else {
		MessageBox(_T("替换失败"));
	}
}
