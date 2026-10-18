#include<stdlib.h>
#include<iostream>
#include <queue>
using namespace std;
typedef int DataType;
int width,height;
typedef struct BinaryTree
{
	struct BinaryTree* lchild; // 第一个孩子结点
	struct BinaryTree* rchild; // 指向其下一个兄弟结点
	DataType data; // 结点中的数据域
	int height1 = 1;
}BTNode;

typedef struct Queue
{
    BTNode* node[10000];
    int front;    //头指针
    int rear;    //尾指针
}Queue;

Queue* Init_Queue(Queue *que){
	que = (Queue*)malloc(sizeof(Queue));
	if(que != NULL){
		que->front =0;
		que->rear =0;
	}
	return que; 
}

BTNode* Init_Btree(BTNode* root){
	root = (BTNode*)malloc(sizeof(BTNode));
	root->lchild = NULL; 
	root->rchild = NULL;
	root->height1 = 1;
	return root;
}
int Empty_Queue(Queue *que){
	if(que->front == que->rear){
		return 1;
	}
	else
	return 0;
}
void Enter_Queue(Queue *que,BTNode *root){
	que->node[que->rear++] = root;
}

BTNode* Delete_Queue(Queue *que){
	BTNode* node1 = que->node[que->front++];
	return node1;
}

void PreOrder(BTNode *root){
	if(root == NULL){
		return;
	}
		printf("%d ",root->data);
		PreOrder(root->lchild);
		PreOrder(root->rchild); 
}

void InOrder(BTNode *root){
	if(root == NULL){
		return;
	}
	InOrder(root->lchild);
	printf("%d ",root->data);
	InOrder(root->rchild); 
}

void PostOrder(BTNode *root){
	if(root == NULL){
		return;
	}
	PostOrder(root->lchild);
	PostOrder(root->rchild);
	printf("%d ",root->data);
}

void TreeLevelOrder(BTNode* root){
	Queue* que;
	que = Init_Queue(que);
	Enter_Queue(que,root);
	while(!Empty_Queue(que)) {
		BTNode * node = Delete_Queue(que);
		printf("%d ",node->data);
		if(node->lchild!=NULL){
			Enter_Queue(que,node->lchild);
		}
		if(node->rchild!=NULL){
			Enter_Queue(que,node->rchild);
		}
	}
}
int max(int a, int b)
{
    return (a > b) ? a : b;
}

// 计算节点的高度
int Height(BTNode *root)
{
    if (root == NULL)
        return 0;
    return root->height1;
}

// 更新节点的高度
void UpdateHeight(BTNode *root)
{
    if (root != NULL)
    {
        root->height1 = 1 + max(Height(root->lchild), Height(root->rchild));
    }
}

// 计算节点的平衡因子
int BalanceFactor(BTNode *root)
{
    if (root == NULL)
        return 0;
    return Height(root->lchild) - Height(root->rchild);
}

// 左旋
BTNode *RotateLeft(BTNode *root)
{
    BTNode *newRoot = root->rchild;
    root->rchild = newRoot->lchild;
    newRoot->lchild = root;
    // 更新节点高度
    UpdateHeight(root);
    UpdateHeight(newRoot);
    return newRoot;
}

// 右旋
BTNode *RotateRight(BTNode *root)
{
    BTNode *newRoot = root->lchild;
    root->lchild = newRoot->rchild;
    newRoot->rchild = root;
    // 更新节点高度
    UpdateHeight(root);
    UpdateHeight(newRoot);
    return newRoot;
}

// 平衡节点
BTNode *BalanceNode(BTNode *root)
{
    // 更新节点高度
    UpdateHeight(root);

    // 计算平衡因子
    int balance = BalanceFactor(root);

    // 左子树高度较大，需要进行右旋
    if (balance > 1)
    {
        if (Height(root->lchild->rchild) > Height(root->lchild->lchild))
        {
            root->lchild = RotateLeft(root->lchild);
        }
        return RotateRight(root);
    }
    // 右子树高度较大，需要进行左旋
    else if (balance < -1)
    {
        if (Height(root->rchild->lchild) > Height(root->rchild->rchild))
        {
            root->rchild = RotateRight(root->rchild);
        }
        return RotateLeft(root);
    }
    return root;
}

