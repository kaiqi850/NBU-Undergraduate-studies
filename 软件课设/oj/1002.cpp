#include <iostream>
#include <string>
using namespace std;

// 定义 FBI 树的节点结构体
struct FBINode {
    char type;
    FBINode* left;
    FBINode* right;
    FBINode(char t) : type(t), left(nullptr), right(nullptr) {}
};

// 构建 FBI 树的函数
FBINode* buildFBITree(const string& s) {
    if (s.size() == 1) {
        return new FBINode(s[0]);
    }
    int mid = s.size() / 2;
    FBINode* left = buildFBITree(s.substr(0, mid));
    FBINode* right = buildFBITree(s.substr(mid));
    char rootType;
    if ((left->type == '0' && right->type == '1') || (left->type == '1' && right->type == '0')) {
        rootType = 'F';
    } else if (left->type == '0' && right->type == '0') {
        rootType = 'B';
    } else {
        rootType = 'I';
    }
    FBINode* root = new FBINode(rootType);
    root->left = left;
    root->right = right;
    return root;
}

// 后序遍历函数
void postOrderTraversal(FBINode* root) {
    if (root == nullptr) {
        return;
    }
    postOrderTraversal(root->left);
    postOrderTraversal(root->right);
    cout << root->type;
}

// 统计各类节点数量的辅助函数
void countNodeTypes(FBINode* node, int* counts) {
    if (node == nullptr) {
        return;
    }
    if (node->type == 'B') {
        counts[0]++;
    } else if (node->type == 'I') {
        counts[1]++;
    } else {
        counts[2]++;
    }
    countNodeTypes(node->left, counts);
    countNodeTypes(node->right, counts);
}

int main() {
    int n;
    cin >> n;
    string s;
    cin >> s;
    FBINode* root = buildFBITree(s);
    postOrderTraversal(root);
    cout << endl;
    int counts[3] = {0, 0, 0};  // 分别存储 B、I、F 节点的数量，counts[0] 存储 B 节点数量，counts[1] 存储 I 节点数量，counts[2] 存储 F 节点数量
    countNodeTypes(root, counts);
    cout << "F 节点数量: " << counts[2] << ", B 节点数量: " << counts[0] << ", I 节点数量: " << counts[1] << endl;
    return 0;
}
