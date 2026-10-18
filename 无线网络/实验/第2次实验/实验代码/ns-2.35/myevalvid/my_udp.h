#ifndef ns_my_udp_h
#define ns_my_udp_h

#include "udp.h"

class my_UdpAgent : public UdpAgent {
public:
	my_UdpAgent();
	virtual void sendmsg(int nbytes, AppData* data, const char *flags = 0);
	virtual int command(int argc, const char*const* argv);
protected:
	//added by smallko
	int id_;	
	char BWfile[100];
	FILE *BWFile;
	int openfile;
	
	nsaddr_t index_;                  // IP Address of this node
};

#endif
