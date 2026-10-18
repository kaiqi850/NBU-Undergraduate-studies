#include <bits/stdc++.h>
using namespace std;


void solve(){
	string num,num1;	 
	int ans;			 
	int cnt=0;			
	while(cin>>num>>ans)
    {
        num1=num;
        cnt=0;
        int t;
        while(cnt<ans)	 
        {
            int flag=0;
            for(int i=0; i<num.size()-1; i++)	 
            {

                if(num[i]>num[i+1])				
                {
                    cnt++;
                    num.erase(i,1);
                    flag=1;
                    break;
                }
            }
            if(flag==0)			
            {
                cnt++; 
                num=num.erase(num.size()-1,1);
            }
        }
        int i = 0;
        for(int j=0; j<num1.size(); j++) 
        {
            if(i<num.size()&&num[i]==num1[j])
            {
                i++;
            }
            else
            {
                if(cnt==1)	 
                    cout<<num1[j]<<endl;
                else		
                    cout<<num1[j]<<" ",cnt--;
            }
        }
        int idx = 0;
		while (idx < num.size() - 1 && num[idx] == '0') idx++;
		cout << num.substr(idx) << endl;
    }
}

int main()
{
	solve();
	return 0;
}
