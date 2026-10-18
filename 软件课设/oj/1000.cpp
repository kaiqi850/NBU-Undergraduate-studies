#include <bits/stdc++.h>
using namespace std;

int precedence_func(char op){
    if(op == '+' || op == '-') return 1;
    if(op == '*' || op == '/') return 2;
    return 0;
}

int main(){
    string expr;
    cin >> expr;
    if(expr.empty() || expr[expr.size()-1] != '@'){
        cout << "NO"<<endl;
        return 0;
    }
    expr.erase(expr.size()-1, 1);
    string postfix = "";
    stack<char> s;
    bool expectOperand = true;
    for(int i=0;i<(int)expr.length();i++){
        char c = expr[i];
        if(c == ' ') continue;
        if(isdigit(c)){
            postfix += c;
            expectOperand = false;
        }
        else if(c == '('){
            s.push(c);
            expectOperand = true;
        }
        else if(c == ')'){
            bool found = false;
            while(!s.empty()){
                char top = s.top(); s.pop();
                if(top == '('){
                    found = true;
                    break;
                }
                postfix += top;
            }
            if(!found){
                cout << "NO"<<endl;
                return 0;
            }
            expectOperand = false;
        }
        else if(c == '+' || c == '-' || c == '*' || c == '/'){
            if(expectOperand){
                if(c == '-'){
                    postfix += '0';
                }
                else{
                    cout << "NO"<<endl;
                    return 0;
                }
            }
            while(!s.empty() && precedence_func(s.top()) >= precedence_func(c)){
                postfix += s.top(); s.pop();
            }
            s.push(c);
            expectOperand = true;
        }
        else{
            cout << "NO"<<endl;
            return 0;
        }
    }
    while(!s.empty()){
        char top = s.top(); s.pop();
        if(top == '(' || top == ')'){
            cout << "NO"<<endl;
            return 0;
        }
        postfix += top;
    }
    stack<int> eval;
    for(int i=0;i<(int)postfix.length();i++){
        char c = postfix[i];
        if(isdigit(c)){
            eval.push(c - '0');
        }
        else{
            if(eval.size() < 2){
                cout << "NO"<<endl;
                return 0;
            }
            int b = eval.top(); eval.pop();
            int a = eval.top(); eval.pop();
            int res = 0;
            if(c == '+') res = a + b;
            else if(c == '-') res = a - b;
            else if(c == '*') res = a * b;
            else if(c == '/'){
                if(b == 0){
                    cout << "NO"<<endl;
                    return 0;
                }
                res = a / b;
            }
            eval.push(res);
        }
    }
    if(eval.size() != 1){
        cout << "NO"<<endl;
        return 0;
    }
    cout << eval.top()<<endl;
}

