/*#include<iostream>

using namespace std;
int n;

void show(int array[]){
	for(int i=0;i<n;i++){
		cout<<array[i]<<" ";
	}
	cout<<endl;
}
void swap(int &a,int &b){
	int temp;
	temp = a;
	a = b;
	b = temp;
}

void QuickSort(int array[], int low, int high){
	int start = low;
	int end = high;
	int temp;
	if(start>=end){
		return;
	}
	temp = array[start];
	while(start!=end){
		while(temp<=array[end]&& start < end){	
			end--;
		}
		while(temp>=array[start]&& start < end){
			start++;
		}
		if(start<end){
			swap(array[start],array[end]);
		}
	}
	swap(array[low],array[start]);
	QuickSort(array,low,start-1);
	QuickSort(array,start+1,high);
}

int main(){
	int k,a[1000];
	cin>>n>>k;
	for(int i=0;i<n;i++){
		cin>>a[i];
	}
	QuickSort(a,0,n-1);
	cout<<a[k-1]<<endl;	//快排后输出对应位置的数 
	return 0;
}*/

//寻找一个序列中第k小的元素
#include <iostream>
using namespace std;
#define MAXN 1000

int Solve(int a[], int s, int t, int k) {
    int i = s, j = t;
    int temp = a[s];

    while (i < j) {
        while (i < j && a[j] >= temp) j--;
        a[i] = a[j];
        while (i < j && a[i] <= temp) i++;
        a[j] = a[i];
    }
    a[i] = temp;

    if (k - 1 == i) return a[i];
    return (k - 1 < i) ? Solve(a, s, i - 1, k) : Solve(a, i + 1, t, k);
}

int main() {
    int n, k;
    int a[MAXN];
    
    cin >> n >> k;
    for (int i = 0; i < n; i++) cin >> a[i];

    cout << Solve(a, 0, n - 1, k) << endl;
    return 0;
}


