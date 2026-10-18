#include<iostream>
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
using namespace std;

typedef struct node
{
	int x, y, t, step;
}strnode;
int m, n, t;
int d[4][2] = { {-1,0},{0,-1},{1,0},{0,1} };
char map[201][201];
int is[201][201][10];
strnode que[44000];
int bfs(int x, int y)
{
	memset(is, 0, sizeof(is));
	int head = 0, tail = 0, i = 0;
	que[tail].x = x;
	que[tail].y = y;
	que[tail].t = t;
	que[tail++].step = 0;
	is[x][y][t] = 1;
	while (head < tail)
	{
		strnode temp = que[head++];
		if (map[temp.x][temp.y] == '+')
		{
			return temp.step;
		}
		for (i = 0; i < 4; i++)
		{
			int dx = temp.x + d[i][0];
			int dy = temp.y + d[i][1];
			if (dx >= 0 && dy >= 0 && dx < m && dy < n && temp.t >= 1)
			{
				if (map[dx][dy] != '*'&&!is[dx][dy][temp.t])
				{
					que[tail].x = dx;
					que[tail].y = dy;
					que[tail].t = temp.t;
					que[tail++].step = temp.step + 1;
					is[dx][dy][temp.t] = 1;
					cout<<1<<endl;
				}
				if (map[dx][dy] == 'w' )
				{
					int dt = temp.t - 1;
					if (!is[dx][dy][dt])
					{
						que[tail].x = dx;
						que[tail].y = dy;
						que[tail].t = dt;
						que[tail++].step = temp.step + 1;
						is[dx][dy][dt] = 1;
						cout<<2<<endl;
					}
				}
			}
		}
	}
	return -1;
}
int main()
{
	scanf("%d%d%d", &m, &n, &t);
	int i = 0, j = 0;
	for (i = 0; i < m; i++)
	{
		getchar();
		scanf("%s", map[i]);
	}
	for(i=0;i<m;i++)
		for (j = 0; j < n; j++)
		{
			if (map[i][j] == '!')
				printf("%d",bfs(i, j));
		}
	return 0;
}

