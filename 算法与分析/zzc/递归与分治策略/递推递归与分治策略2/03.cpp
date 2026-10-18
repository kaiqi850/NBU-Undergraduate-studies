/*给定一个序列a1,a2,…,an，如果存在i<j并且ai>aj，那么我们称之为逆序对，求逆序对的数目。
要求用分治法求解。
*/

#include<iostream>
using namespace std;
static int cnt = 0;
int a[10000] = {0};
static void merge(int array[],int p,int q,int r)	//分治法中合并两块，p,q,r分别为起始、中间、结束索引 
{
	int k = 0;
	int begin1,end1,begin2,end2;	//分别代表左右两块的起始/终止索引 
	int* temp = new int[r-p+1];		//创建临时数组temp 
	begin1 = p;	end1 = q;
	begin2 = q+1;	end2 = r;
	while((begin1 <= end1)&&(begin2 <= end2)){	//判断两边都未排序完成 
		if(array[begin1]<=array[begin2]){	
			temp[k] = array[begin1];
			begin1++;
		}
		else{						//左边的序列要大于右边，存在逆序对，且因为两块是排列完的序列，所以左边接下来的数列都要大。 
			temp[k] = array[begin2];
			begin2++;
			cnt += end1 - begin1 + 1;
		}
		k++;
	}
	//将剩余的数加入临时数组temp 
	while(begin1<=end1){
		temp[k++] = array[begin1++];
	}
	while(begin2<=end2){
		temp[k++] = array[begin2++];
	}
	//将临时数组存入数组中。 
	for(int i=0;i<(r-p+1);i++){
		array[p+i] = temp[i];
	}
	delete[] (temp);
}

//分治排序 
void MergeSort(int array[],int p,int r){
	if(p<r){
		int Mid = (p+r)/2;
		MergeSort(array,p,Mid);
		MergeSort(array,Mid+1,r);
		merge(array,p,Mid,r);
	}
}

int main(){
	int n;
	cin>>n;
	for(int i=0;i<n;i++)
		cin>>a[i];
	MergeSort(a,0,n-1);
	cout<<cnt<<endl;
	return 0;
}


void Merge(int sourceArr[],int tempArr[], int startIndex, int midIndex, int endIndex){
    int i = startIndex, j=midIndex+1, k = startIndex;
    while(i!=midIndex+1 && j!=endIndex+1) {
        if(sourceArr[i] > sourceArr[j])
            tempArr[k++] = sourceArr[j++];
        else
            tempArr[k++] = sourceArr[i++];
    }
    while(i != midIndex+1)
        tempArr[k++] = sourceArr[i++];
    while(j != endIndex+1)
        tempArr[k++] = sourceArr[j++];
    for(i=startIndex; i<=endIndex; i++)
        sourceArr[i] = tempArr[i];
}
 
//内部使用递归
void MergeSort(int sourceArr[], int tempArr[], int startIndex, int endIndex) {
    int midIndex;
    if(startIndex < endIndex) {
        midIndex = startIndex + (endIndex-startIndex) / 2;//避免溢出int
        MergeSort(sourceArr, tempArr, startIndex, midIndex);
        MergeSort(sourceArr, tempArr, midIndex+1, endIndex);
        Merge(sourceArr, tempArr, startIndex, midIndex, endIndex);
    }
}
 

