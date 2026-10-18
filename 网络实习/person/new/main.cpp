// server.cpp
#include <winsock2.h>
#include <windows.h>
#include <iostream>
#include <string>
#include <sstream>
#include <vector>

#pragma comment(lib, "ws2_32.lib")

using namespace std;

// ====== 配置区 ======
#define LISTEN_PORT 9999
#define HTML_PATH   "C:/Users/asus/Desktop/x/试卷卷卷子/网络实习/person/new/index.html"
// ====================

// 全局运行标志
volatile bool g_running = true;

// 输出错误并退出
void error_die(const char* msg) {
    cerr << "[Error] " << msg << " failed: " << WSAGetLastError() << endl;
    WSACleanup();
    exit(EXIT_FAILURE);
}

// 初始化 WinSock
void initSocket() {
    WSADATA wsadata;
    if (WSAStartup(MAKEWORD(2,2), &wsadata) != 0) {
        error_die("WSAStartup");
    }
}

// 创建监听 socket
SOCKET setupListener(unsigned short port) {
    SOCKET serfd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (serfd == INVALID_SOCKET)
        error_die("socket");

    sockaddr_in addr;
    addr.sin_family      = AF_INET;
    addr.sin_port        = htons(port);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(serfd, (sockaddr*)&addr, sizeof(addr)) == SOCKET_ERROR)
        error_die("bind");

    if (listen(serfd, 10) == SOCKET_ERROR)
        error_die("listen");

    return serfd;
}

// 读取完整 HTTP 请求：
// 1) 循环 recv，直到读到 "\r\n\r\n"（请求头结束）
// 2) 如果有 Content-Length，则继续读取 body
string recvHttpRequest(SOCKET clifd) {
    const int BUF_SIZE = 4096;
    vector<char> buffer;
    buffer.reserve(BUF_SIZE);

    // 1. 读取头部
    while (true) {
        char tmp[BUF_SIZE];
        int len = recv(clifd, tmp, BUF_SIZE, 0);
        if (len <= 0) break;
        buffer.insert(buffer.end(), tmp, tmp + len);
        string sofar(buffer.begin(), buffer.end());
        // 请求头结束标志
        size_t pos = sofar.find("\r\n\r\n");
        if (pos != string::npos) {
            // 如果有 body，根据 Content-Length 再读
            size_t header_end = pos + 4;
            // 查找 Content-Length
            size_t cl_pos = sofar.find("Content-Length:");
            if (cl_pos != string::npos) {
                cl_pos += strlen("Content-Length:");
                // 取数字
                int content_length = stoi(sofar.substr(cl_pos));
                int already = (int)buffer.size() - (int)header_end;
                int to_read = content_length - already;
                while (to_read > 0) {
                    int r = recv(clifd, tmp, min(BUF_SIZE, to_read), 0);
                    if (r <= 0) break;
                    buffer.insert(buffer.end(), tmp, tmp + r);
                    to_read -= r;
                }
            }
            break;
        }
    }
    return string(buffer.begin(), buffer.end());
}

// 发送静态 HTML 文件
void sendHtml(SOCKET clifd, const char* filePath) {
    FILE* fp = fopen(filePath, "r");
    if (!fp) {
        const char* resp500 =
            "HTTP/1.1 500 Internal Server Error\r\n"
            "Content-Type: text/plain; charset=UTF-8\r\n"
            "Connection: close\r\n\r\n"
            "500 Internal Server Error: cannot open file.";
        send(clifd, resp500, (int)strlen(resp500), 0);
        return;
    }
    // 发送头部
    const char* header =
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        "Connection: close\r\n\r\n";
    send(clifd, header, (int)strlen(header), 0);

    // 发送文件内容
    char buf[1024];
    while (fgets(buf, sizeof(buf), fp)) {
        send(clifd, buf, (int)strlen(buf), 0);
    }
    fclose(fp);
}

int main() {
    initSocket();
    SOCKET serfd = setupListener(LISTEN_PORT);
    cout << "服务器已启动，监听端口 " << LISTEN_PORT << endl;

    while (g_running) {
        sockaddr_in cliAddr;
        int addrLen = sizeof(cliAddr);
        SOCKET clifd = accept(serfd, (sockaddr*)&cliAddr, &addrLen);
        if (clifd == INVALID_SOCKET) {
            if (WSAGetLastError() == WSAEINTR) break;
            continue;
        }

        // 1. 接收并打印完整请求
        string request = recvHttpRequest(clifd);
        cout << "=== Full HTTP Request ===\n"
             << request
             << "\n=== End ===\n";

        // 2. 解析请求行
        istringstream reqstream(request);
        string method, path, version;
        reqstream >> method >> path >> version;
        cout << "[Parsed] Method=" << method
             << "  Path=" << path
             << "  Version=" << version << "\n";

        // 3. 路由处理
        if (method == "POST" && path == "/shutdown") {
            const char* resp =
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain; charset=UTF-8\r\n"
                "Connection: close\r\n\r\n"
                "服务器正在关闭...";
            send(clifd, resp, (int)strlen(resp), 0);
            g_running = false;
        }
        else if ((method == "GET"  || method == "POST" ||
                  method == "PUT"  || method == "DELETE")
                 && (path == "/" || path == "/index.html"))
        {
            // 针对 PUT/DELETE 也返回相同 HTML
            cout << "[Info] " << method << " " << path << " -> send index.html\n";
            sendHtml(clifd, HTML_PATH);
        }
        else {
            const char* resp404 =
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/plain; charset=UTF-8\r\n"
                "Connection: close\r\n\r\n"
                "404 Not Found";
            send(clifd, resp404, (int)strlen(resp404), 0);
        }

        closesocket(clifd);
    }

    // 清理
    closesocket(serfd);
    WSACleanup();
    cout << "服务器已关闭，程序退出。" << endl;
    return 0;
}

