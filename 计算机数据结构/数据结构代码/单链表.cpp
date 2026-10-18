#include<stdio.h>
#include<stdlib.h> 

typedef struct Node{
	int data;
	struct Node *next;
}Node;

Node* creathead(){
	Node* head = (Node*)malloc(sizeof(Node));
	head->data = 0;
	head->next = NULL; 
	return head;
}

Node* head_insert(Node *L){    //头插法 
	int x;
	L = (Node*)malloc(sizeof(Node));
	printf("请输入元素，输入9999停止\n");
	scanf("%d",&x);
	while(x!=9999){
		Node* l = (Node*)malloc(sizeof(Node));
		l->data = x;
		l->next = L->next;
		L->next = l;
		printf("请输入元素，输入9999停止\n");
		scanf("%d",&x);
	}
	return L;
}

Node* foot_insert(Node* L){     //尾插法 
	int x;
	L = (Node*)malloc(sizeof(Node));
	Node* s,*r = L;
	printf("请输入元素，输入9999停止\n");
	scanf("%d",&x);
	while(x!=9999){
		Node* s = (Node*)malloc(sizeof(Node));
		s->data = x;
		r->next = s;
		r = s;   
		printf("请输入元素，输入9999停止\n");
		scanf("%d",&x);	 
	}
	r->next =NULL; 
	return L;
}

Node* findxuhao(Node* L,int i){   //查找节点 序号 
	int j=1;
	Node* p = L->next;
	while(j<i&&p!=NULL){
		p = p->next;
		j++;
	}
	return p;
}

Node* findzhi(Node* L,int x){   //查找节点，值 
	int j;
	Node* p =L->next;
	while(p!=NULL){
		if(p->data == x){
			return p; 
		}
		p = p->next;	
	}
	return p;
}

void insert(Node* L){
	int x,i;
	printf("请输入要插入的数据和位置\n");
	scanf("%d%d",x,i);
	Node* s = (Node*)malloc(sizeof(Node));
	Node* p =findxuhao(L,i-1);
	s->next = findxuhao(L,i+1); //s->next = p->next;
	p->next = s;
	s->data = x;
}

void delet(Node *L){
	int i;
	printf("请输入要删除的位置\n");
	scanf("%d",i);
	Node* p =findxuhao(L,i-1);
	Node* p1 = findxuhao(L,i+1);
	p->next = p1;
}
int main(){
	Node* node = creathead();
	//printf("%d",node->data);
	head_insert(node);
	
}


