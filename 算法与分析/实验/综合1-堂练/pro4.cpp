#include<iostream>
#include<algorithm> 
using namespace std;

struct Section{
	int num1;
	int num2;
};

// 根据区间的左端点进行升序排序
// 左端点一致的根据右端点升序排序 
bool cmp(Section s1, Section s2){
	if(s1.num1<s2.num1)
		return true;
	else if(s1.num1==s2.num1 && s1.num2<s2.num2)
		return true;
	else 
		return false;
}

void Solve(Section a[],int n){
	int cnt = 0;
	Section ans[100];
	sort(a, a+n, cmp);
	int right = a[0].num1-1;	// 覆盖区域的右端点区域的终点 
	int end = a[n-1].num2;  
    // 找到一个区间左端点在已覆盖区域内，右端点尽可能长 
	for(int i=0; i<n-1; ){
		int max_right = a[i].num2, max_index = i;
		while(a[i].num1<=right+1 && i<n){
			if(a[i].num2>max_right){
				max_right = a[i].num2;
				max_index = i;
			}
			i++;
		} 
		right = max_right;
		ans[cnt++] = a[max_index];
		i = max_index;
		if(right == end)
			break;		
	}
	
	for(int i=0; i<cnt; i++){
		cout << ans[i].num1 << " " << ans[i].num2 << endl;
	}
}


int main()
{
	Section a[100];
	int n;  // 区间的个数  
	cin>>n;
	for(int i=0; i<n; i++){
		cin >> a[i].num1 >> a[i].num2;
	}
	Solve(a,n);
	return 0;
}

