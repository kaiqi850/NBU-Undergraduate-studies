#include<bits/stdc++.h>
using namespace std;

int cnt = 0;
int a[10000] = {0};

void Merge(int source[],int s,int m,int e){     //source是原数组，temp是暂时的数组，s是开头，m是中间，e是结尾
	 int i = s,j = m+1,k = s;
	 int temp[100];
	 while(i!=m+1 && j!=e+1){
	 	if(source[i]<=source[j]){
	 		temp[k++] = source[i++];
		 }
		 else{
		 	temp[k++] = source[j++];
		 	cnt += m-i+1;
		 }
	 }
	 if(i == m+1){
	 	while(j!=e+1){
	 		temp[k++] = source[j++];
		 }
	 	
	 }
	 else if(j == e+1){
	 	while(i!=m+1){
	 		temp[k++] = source[i++];
		 }
	 }
	 for(int i = 0;i<=e;i++){
	 	source[i] = temp[i];
	 }
}

void MergeSort(int source[],int s,int e){
	if(s<e){
		int mid = (s+e)/2;
		MergeSort(source,s,mid);
		MergeSort(source,mid+1,e);
		Merge(source,s,mid,e);
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
