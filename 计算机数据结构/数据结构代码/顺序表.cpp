#include<stdio.h>
#include<stdlib.h>

int MAXSIZE = 100;
typedef int ElemType;
typedef int Status;

int menu(){
	int choice;
	printf("请输入您要的选择：\n1.创建新表\n2.插入元素\n3.删除元素\n4.展示表\n5.翻转表\n6.删除指定元素\n0.退出\n");
	scanf("%d",&choice);
	printf("------------------\n");
	return choice;
} 
typedef struct {
	ElemType *elem;
	int length;
} SqList;

Status InitList(SqList* L){
    //构造一个空的线性表L
    L -> elem = (ElemType *)malloc(MAXSIZE*sizeof(ElemType));
    if(!L -> elem){
        return 0;
    }
    L -> length = 0;
    return 1;
}

Status ListInsert(SqList *L, int i, ElemType e){
    int k;
    if (L->length == MAXSIZE){  //线性表已满
        return 0;
    }   
    if (i < 1 || i > L->length+1){ //当i不在范围内时
        return 0;
    }
    if (i <= L->length){  //若插入位置不在表尾
        for(k = L->length-1;k >= i-1;k--){
            L->elem[k+1] = L->elem[k];
        }	
    }   
    L->elem[i-1] = e;   //将新元素插入
    L->length++;    //长度加1
    return 1;
}

Status ListDelet(SqList *L,int i,ElemType *e){  
    int k;
    if (i < 1 || i >= L->length+1){ //当i不在范围内时
        return 0;
    }
    *e = L->elem[i-1];
    if(i < L->length){
    	for(k = i-1 ; k<=L->length-2 ; k++){
    		L->elem[k] = L->elem[k+1];
		}
	}
	L->length--;
	return 1; 
}

void ListShow(SqList *L){
	int k;
	for(k = 0;k<L->length;k++){
		printf("%d\n",L->elem[k]);
	}
	
}

void ListConverse(SqList *L){
	int i,temp;
	for(i = 0;i<L->length/2;i++){
		temp = L->elem[i];
		L->elem[i] = L->elem[L->length-i-1];
		L->elem[L->length-i-1] = temp;
	}
}
void ListDeletElem(SqList *L){
	int i,k = 0,x;
	printf("请输入删除元素:");
	scanf("%d",&x);
	for(i = 0; i < L->length ; i++){
		if(L->elem[i] != x){
			L->elem[k++] = L->elem[i];
		}
	}
	L->length = k;
}

void DeletSame(SqList *L){  //仅使用于有序表 
	int i,k;
	for(i = 0 ,j = 1 ; j <L->length ; j++){
		if(L->elem[i]!= L->elem[j]){
			L->elem[++i] = L->elem[j];
		}
	}
	L->length = i+1;
}

void ListComplex(SqList A,SqList B,SqList *L){   //合成新表，仅适用于有序表 
	int i=0,j=0,k=0;
	while(i<A.length && j<B.length){
		if(A.elem[i]>=B.elem[j]){
			L->elem[k++] = B.elem[i++];
		}
		else{
			L->elem[k++] = A.elem[j++];
		}
	}
	while(i<A.length){
		L->elem[k++] = A.elem[i++];
	}
	while(j<B.length){
		L->elem[k++] = B.elem[j++];
	}
	L->length = k;
}
int main() {
   SqList sql;
   SqList * p = &sql;
   InitList(p); 
   int a,choice,pos,delet,flag = 0;
   int *p_delet = &delet;
   while(1){
   	choice = menu();
   	switch(choice){
   		case(1):
   			InitList(p); 
   			printf("已经创建\n");
			break;
		case(2):
			printf("请输入元素:\n");
   	        scanf("%d",&a);
   	        printf("请输入位置:\n");
   	        scanf("%d",&pos);
	        if(!ListInsert(p,pos,a)){
	        	printf("ERROR，请重新选择\n");
			}
			break;
		case(3):
		    printf("请输入要删除的位置\n");
			scanf("%d",&pos);
			if(!ListDelet(p,pos,p_delet)){
	        	printf("ERROR，请重新选择\n");
			}
			else{
				printf("被删除的元素是：%d",*p_delet);
			}
			break;
		case(4): 
		    ListShow(p);
		    break;
		case(5):
			ListConverse(p);
			break;
		case(6):
			ListDeletElem(p);
			break;
		case(0):
			flag = 1;
			break;
	   }
	   printf("目前长度是：%d\n",p->length);  
	if(flag){
		break;
	}
   }
   return 0;
}
