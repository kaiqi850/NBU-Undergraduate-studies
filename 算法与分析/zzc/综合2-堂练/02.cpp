#include <iostream>
using namespace std;

int M;
int lawn[100][100];
int visited[100][100]={0};

void dfs(int row, int col) {		// 深度搜索 
    visited[row][col] = 1;			//代表这个节点被搜索过 
    if (row > 0 && lawn[row - 1][col] == 1 && visited[row - 1][col] == 0) 	//往左侧节点搜索 
		dfs(row - 1, col);
    if (row < M - 1 && lawn[row + 1][col] == 1 && visited[row + 1][col] == 0) 	//往右侧节点搜索 
		dfs(row + 1, col);
    if (col > 0 && lawn[row][col - 1] == 1 && visited[row][col - 1] == 0) 		//往上方节点搜索 
		dfs(row, col - 1);
    if (col < M - 1 && lawn[row][col + 1] == 1 && visited[row][col + 1] == 0) 	//往下方节点搜索 
		dfs(row, col + 1);
}

int main() {
    cin >> M;
    for (int i = 0; i < M; i++) {		//建图 
        for (int j = 0; j < M; j++) {
            cin >> lawn[i][j];
        }
    }
    int count = 0;
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < M; j++) {
            if (lawn[i][j] == 1 && visited[i][j] == 0) {	//如果是花且未被搜索过，则花的品种+1 
                count++;
                dfs(i, j);		//深搜，排除同一种类的花的数量 
            }
        }
    }
    cout << count << endl;
    return 0;
}

