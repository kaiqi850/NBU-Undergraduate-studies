#include <iostream>
#include <algorithm>
#include <cstdio>
using namespace std;

const int N = 1000;
int s[N];
int num = 0; // 众数的重数
int idx = 0; // 众数的下标
 
void split(int l, int r) {
    if (l > r) return;
    int ll = l, rr = r;  // 保留l合r
    
   // 查找当前区间内的众数及其重数
    int mid = (ll + rr) / 2;
    int count = 1;
    // 统计左侧出现的次数
    for (int i = mid - 1; i >= ll && s[i] == s[mid]; i--) count++;
    // 统计右侧出现的次数
    for (int i = mid + 1; i <= rr && s[i] == s[mid]; i++) count++;
    
    // 更新众数及其重数
    if (count > num ) {
        num = count;
        idx = mid;
    }
    if(count == num && s[mid] < s[idx])
    	idx = mid;
 
 	l = mid;
 	r = mid;
   // 若左边个数够，还有机会 
    if ((l - 1) - ll + 1 >= num) split(ll, l - 1); 
    // 若右边数数够，还有机会
    if (rr - (r + 1) + 1 >= num) split(r + 1, rr); 
}
 
int main() {
    int n;
    scanf("%d", &n);
    for (int i = 0; i < n; i++) scanf("%d", s + i);
    sort(s, s + n); // 升序
    int left = 0;  
    int right = n - 1;
    split(left, right);
    printf("%d %d\n", s[idx], num);
    return 0;
}
