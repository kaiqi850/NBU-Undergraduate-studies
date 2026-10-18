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

#include <object.h>
#include <queue.h>
#include <packet.h>
#include <cmu-trace.h>
//#include <iostream.h>
#include "priq.h"
#include "mac-802_11e.h"

typedef int (*PacketFilter)(Packet *, void *);

PriQ_List PriQ::prhead = { 0 };

static class PriQClass : public TclClass {
public:
  PriQClass() : TclClass("Queue/DTail/PriQ") {}
  TclObject* create(int, const char*const*) {
    return (new PriQ);
  }
} class_PriQ;


PriQ::PriQ() : DTail()
{
        bind("Prefer_Routing_Protocols", &Prefer_Routing_Protocols);
	bind("Max_Levels", &max_levels);
	bind("Levels", &levels);
	LIST_INSERT_HEAD(&prhead, this, link);
	flag = 0;
	cntl = 0;
	level = 0;
}

int
PriQ::command(int argc, const char*const* argv)
{
    Scheduler &s = Scheduler::instance();
    if (argc == 5 )
    { 
	if(strcmp(argv[1], "Prio") == 0){
	    if(!(atoi(argv[2]) > levels)){
		level = atoi(argv[2]);
		if(strcmp(argv[3], "PF") == 0){
		    pri_[level].setPF(atoi(argv[4]));
		    return(TCL_OK);
		}
		if(strcmp(argv[3], "CW_MIN") == 0){
		    pri_[level].setCW_MIN(atoi(argv[4]));
		    return(TCL_OK);
		}
		if(strcmp(argv[3], "CW_MAX") == 0){
		    pri_[level].setCW_MAX(atoi(argv[4]));
		    return(TCL_OK);
		}
		if(strcmp(argv[3], "AIFS") == 0){
		    pri_[level].setAIFS(atoi(argv[4])); 
		    return(TCL_OK);	      
		}
		if(strcmp(argv[3], "TXOPLimit") == 0){
		    pri_[level].setTXOPLimit(atof(argv[4])); 
		    return(TCL_OK);	      
		}
	    }else return (TCL_ERROR);
	}
    }
    if (argc == 2 && strcasecmp(argv[1], "reset") == 0)
    {
	Terminate();
	//FALL-THROUGH to give parents a chance to reset
    }

    return DTail::command(argc, argv);
}

void
PriQ::recv(Packet *p, Handler *h)
{
    if(flag == 0) {
	((Mac802_11e*) target())->queue_ = this;
	flag = 1;
	for(int i = 0; i < MAX_PRI; i++) {
	    pri_[i].setdrop(drop_);    
	}
    }
    
    struct hdr_cmn *ch = HDR_CMN(p);
    if(Prefer_Routing_Protocols) {

                switch(ch->ptype()) {
                case PT_DSR:
                case PT_MESSAGE:
                case PT_TORA:
                case PT_AODV:
                        recvHighPriority(p, h);
                        break;

                default:
		    pri_recv(p, h);
                }
        }
        else {
	    pri_recv(p, h);
        }
}

void
PriQ::pri_recv(Packet *p, Handler *h)
{
    Scheduler &s = Scheduler::instance();
    level = PKT_LEVEL(p); 
    struct hdr_cmn *ch = HDR_CMN(p);
    /*  target_handle() is necessary to give the target to class Queue.  
     *  Otherwise the target is not known in class Queue 
     *  when dequeing packet :o(
     */
    pri_[level].target_handle(target_);
    pri_[level].recv(p,h);
}    


void 
PriQ::recvHighPriority(Packet *p, Handler *)
  // insert packet at front of queue
{
    pri_[cntl].q_->enqueHead(p);
    pri_[cntl].target_handle(target_);
    if (pri_[cntl].q_->length() >= qlim_)
    {
      Packet *to_drop = pri_[cntl].q_->lookup(pri_[cntl].q_->length()-1);
      pri_[cntl].q_->remove(to_drop);
      drop(to_drop);
    }
  if (!pri_[cntl].blocked()) {
    /*
     * We're not blocked.  Get a packet and send it on.
     * We perform an extra check because the queue
     * might drop the packet even if it was
     * previously empty!  (e.g., RED can do this.)
     */
  

p = pri_[cntl].deque();
    if (p != 0) {
      pri_[cntl].block();
      pri_[cntl].recvHighPri(p);
      //target_->recv(p, &qh_); <- done in d-tail.cc
    }
  } 
}
 
void 
PriQ::filter(PacketFilter filter, void * data)
  // apply filter to each packet in queue, 
  // - if filter returns 0 leave packet in queue
  // - if filter returns 1 remove packet from queue
{
    int i = 0;
    while (i < pri_[cntl].q_->length())
    {
      Packet *p = pri_[cntl].q_->lookup(i);
      if (filter(p,data))
	{
	  pri_[cntl].q_->remove(p); // decrements q len
	}
      else i++;
    }
}

Packet*
PriQ::filter(nsaddr_t id)
{
    Packet *p = 0;
    Packet *pp = 0;
    struct hdr_cmn *ch;
    
    for(p = pri_[cntl].q_->head(); p; p = p->next_) {
	ch = HDR_CMN(p);
	if(ch->next_hop() == id)
	    break;
	pp = p;
    }

	/*
	 * Deque Packet
	 */
     if(p) {
	if(pp == 0)
	    pri_[cntl].q_->remove(p);
	else
	    pri_[cntl].q_->remove(p, pp);
    }
    return p;
}



/*
 * Called at the end of the simulation to purge the IFQ.
 */
void
PriQ::Terminate()
{
    for(int i = 0; i< MAX_PRI; i++){
	Packet *p;
	while((p = pri_[i].deque())) {
	    drop(p, DROP_END_OF_SIMULATION);
	    //drop(p);
		
	}
    }
}

int PriQ::getLevels(){
    return levels;
}




