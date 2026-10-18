#include<stdio.h>
#include<string.h>
#include<time.h>
#include<stdlib.h>

typedef struct card
{
    char suit[10];    //花色
    char face[10];    //牌面
} CARD;

void Initialize(int result[]);     //按新牌顺序编号
void Shuffle(int result[]);        //通过对编号随机置乱，实现洗牌
void FillCard(CARD card[]);        //填充牌面和花色
void Deal(CARD card[], int result[]);  //输出

void Initialize(int result[])
{
    int i;
    for(i=0;i<54;i++) // 修改为54张牌
    {
        result[i]=i;
    }
}

void Shuffle(int result[]) {
    int n = 54; // 数组的长度
    int iterations = 1000; // 定义热力学洗牌的迭代次数，可根据需要调整

    for (int outer = 0; outer < iterations; outer++) {
        for (int i = 0; i < n - 1; i++) {
            // 以一定的概率交换相邻元素
            if (rand() % 2 == 0) {		//在这里我们设置以50%的概率逐步随机地交换元素 
                int temp = result[i];
                result[i] = result[i + 1];
                result[i + 1] = temp;
            }
        }
    }
}

void FillCard(CARD card[])
{
    int i;
    char suits[5][10] = {"红心", "方块", "黑桃", "梅花", "小丑"}; // 添加Jokers花色
    char faces[15][10] = {"2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "黑", "红"}; // 添加大小王牌面

    for(i = 0; i < 52; i++)
    {
        strcpy(card[i].suit, suits[i / 13]);
        strcpy(card[i].face, faces[i % 13]);
    }
    // 添加两张Joker牌
    strcpy(card[52].suit, suits[4]); // Jokers花色
    strcpy(card[52].face, faces[13]); // Small Joker牌面
    strcpy(card[53].suit, suits[4]); // Jokers花色
    strcpy(card[53].face, faces[14]); // Big Joker牌面
}

void Deal(CARD card[], int result[])
{
    int i;
    for(i = 0; i < 54; i++)
    {
        printf("%-6s%-4s  ", card[result[i]].suit, card[result[i]].face); // 格式对齐输出
        if((i + 1) % 9 == 0)
            printf("\n"); // 每9张牌换一行
    }
}


int main()
{
	srand(time(NULL)); // 初始化随机数生成器
    CARD card[54]; // 修改为54张牌
    int result[54]; // 修改为54张牌
    FillCard(card);          //将牌面和花色顺序存放于结构体数组card
    Initialize(result);      //将牌编号存放于数组result中
    Deal(card,result);      //输出洗牌前的结果
    Shuffle(result);         //洗牌
    printf("在洗牌后：\n");
    Deal(card,result);      //输出洗牌后的结果
    return 0;
}
