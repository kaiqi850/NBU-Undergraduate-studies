#include <bits/stdc++.h>
using namespace std;

int m, n;
bool used[505] = {false}; 

class game {
public:
    int time;
    int mon;
};

bool compare(game g1, game g2) {
    return g1.mon > g2.mon;
}

int main() {
    cin >> m >> n;
    game g[n];
    for (int i = 0; i < n; i++) {
        cin >> g[i].time;
    }
    for (int i = 0; i < n; i++) {
        cin >> g[i].mon;
    }

    sort(g, g + n, compare);

    int total = 0;

    for (int i = 0; i < n; i++) {
        bool scheduled = false;  
        for (int t = g[i].time; t >= 1; t--) {
            if (!used[t]) {
                used[t] = true;
                scheduled = true;
                break;  
            }
        }

        if (!scheduled) {
            total += g[i].mon;  
        }
    }

    cout << m - total << endl;
    return 0;
}

