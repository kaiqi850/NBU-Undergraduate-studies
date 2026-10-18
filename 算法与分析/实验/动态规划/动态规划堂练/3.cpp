/*#include<bits/stdc++.h>
using namespace std;

int n;
int arr1[101];
int max1 = 0;
int min1 = 0;
int main(){
	cin >>n;
	for(int i =0;i<n;i++){
		cin >> arr1[i];
	}
	
	sort(arr1,arr1+n);
	
	for(int i =0;i<n;i++){
		min1 += (n-i)*arr1[i];
	}
	min1 = min1-arr1[0];
	
	for(int i = n;i>=1;i--){
		max1 += i*arr1[i-1];
	}
	max1 = max1-arr1[n-1];
	cout<<min1<<endl;
	cout<<max1<<endl;
} */



/*4+4+(8+5)+(13+9)
4+4+4+4+5+4+4+5+9
9+5+9+5+4+9+5+4+4*/


#include <bits/stdc++.h>
using namespace std;

const int INF = 1e9;
int n;
int stones[210];
int prefix[210];
int dp_min[210][210];
int dp_max[210][210];

int main() {
    cin >> n;
    for (int i = 1; i <= n; i++) {
        cin >> stones[i];
        stones[i + n] = stones[i];//»·ÐÎ 
    }

    for (int i = 1; i <= 2 * n; i++) {
        prefix[i] = prefix[i - 1] + stones[i];
    }

    for (int i = 1; i <= 2 * n; i++) {
        for (int j = 1; j <= 2 * n; j++) {
            if (i == j) {
                dp_min[i][j] = dp_max[i][j] = 0;
            } else {
                dp_min[i][j] = INF;
                dp_max[i][j] = 0;
            }
        }
    }


    for (int len = 2; len <= n; len++) { 
        for (int i = 1; i + len - 1 <= 2 * n; i++) {
            int j = i + len - 1;
            for (int k = i; k < j; k++) {
                int sum = prefix[j] - prefix[i - 1];
                dp_min[i][j] = min(dp_min[i][j], dp_min[i][k] + dp_min[k + 1][j] + sum);
                dp_max[i][j] = max(dp_max[i][j], dp_max[i][k] + dp_max[k + 1][j] + sum);
            }
        }
    }

    int res_min = INF, res_max = 0;
    for (int i = 1; i <= n; i++) {
        res_min = min(res_min, dp_min[i][i + n - 1]);
        res_max = max(res_max, dp_max[i][i + n - 1]);
    }

    cout << res_min << endl;
    cout << res_max << endl;
    return 0;
}