BTNode *Insert_BTree(BTNode *root, DataType data)
{
    if (root == NULL)
    {
        root = Init_Btree(root);
        root->data = data;
    }
    else if (data < root->data)
    {
        root->lchild = Insert_BTree(root->lchild, data);
    }

    else if (data > root->data)
    {
        root->rchild = Insert_BTree(root->rchild, data);
    }

    // 平衡节点
    return BalanceNode(root);
}

BTNode* Search_BTree(BTNode* root,DataType data){
	if(root->data == data){
		return root;
	}
	else if(root->data > data){
		return Search_BTree(root->lchild,data);
	}
	else if(root->data < data){
		return Search_BTree(root->rchild,data);
	}
	else{
		return NULL;
	} 
}

BTNode* Delet(BTNode* root,DataType data){
	if(root == NULL){
		return NULL;
	}
	else if(root->data < data){
		root->rchild = Delet(root->rchild,data);
		return root;
	}
	else if(root->data > data){
		root->lchild = Delet(root->lchild,data);
		return root;
	}
	else if(root->data == data){
		if(root->lchild == NULL && root->rchild == NULL)
		{
			free(root);
			return NULL;
		}
		else if(root->lchild == NULL && root->rchild !=NULL){
			return root->rchild;
		}
		else if(root->rchild == NULL && root->lchild !=NULL){
			return root->lchild;
		}
		else{
			BTNode* left = root->lchild;
			while(left->rchild != NULL){
				left = left->rchild; 
			}
			left->rchild = root->rchild;
			return root->lchild;
		}
	}
	else{
		return NULL;
	}
}
int DeepTree(BTNode* T)
{
    if(!T)
    {
        return 0;
    }
    return DeepTree(T->lchild)>DeepTree(T->rchild)?DeepTree(T->lchild)+1:DeepTree(T->rchild)+1;
}

void fillArray(BTNode* &T,int *a,int i, int j)
{
    int ti,tj;
    if(T) //如果该位置有节点
    {
        *(a+(i*width)+j) = T->data; //向数组该点填入字符
        if(T->lchild) //有左右孩子给对应的连接线,左右孩子的值在下一层递归赋
        {
            //将该点与其左孩子之间的连线全部填上'/'
            for(ti=i+1,tj=j-1;tj>j-(height-i+1)/2;tj--)
            {
                *(a+((ti)*width)+tj) = -1;
                ti++;
            }
        }
        if(T->rchild)
        {
            for(ti=i+1,tj=j+1;tj<j+(height-i+1)/2;tj++)
            {
                *(a+((ti)*width)+tj) = 1;
                ti++;
            }
        }
        //经过循环,ti恰好指到其孩子所在的层
        fillArray(T->lchild, a, ti, j-(height-i+1)/2);
        fillArray(T->rchild, a, ti, j+(height-i+1)/2);
    }
}

void printBiTree(BTNode* &T)
{
    int i,j;
    int n = DeepTree(T); //计算出深度n
    //在计算机中数据以二进制形式存储,所以一个数据左移1位就相当于乘以2的1次方
    width = (2<<n)-3;  // 2^(n+1)-3
    height = (2<<(n-1))-1; // 2^n-1
    int *a = (int *)malloc(sizeof(int) * (width*height)); // 申请空间
 
    // 空间初始化为0
    for(i=0;i<height;i++)
    {
        for(j=0;j<width;j++)
        {
            *(a+(i*width)+j) = 0;
        }
    }
 
    //调用之前定义好的函数,填充打印数组
    fillArray(T, a, 0, (width-1)/2);
 
    //根据打印数组的内容来实现打印
    for(i=0;i<height;i++)
    {
        for(j=0;j<width;j++)
        {
            if(*(a+(i*width)+j) == -1)
            {
                printf("/");
            }else if(*(a+(i*width)+j) == 1)
            {
                printf("\\");
            }else if(*(a+(i*width)+j) == 0)
            {
                printf(" ");
            }else
            {
                printf("%d", *(a+(i*width)+j));
            }
        }
        printf("\n");
    }
}


int main(){
	BTNode* root = NULL;
	BTNode* node = NULL;
	int num[100] = {12,78,23,63,35,16,13,61,87,70,27};
	// int numSize = sizeof(num) / sizeof(num[0]);
    int i = 0;
    for(i = 0;i < 11;i++){
    	root = Insert_BTree(root,num[i]);
	}
	//printBiTree(root);
	// InOrder(root);
	node = Delet(root,63);
	printBiTree(root);
}

