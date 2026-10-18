#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

// 获取中位数
int medianOfMedians(vector<int>& a, int left, int right) {		 
    if (right - left < 5) {		//找到的中位数作为枢纽元 
        sort(a.begin() + left, a.begin() + right + 1);
        return a[left + (right - left) / 2];
    }

    for (int i = left; i <= right; i += 5) {	//将数组分成多个组，每组最多五个元素，并将找到的中位数移动至最左侧 
        int subRight = min(i + 4, right);
        sort(a.begin() + i, a.begin() + subRight + 1);
        int medianIdx = i + (subRight - i) / 2;
        swap(a[medianIdx], a[left + (i - left) / 5]);
    }

    return medianOfMedians(a, left, left + (right - left) / 5);		//递归找到中位数的中位数 
}

//分区函数 
int partition(vector<int>& a, int left, int right, int pivot) {
    for (int i = left; i <= right; ++i) {	//找到枢纽元并将其移动到数组的最右侧 
        if (a[i] == pivot) {
            swap(a[i], a[right]);
            break;
        }
    }

    int i = left;
    for (int j = left; j < right; ++j) {	//对数组进行分区 
        if (a[j] < pivot) {
            swap(a[i], a[j]);
            ++i;
        }
    }
    swap(a[i], a[right]);
    return i;		//返回枢纽元的最终位置 
}

int selectK(vector<int>& a, int left, int right, int k) {
    while (true) {
        if (left == right) {
            return a[left];
        }

        int pivot = medianOfMedians(a, left, right);	//使用medianOfMedians函数找到枢纽元 
        int pivotIndex = partition(a, left, right, pivot);	//对数组进行分区，并找到枢纽元的位置 

        int rank = pivotIndex - left + 1;
        if (rank == k) {	//若正好找到 
            return a[pivotIndex];
        } else if (rank > k) {		//若枢纽元比k大，则往左边找 
            right = pivotIndex - 1;
        } else {					//若枢纽元比k小，则往右边找 
            k = k - rank;
            left = pivotIndex + 1;
        }
    }
}

int main() {
    vector<int> a = {1, 8, 4, 9, 0, 32, 45, 27, 6, 5};
    int k = 5;
    int ans = selectK(a, 0, a.size() - 1, k);
    cout << "The " << k << "-th smallest element is: " << ans << endl;
    return 0;
}

