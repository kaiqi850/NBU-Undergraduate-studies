#include <cassert>
#include <cstdio>
#include <stdexcept>
#include <string>

#include "huffman_encoder.h"

using namespace std;

int main(int argc, char** argv) {
    assert(argc >= 1);
    string filename = argv[1];  // 读取输入（也可在界面中拖动）
    zfish::HuffmanEncoder hec{filename};
    hec.run();
    getchar();

    return 0;
}

