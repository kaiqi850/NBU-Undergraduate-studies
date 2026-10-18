#include <bits/stdc++.h>
using namespace std;

class people {
public:
    int id;
    int time;
};

bool compare(const people& p1, const people& p2) {
    return p1.time < p2.time;  
}

int main() {
    int n;
    while (cin >> n) {
        long sum = 0;
        int wait = 0;
        vector<people> a(n);  
        for (int i = 0; i < n; i++) {
            cin >> a[i].time;
            a[i].id = i + 1;
        }
        sort(a.begin(), a.end(), compare);  
        for (int i = 0; i < n; i++) {
            sum += wait;
            wait += a[i].time;
            cout << a[i].id << " ";
        }
		cout<<endl;
        printf("%.2f\n",1.0*sum/n);	
    }
}

