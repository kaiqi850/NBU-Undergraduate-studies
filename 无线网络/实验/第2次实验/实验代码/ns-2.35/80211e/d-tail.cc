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

// derived from drop-tail.cc

#include <cmu-trace.h>
#include "d-tail.h"
#include <iostream>
using namespace std;


static class DTailClass : public TclClass {
 public:
	DTailClass() : TclClass("Queue/DTail") {}
	TclObject* create(int, const char*const*) {
		return (new DTail);
	}
} class_d_tail;

void DTail::reset()
{
	Queue::reset();
}

int 
DTail::command(int argc, const char*const* argv) {

	if (argc==2) {
		if (strcmp(argv[1], "printstats") == 0) {
			print_summarystats();
			return (TCL_OK);
		}
	}
	if (argc == 3) {
		if (!strcmp(argv[1], "packetqueue-attach")) {
			delete q_;
			if (!(q_ = (PacketQueue*) TclObject::lookup(argv[2])))
				return (TCL_ERROR);
			else {
				pq_ = q_;
				return (TCL_OK);
			}
		}
	}
	return Queue::command(argc, argv);
}

/*
 * drop-tail
 */
void DTail::target_handle(NsObject* targ){
    target_ = targ;
}

void DTail::recv(Packet* p, Handler *h)
{
    Queue::recv(p,h);
}

void DTail::enque(Packet* p)
{
    	if (summarystats) {
                Queue::updateStats(qib_?q_->byteLength():q_->length());
	}
	int qlimBytes = qlim_ * mean_pktsize_;
	if ((!qib_ && (q_->length() + 1) >= qlim_) ||
  	(qib_ && (q_->byteLength() + hdr_cmn::access(p)->size()) >= qlimBytes)){
	    
            // if the queue would overflow if we added this packet...
		if (drop_front_) { /* remove from head of queue */
		        q_->enque(p);
			Packet *pp = q_->deque();
			drop(pp);
		} else {
		    drop(p);
		}
	} else {
	    q_->enque(p);
	}
}

Packet* DTail::deque()
{
        if (summarystats && &Scheduler::instance() != NULL) {
                Queue::updateStats(qib_?q_->byteLength():q_->length());
        }
	return q_->deque();
}

void DTail::print_summarystats()
{
	//double now = Scheduler::instance().clock();
        printf("True average queue: %5.3f", true_ave_);
        if (qib_)
                printf(" (in bytes)");
        printf(" time: %5.3f\n", total_time_);
}

void DTail::setPF(int pf){
    PF = pf;
}
void DTail::setCW_MIN(int cw_min){
    CW_MIN = cw_min;
}
void DTail::setCW_MAX(int cw_max){
    CW_MAX = cw_max;
}
void DTail::setAIFS(int aifs){
    AIFS = aifs;
}

void DTail::setTXOPLimit(double limit){
    LIMIT = limit;
}

int DTail::getPF(){
    return PF;
}
int DTail::getCW_MIN(){
    return CW_MIN;
}

int DTail::getCW_MAX(){
    return CW_MAX;
}
int DTail::getAIFS(){
    return AIFS;
}

double DTail::getTXOPLimit(){
    return LIMIT;
}

int DTail::getLen(){
    return Queue::length();
}

int DTail::getByteLen(){
    return Queue::byteLength();
}

void DTail::recvHighPri(Packet *p) {
    target_->recv(p, &qh_);
}

void DTail::setdrop(NsObject* getdrop_) {
    drop_ = getdrop_;
}

