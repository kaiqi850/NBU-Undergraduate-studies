#include<stdio.h>
#include<stdlib.h>
#define MAXSIZE 100
typedef struct{
	int data[MAXSIZE];
	int top;
}Stack;

void InitStack(Stack &S){
	S.top = -1;
}

bool StackEmpty(Stack &S){
	if(S.top == -1){
		return true;
	}
	else{
		return false;
	}
}

int Push(Stack &S){
	int x;
	S.top += 1;
	printf("«Î ‰»Î ˝æ›\n");
	scanf("%d",&x);
	S.data[S.top] = x;
	return x;
}

int Pop(Stack &S){
	int x;
	return S.data[S.top--];
}

int GetTop(Stack &S){
	int x;
	return S.data[S.top];
}

int main(){
	int i = 1;
	printf("%d",(++i)+(++i));
}
