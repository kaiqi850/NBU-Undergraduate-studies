#include <iostream>
#include <vector>
using namespace std;

int main() {
    int n, k;
    cin >> n >> k;
    vector<int> a(k + 1);
    for (int i = 0; i <= k; i++) {
        cin >> a[i];
    }

    int count = 0;  
    int curgas = n;   
    
    for (int i = 0; i <= k; i++) {
        if (a[i] > n) {
            cout << "No Solution" << endl;
            return 0;
        }
        if (curgas >= a[i]) {
            curgas -= a[i];  
        } else {
            count++;       
            curgas = n - a[i];
        }
    }
    cout << count << endl;
    return 0;
}

