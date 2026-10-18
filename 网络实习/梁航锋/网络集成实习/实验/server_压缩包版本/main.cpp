#include<stdio.h>
#include<io.h>
#include<bits/stdc++.h>

//用于网络编程的头文件和库文件
#include<winsock2.h> //头文件
#pragma comment(lib,"ws2_32.lib")//库文件
using namespace std;
//得到输出错误信息代码并返回错误码
void error_die(const char*str)
{
    printf("[hint]%s failed:%d",str,WSAGetLastError());
    exit(-1);
}

void initSocket();
void sendHtml(SOCKET clifd,const char* filePath);


void initSocket()
{
    WORD version=MAKEWORD(2,2);
    //传出参数
    WSADATA  wsadata;

    if( WSAStartup(version,&wsadata)!=0)
    {
       error_die("WSAStartup");
    }
}

SOCKET listenClient()
{
    /*创建socket*/
    //指定socket版本；
    //指定ip协议 ipv4 AF_NET/ipv6 AF_NET6
    //数据传输格式 流式（TCP）/数据报（UDP）
    //传输协议
    SOCKET serfd=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP);
    if(serfd==INVALID_SOCKET)
    {
        error_die("socket");
    }

    /*绑定ip和端口*/
    //指定的socket
    //ip地址和端口号
    //
    struct sockaddr_in serAddr;
    serAddr.sin_family=AF_INET;
    //计算机中是小端存储，而网络中是大端存储，因此此处不能简单写数字，而要转换成网络字节序
    serAddr.sin_port=htons(9999);
    serAddr.sin_addr.S_un.S_addr=INADDR_ANY;
    //serAddr.sin_addr.s_addr = ;//绑定本机任意ip地址
    if(SOCKET_ERROR==bind(serfd,(struct sockaddr*)&serAddr,sizeof(serAddr)))
    {
        error_die("bind");
    }

    //监听
    listen(serfd,10);
    return serfd;
}

void accept_request(SOCKET clifd)
{
    //从clifd接收数据
    char recvBuf[1024]="";
    //从socket中读取数据到recvBuf
    if(recv(clifd,recvBuf,sizeof(recvBuf),0)<=0)
    {
        error_die("recv offline");
    }
    printf("recvBuf:%s\n",recvBuf);

    //给客户端发送网页
    char filePath[128]="E:/大三下学期/网络集成/socket/server/test.html";
    //判断文件是否存在
    if(access(filePath,0)==0)//0:判断文件是否存在 如果存在，返回0；否则返回-1
    {
        //发送网页
        cout<<"YES"<<endl;
        sendHtml(clifd,filePath);
    }
    else
    {
        //发送404not found
        cout<<"NO"<<endl;
    }



}

//发送网页
void sendHtml(SOCKET clifd,const char* filePath)
{
    FILE*pr= fopen(filePath,"r");
    if(pr==NULL)
    {
        error_die("fopen");
        cout<<"fopen"<<endl;
    }
    char data[1024]="";
    do
    {
    fgets(data,1024,pr);
    send(clifd,data,strlen(data),0);
    }while(!feof(pr));

    fclose(pr);
}

int main()
{
    /*初始化网络库*/
    initSocket();

    SOCKET serfd=listenClient();


     printf("欢迎欢迎欢迎光临");
    //接收连接
    //后两个参数设置为null时，将不显示访问的信息
    struct sockaddr_in cliAddr;
    int len=sizeof(cliAddr);
    while(1)
    {

    SOCKET clifd=accept(serfd,(struct sockaddr*)&cliAddr,&len);
    if(clifd==INVALID_SOCKET)
    {
        error_die("accept");
    }
    printf("have a new connect...\n");
    char sendData[] = "HTTP/1.1 200 OK\r\nAccept-Ranges: bytes\r\n\
					 Content-Length: 1024\r\n\
					 Content-Type: textml;charset=UTF-8\r\n\
					 Connection: close\r\n\r\n";
	if (send(clifd, sendData, strlen(sendData), 0) == SOCKET_ERROR)
	{
		error_die("send");
	}


    //处理连接请求
    //给客户端发送相关消息
    accept_request(clifd);
    //sendHtml(clifd,"test.html");

    //发送完关闭连接
    closesocket(clifd);
    }

    closesocket(serfd);
    WSACleanup();


    return 0;
}
