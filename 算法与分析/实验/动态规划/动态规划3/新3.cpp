#include <bits/stdc++.h> 
using namespace std;

int main() {
    string s;
    getline(cin,s);
    int n = s.size();
    int maxLen = 1; 

    for (int i = 0; i < n; i++) {
        int left = i, right = i;
        while(left >= 0 && right < n && s[left] == s[right]) {
            int len = right - left + 1;
            if (len > maxLen) maxLen = len;
            left--;
            right++;
        }
        
        left = i, right = i + 1;
        while(left >= 0 && right < n && s[left] == s[right]) {
            int len = right - left + 1;
            if (len > maxLen) maxLen = len;
            left--;
            right++;
        }
    }
    
    cout << maxLen;
    return 0;
}
