/*输入n个数，求其中第k小的数。（要求采用分治法完成，不建议采用完整的排序）
第一行包含两个整数n和k；n<1000，1<=K<=n
第二行包含n个整数。
可以使用快速排序算法 
*/

#include<iostream>
using namespace std;

//用于将两个数的值进行交换 
void swap(int &a,int &b){
	int temp;
	temp = a;
	a = b;
	b = temp;
}

//快速排序算法 
void QuickSort(int array[], int low, int high) {
    int i = low; 
    int j = high;
    if(i >= j) {
        return;
    }
 
    int temp = array[low];
    while(i != j) {
        while(array[j] >= temp && i < j) {
            j--;
        }
	while(array[i] <= temp && i < j) {
            i++;
        }
	if(i < j) {
            swap(array[i], array[j]);
        }
    }
 
    //将基准temp放于自己的位置，（第i个位置）
    swap(array[low], array[i]);
    QuickSort(array, low, i - 1);
    QuickSort(array, i + 1, high);
}


int main(){
	int n,k,a[1000];
	cin>>n>>k;
	for(int i=0;i<n;i++){
		cin>>a[i];
	}
	QuickSort(a,0,n-1);
	cout<<a[k-1]<<endl;	//快排后输出对应位置的数 
	return 0;
}








