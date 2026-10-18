#include <iostream>
#include <cmath>
#include <iomanip>

using namespace std;

double cal(double x, double rate) {
    double r = rate / 12.0; // 计算月利率
    double balance = 0.0; // 最后一个月结束时余额为0
    
    // 逆向递推计算第一个月初的存款
    for (int i = 0; i < 48; ++i) {
        balance = (balance + x) / (1 + r);
    }
    return balance;
}

int main() {
    double x, rate;
    cin >> x;
    cin >> rate;
    
    double initialDeposit = cal(x, rate);
    cout << fixed << setprecision(2)<< initialDeposit << endl;
    
    return 0;
}

#include <stdio.h>

int main()
{
    int x;       
    double rate; 

    scanf("%d %lf", &x, &rate);


    double monthRate = rate / 12.0;

    double money = x; 

   
    for (int i = 1; i < 48; i++)
    {

        money = (money + x) / (1 + monthRate);
    }

    printf("%.2f\n", money);

    return 0;
}

