//* -*-	Mode:C++; c-basic-offset:8; tab-width:8; indent-tabs-mode:t -*- */
/*
 * Copyright (c) 1997 Regents of the University of California.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. All advertising materials mentioning features or use of this software
 *    must display the following acknowledgement:
 *	This product includes software developed by the Computer Systems
 *	Engineering Group at Lawrence Berkeley Laboratory.
 * 4. Neither the name of the University nor of the Laboratory may be used
 *    to endorse or promote products derived from this software without
 *    specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 */

#ifndef ns_d_tail_h
#define ns_d_tail_h

#include <string.h>
#include "queue.h"
#include "config.h"

/*
 * A bounded, drop-tail queue
 */
class DTail : public Queue {
  public:
	DTail() { 
		
	    q_ = new PacketQueue; 
	    pq_ = q_;
	    bind_bool("drop_front_", &drop_front_);
	    bind_bool("summarystats_", &summarystats);
	    bind_bool("queue_in_bytes_", &qib_);  // boolean: q in bytes?
	    bind("mean_pktsize_", &mean_pktsize_);
	    //		_RENAMED("drop-front_", "drop_front_");
	    //parameter for backoff instance
	    PF = 0;
	    CW_MIN = 0;
	    CW_MAX = 0;
	    AIFS = 0;
	}
	
	
	void target_handle(NsObject* targ);
	void recv(Packet* p, Handler* h);
	~DTail() {
	    delete q_;
	}
	void   setPF(int pf);
	void   setCW_MIN(int cw_min);
	void   setCW_MAX(int cw_max);
	void   setAIFS(int aifs);
	void   setTXOPLimit(double limit);
	int    getPF();
	int    getCW_MIN();
	int    getCW_MAX();
	int    getAIFS();
	double getTXOPLimit();
        int    getLen();
	int    getByteLen();
	void   recvHighPri(Packet* p);
	PacketQueue *q_;	/* underlying FIFO queue */
	Packet* deque();	
	void enque(Packet* p);
	void setdrop(NsObject* getdrop_);
	//Connector* pricon;
	//NsObject* qdrop_;
protected:
	void   reset();
	int    command(int argc, const char*const* argv); 
	int    drop_front_;	/* drop-from-front (rather than from tail) */
	int    summarystats;
	void   print_summarystats();
	int    qib_;       	/* bool: queue measured in bytes? */
	int    mean_pktsize_;	/* configured mean packet size in bytes */
	int    PF;
	int    CW_MIN;
	int    CW_MAX;
	int    AIFS;
	double LIMIT;
};

#endif
