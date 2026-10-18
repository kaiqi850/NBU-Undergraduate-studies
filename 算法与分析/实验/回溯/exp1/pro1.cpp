#include<bits/stdc++.h>
using namespace std;

vector<int> q(20,0); 
int solves = 0;  

void queen(int i, int n)
{
	if(i < n+1){  
		for(int col=1; col<=n; col++){  
			bool flag = true;
			for(int j=1; j<i; j++){  
				if(col==q[j] || i+col==j+q[j] || i-col==j-q[j]){
					flag = false; 
					break;
				}	
			}
			
			if(flag){   
				q[i] = col;
				queen(i+1, n);
			}
		}
	}
	
	else{	
		solves++;
		if(solves <= 3){  
			for(int j=1; j<=n; j++){
				if(j == n){  
					cout << q[j];
					cout << endl;
				}	
				else
					cout << q[j] << " ";	
			}	
		}
		return ; 
	}

}

void Solve(){
	int n;
	cin >> n;
	queen(1, n);
	cout << solves << endl;
}

int main()
{
		Solve();
		return 0;
}

