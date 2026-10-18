#include<stdio.h>
#include<stdlib.h>

typedef struct Node{
	int data;
	Node* prior,* next;
}Node;

Node* creat(Node* L){
	int x;
	L = (Node*)malloc(sizeof(Node));
	L->data = 0;
	L->next = NULL;
	L->prior = NULL;
	Node* r = (Node*)malloc(sizeof(Node));
	r = L;
	printf("请输入数据，输入9999停止");
	scanf("%d",&x);
	while(x!=9999){
		Node* s = (Node*)malloc(sizeof(Node));
		s->prior = r;
		r->next = s;
		r = s;
		s->data = x;
		printf("请输入数据，输入9999停止");
        scanf("%d", &x);
	}
	return L;
}

void insert(Node* L,int i){          //i节点后新增一个节点 
	int j=1;
	Node* s = L;
	while(j<i&&s->next!NULL){
		s = s->next;
	}
	printf("请输入数据，输入9999停止");
    scanf("%d", &x);
    Node* r =(Node*)malloc(sizeof(Node)); 
    r->data = x;  //数据  
	r->next = s->next;    //中连接后
	s->next->prior = r;   //后连接中 
	s->next = r;          //前连接中
	r->prior = s;         //中连接前 
}

void delet(Node* L,int i){
	int j=1;
	Node* s = L;
	while(j<i&&s->next!NULL){
		s = s->next;
	}
	s->prior->next = s->next;
	s->next->prior = s->prior;
}
int main(){
	
}
