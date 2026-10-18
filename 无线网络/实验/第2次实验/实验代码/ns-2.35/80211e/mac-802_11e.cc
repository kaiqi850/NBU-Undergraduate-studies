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
#undef NDEBUG
#include <assert.h>
#include "delay.h"
#include "connector.h"
#include "packet.h"
#include "random.h"
#include "mobilenode.h"
#include <iostream>
using namespace std;

#include "arp.h"
//#include "ll.h"
//#include "mac.h"
#include "mac-timers_802_11e.h"
#include "mac-802_11e.h"
#include "cmu-trace.h"
#include "priq.h"

//include the following line when using Akaroa
//#include "akaroa.H"
#define AKAROA 0 
#define AK_INTERVAL 0.01 

inline void
Mac802_11e::set_rx_state(MacState x)
{
	rx_state_ = x;
	check_backoff_timer();
}

inline void
Mac802_11e::set_tx_state(int pri, MacState x)
{
	tx_state_[pri] = x;
}

inline void
Mac802_11e::transmit(Packet *p, double t)
{                                                                       
	/*                                                              
         * If I'm transmitting without doing CS, such as when           
         * sending an ACK, any incoming packet will be "missed"         
         * and hence, must be discarded.                                
         */                                                             
         if(rx_state_ != MAC_IDLE) {                                     
                struct hdr_mac802_11e *dh = HDR_MAC802_11E(p);            
                                                                        
                assert(dh->dh_fc.fc_type == MAC_Type_Control);          
                assert(dh->dh_fc.fc_subtype == MAC_Subtype_ACK);        
                                                                        
                assert(pktRx_);                                         
                struct hdr_cmn *ch = HDR_CMN(pktRx_);                   
                                                                        
                ch->error() = 1;        /* force packet discard */      
        }                                                               
                                                                        
        /*                                                              
         * pass the packet on the "interface" which will in turn        
         * place the packet on the channel.                             
         *                                                              
         * NOTE: a handler is passed along so that the Network          
         *       Interface can distinguish between incoming and         
         *       outgoing packets.                                      
         */
	struct hdr_cmn *sd = HDR_CMN(p);
	int prio = LEVEL(p);
	tx_active_ = 1;
	sending = 1;
	check_backoff_timer();

	downtarget_->recv(p->copy(), this);
	if(sd->ptype() == PT_CBR || sd->ptype() == PT_EXP) {
	  if(!rtx_[prio]){
	    numbytes_[prio] += sd->size() - phymib_.getHdrLen11();
	  }
	} 
	mhIF_.start(txtime(p));  
	mhSend_.start(t);                      

	                                       
} 

void 
Mac802_11e::check_backoff_timer()
{
	if(is_idle() && mhBackoff_.paused()) {
            mhBackoff_.resume();
	}                                   
	if(! is_idle() && mhBackoff_.busy() && ! mhBackoff_.paused()){  
		mhBackoff_.pause();				       
        }                            
 if(!is_idle() && mhDefer_.busy()) mhDefer_.stop();
}

/* ======================================================================
   Global Variables
   ====================================================================== */

EDCA_PHY_MIB::EDCA_PHY_MIB(Mac802_11e *parent)
{
  /*
   * Bind the phy mib objects.  Note that these will be bound
   * to Mac/802_11e variables
   */
  parent->bind("SlotTime_", &SlotTime);
  parent->bind("SIFS_", &SIFSTime);
  parent->bind("PreambleLength_", &PreambleLength);
  parent->bind("PLCPHeaderLength_", &PLCPHeaderLength);
  parent->bind_bw("PLCPDataRate_", &PLCPDataRate);
}

EDCA_MAC_MIB::EDCA_MAC_MIB(Mac802_11e *parent)
{
  /*
   * Bind the phy mib objects.  Note that these will be bound
   * to Mac/802_11 variables
   */
  
  parent->bind("RTSThreshold_", &RTSThreshold);
  parent->bind("ShortRetryLimit_", &ShortRetryLimit);
  parent->bind("LongRetryLimit_", &LongRetryLimit);
}

/* ======================================================================
   TCL Hooks for the simulator
   ====================================================================== */
static class Mac802_11eClass : public TclClass {
public:
	Mac802_11eClass() : TclClass("Mac/802_11e") {}
	TclObject* create(int, const char*const*) {
		return (new Mac802_11e());
	}
} class_mac802_11e;


/* ======================================================================
   Mac Class Functions
   ====================================================================== */
Mac802_11e::Mac802_11e() : 
  Mac(), phymib_(this), macmib_(this), mhIF_(this), mhNav_(this), mhRecv_(this), mhSend_(this), mhDefer_(this, phymib_.getSlotTime()), mhSifs_(this, phymib_.getSlotTime()), mhBackoff_(this, phymib_.getSlotTime()), AK(this)
{
        // Pointer to PriQ, Cast in priq.cc
	queue_  = 0;
	
	//flags to control if PriQ Parameters have already been adopted
	AIFSset = 0;
	CWset   = 0;
	for(int i=0; i < MAX_PRI; i++){
	    packets_[i] = 0;
	    pktRTS_[i] = 0;
	    pktCTRL_[i] = 0;
	    pktTx_[i] = 0;
	    tx_state_[i] = MAC_IDLE;
	    ssrc_[i] = slrc_[i] = 0;
	    callback_[i] = 0;
	    numbytes_[i] = 0;
	    rtx_[i] = 0;
	    cw_[i] = 0;
	    cwmin_[i] = 0;
	    cwmax_[i] = 0;
	    aifs_[i] = 0;
	    txop_limit_[i] = 0;
	    start_handle_[i] = 0;
	} 
        jitter  =    1000;
	//jitter =   0;
	throughput = 0;
	interval_ =  AK_INTERVAL;
        if(AKAROA) AK.start();
		
	nav_ =       0.0;
	
	rx_state_ =  MAC_IDLE;
	tx_active_ = 0;    
      	
	idle_time =     0;
	sending =       0;
	cfb_dur =       0;
	cfb_active =    0;
        cfb_broadcast = 0;
	
	levels =     0;
	slotnum =    0;
	pf =         0;
	cw_old =     0;

	sifs_ = phymib_.getSIFS();
	pifs_ = phymib_.getPIFS();
	difs_ = phymib_.getDIFS();
		
        // see (802.11-1999, 9.2.10) 
	eifs_ = phymib_.getDIFS();
	
	eifs_nav_ =  0;
	
	sta_seqno_ =        1;
	cache_ =            0;
	cache_node_count_ = 0;
	
        // chk if basic/data rates are set
	// otherwise use bandwidth_ as default;
	
	Tcl& tcl = Tcl::instance();
	tcl.evalf("Mac/802_11e set basicRate_");
	if (strcmp(tcl.result(), "0") != 0) 
		bind_bw("basicRate_", &basicRate_);
	else
	    basicRate_ = bandwidth_;

	tcl.evalf("Mac/802_11e set dataRate_");
	if (strcmp(tcl.result(), "0") != 0) 
	  bind_bw("dataRate_", &dataRate_);
	else
	  dataRate_ = bandwidth_;
	
	bind("cfb_", &cfb_);
}


int
Mac802_11e::command(int argc, const char*const* argv)
{
	if (argc == 3) {
	    if (strcmp(argv[1], "log-target") == 0) {
		logtarget_ = (NsObject*) TclObject::lookup(argv[2]);
		if(logtarget_ == 0)
		    return TCL_ERROR;
		return TCL_OK;
	    } else if(strcmp(argv[1], "nodes") == 0) {
		if(cache_) return TCL_ERROR;
		cache_node_count_ = atoi(argv[2]);
		cache_ = new Host[cache_node_count_ + 1];
		assert(cache_);
		bzero(cache_, sizeof(Host) * (cache_node_count_+1 ));
		return TCL_OK;
	    }
	}
	return Mac::command(argc, argv);
}

/* ======================================================================
   Debugging Routines
   ====================================================================== */

/*
 * dump and packet trace are not adopted to 802.11e yet!
 */

void
Mac802_11e::trace_pkt(Packet *p) {
	struct hdr_cmn *ch = HDR_CMN(p);
	struct hdr_mac802_11e* dh = HDR_MAC802_11E(p);
	u_int16_t *t = (u_int16_t*) &dh->dh_fc;

	fprintf(stderr, "\t[ %2x %2x %2x %2x ] %x %s %d\n",
		*t, dh->dh_duration,
		ETHER_ADDR(dh->dh_da), ETHER_ADDR(dh->dh_sa),
		index_, packet_info.name(ch->ptype()), ch->size());
}

void
Mac802_11e::dump(char *fname)
{
	fprintf(stderr,
		"\n%s --- (INDEX: %d, time: %2.9f)\n",
		fname, index_, Scheduler::instance().clock());

	fprintf(stderr,
		"\ttx_state_: %x, rx_state_: %x, nav: %2.9f, idle: %d\n",
		tx_state_, rx_state_, nav_, is_idle());

	//fprintf(stderr,
	//	"\tpktTx_: %x, pktRx_: %x, pktRTS_: %x, pktCTRL_: %x, callback: %x\n",
	//	(int) pktTx_, (int) pktRx_, (int) pktRTS_,
	//	(int) pktCTRL_, (int) callback_);

	fprintf(stderr,
		"\tDefer: %d, Backoff: %d (%d), Recv: %d, Timer: %d Nav: %d\n",
		mhDefer_.busy(), mhBackoff_.busy(), mhBackoff_.paused(),
		mhRecv_.busy(), mhSend_.busy(), mhNav_.busy());
	fprintf(stderr,
		"\tBackoff Expire: %f\n",
		mhBackoff_.expire());
}


/* ======================================================================
   Packet Headers Routines
   ====================================================================== */
inline int
Mac802_11e::hdr_dst(char* hdr, int dst )
{
	struct hdr_mac802_11e *dh = (struct hdr_mac802_11e*) hdr;
	//dst = (u_int32_t)(dst);

	if(dst > -2)
		STORE4BYTE(&dst, (dh->dh_da));

	return ETHER_ADDR(dh->dh_da);
}

inline int 
Mac802_11e::hdr_src(char* hdr, int src )
{
	struct hdr_mac802_11e *dh = (struct hdr_mac802_11e*) hdr;
	if(src > -2)
		STORE4BYTE(&src, (dh->dh_sa));
	return ETHER_ADDR(dh->dh_sa);
}

inline int 
Mac802_11e::hdr_type(char* hdr, u_int16_t type)
{
	struct hdr_mac802_11e *dh = (struct hdr_mac802_11e*) hdr;
	if(type)
		STORE2BYTE(&type,(dh->dh_body));
	return GET2BYTE(dh->dh_body);
}


/* ======================================================================
   Misc Routines
   ====================================================================== */
inline int
Mac802_11e::is_idle()
{
    if(rx_state_ != MAC_IDLE){
      idle_time = 0;
      return 0;
    }
    if(sending) {
      idle_time = 0;
      return 0;
    }
    
    if(nav_ > Scheduler::instance().clock()){
      idle_time = 0;
      return 0;
    }
    idle_time = Scheduler::instance().clock();
    return 1;
}

void
Mac802_11e::discard(Packet *p, const char* why)
{
	hdr_mac802_11e* mh = HDR_MAC802_11E(p);
	hdr_cmn *ch = HDR_CMN(p);

#if 0
	/* old logic 8/8/98 -dam */
	/*
	 * If received below the RXThreshold, then just free.
	 */
	if(p->txinfo_.Pr < p->txinfo_.ant.RXThresh) {
		Packet::free(p);
		//p = 0;
		return;
	}
#endif // 0

	/* if the rcvd pkt contains errors, a real MAC layer couldn't
	   necessarily read any data from it, so we just toss it now */
	if(ch->error() != 0) {
		Packet::free(p);
		//p = 0;
		return;
	}

	switch(mh->dh_fc.fc_type) {
	case MAC_Type_Management:
		drop(p, why);
		return;
	case MAC_Type_Control:
		switch(mh->dh_fc.fc_subtype) {
		case MAC_Subtype_RTS:
			if((u_int32_t)ETHER_ADDR(mh->dh_sa) == \
			   (u_int32_t)index_) {
				drop(p, why);
				return;
			}
			/* fall through - if necessary */
		case MAC_Subtype_CTS:
		case MAC_Subtype_ACK:
			if((u_int32_t)ETHER_ADDR(mh->dh_da) == \
			   (u_int32_t)index_) {
				drop(p, why);
				return;
			}
			break;
		default:
			fprintf(stderr, "invalid MAC Control subtype\n");
			exit(1);
		}
		break;
	case MAC_Type_Data:
		switch(mh->dh_fc.fc_subtype) {
		case MAC_Subtype_Data:
			if((u_int32_t)ETHER_ADDR(mh->dh_da) == \
			   (u_int32_t)index_ ||
			   (u_int32_t)ETHER_ADDR(mh->dh_sa) == \
			   (u_int32_t)index_ ||
			   (u_int32_t)ETHER_ADDR(mh->dh_da) == MAC_BROADCAST) {
				drop(p, why);
				return;
			}
			break;
		default:
			fprintf(stderr, "invalid MAC Data subtype\n");
			exit(1);
		}
		break;
	default:
		fprintf(stderr, "invalid MAC type (%x)\n", mh->dh_fc.fc_type);
		trace_pkt(p);
		exit(1);
	}
	Packet::free(p);
}

void
Mac802_11e::capture(Packet *p)
{
	/*
	 * Update the NAV so that this does not screw
	 * up carrier sense.
	 */
    	set_nav(usec(eifs_ + txtime(p)));
		      Packet::free(p);
}

void
Mac802_11e::collision(Packet *p)
{
	switch(rx_state_) {
	case MAC_RECV:
		set_rx_state(MAC_COLL);
		/* fall through */
	case MAC_COLL:
		assert(pktRx_);
		assert(mhRecv_.busy());
		/*
		 *  Since a collision has occurred, figure out
		 *  which packet that caused the collision will
		 *  "last" the longest.  Make this packet,
		 *  pktRx_ and reset the Recv Timer if necessary.
		 */
		if(txtime(p) > mhRecv_.expire()) {
			mhRecv_.stop();
			discard(pktRx_, DROP_MAC_COLLISION);
			pktRx_ = p;
			mhRecv_.start(txtime(pktRx_));
		}
		else {
			discard(p, DROP_MAC_COLLISION);
		}
		break;
	default:
		assert(0);
	}
}

void
Mac802_11e::tx_resume()
{
	double rTime;
	assert(mhSend_.busy() == 0);
	
	for(int pri = 0; pri < MAX_PRI; pri++){
	    //assert(mhDefer_.defer(pri) == 0);
	    if(!mhDefer_.defer(pri)) {
		if(pktCTRL_[pri]) {
		/*
		 *  Need to send a CTS or ACK.
		 */
		    mhSifs_.start(pri, sifs_);
		} else if(pktRTS_[pri]) {
		    if(mhBackoff_.backoff(pri) == 0) {
		      rTime = (Random::random() % getCW(LEVEL(pktRTS_[pri]))) * phymib_.getSlotTime();
		      mhDefer_.start(pri, getAIFS(LEVEL(pktRTS_[pri]))); 
		    }
		} else if(pktTx_[pri]) {
		    if(mhBackoff_.backoff(pri) == 0) {
			hdr_cmn *ch = HDR_CMN(pktTx_[pri]);
			struct hdr_mac802_11e *mh = HDR_MAC802_11E(pktTx_[pri]);
			
			if ((u_int32_t) ch->size() < macmib_.RTSThreshold ||
			    (u_int32_t) ETHER_ADDR(mh->dh_da) == MAC_BROADCAST) {
			  
			  if((u_int32_t) ETHER_ADDR(mh->dh_da) == MAC_BROADCAST) rTime = (Random::random() % (getCW(pri) + 1)) * phymib_.getSlotTime();
			  else rTime = 0;
			    mhDefer_.start(pri, getAIFS(pri) + rTime);
			} else {
			    mhSifs_.start(pri, sifs_); 
			}
		    }
		} else if(callback_[pri] != 0) {
		  rtx_[pri] = 0;
		  Handler *h = callback_[pri];
		  callback_[pri] = 0;
		  h->handle((Event*) 0);
		}
		set_tx_state(pri, MAC_IDLE);
	    }
	}
}

void
Mac802_11e::rx_resume()
{
  assert(pktRx_ == 0);
    assert(mhRecv_.busy() == 0);
    set_rx_state(MAC_IDLE);
}


/* ======================================================================
   Timer Handler Routines
   ====================================================================== */
void
Mac802_11e::backoffHandler(int pri)
{
   if(pktCTRL_[pri]) {
    assert(mhSend_.busy() || mhDefer_.defer(pri));
    return;
  }
  
  if(check_pktRTS(pri) == 0)
    return;
  
  if(check_pktTx(pri) == 0)
    return;
}

void
Mac802_11e::deferHandler(int pri)
{
	assert(pktCTRL_[pri] || pktRTS_[pri] || pktTx_[pri]);

	if(check_pktCTRL(pri) == 0)
		return;

	assert(mhBackoff_.backoff(pri) == 0);
	//if (mhBackoff_.busy() != 0)
	//{
	//	printf("deferHandler:mhBackoff_ busy!\n");
	//	return;
	//}
	if(check_pktRTS(pri) == 0)
		return;

	if(check_pktTx(pri) == 0)
		return;
}

void
Mac802_11e::navHandler()
{
    eifs_nav_ = 0.0;
    if(is_idle() && mhBackoff_.paused()) {
		mhBackoff_.resume();
    }
}

void
Mac802_11e::recvHandler()
{
    
	recv_timer();
}

void
Mac802_11e::sendHandler()
{
    Scheduler &s = Scheduler::instance();
    sending = 0;
    check_backoff_timer();
    send_timer();
}


void
Mac802_11e::txHandler()
{
    tx_active_ = 0;
    if(cfb_ && !cfb_broadcast) cfb_active = 0;
    if(cfb_broadcast) cfb_broadcast = 0;
}

void
Mac802_11e::defer_stop(int pri)
{
   mhBackoff_.start(pri, getCW(pri), is_idle());
}

/* sends the throughput every AK_INTERVAL to Akaroa 
 * via AkObservation. This works only if you have 
 * installed Akaroa and the ns-2/Akaroa interface.
 */
void
Mac802_11e::calc_throughput()
{
#if AKAROA > 0
  if(AKAROA){	
    if(index_ > 0){
      //int pri = 2; 
      // jitter is for cases in which the simulation is
      // already in a steady state at the very beginning
      if (jitter >0) {if(jitter >= 10 ) jitter -= 10; }
      for(int pri = 0; pri < 3; pri++){
	if(jitter > 0){
	  throughput = ((numbytes_[pri] * 8.) / interval_) + Random::uniform(0,jitter);
	}else {
	  throughput = (8. * numbytes_[pri]) / interval_;
	}
	if(throughput <= 0) throughput = 0.0001;
	AkObservation((3 * (index_ - 1)) + (pri + 1), throughput);
	//AkObservation((6 * (index_ - 1)) + (pri + 1), throughput);
	//AkObservation((pri + 1), throughput);
	//AkObservation(1, throughput);
	//if(index_ == 1 && pri == 0) {
	cout.precision(16);
	//cout<<"Mac "<<index_<<", now: "<<Scheduler::instance().clock()<<", priority "<<pri<<", throughput: "<<throughput<<", interval_: "<<interval_<<" numbytes " << numbytes_[pri] <<"  jitter "<<jitter<<"\n";
	//}
	numbytes_[pri] = 0; throughput = 0;
      }
      AK.start();
    } 
  }
#endif
}

/* ======================================================================
   The "real" Timer Handler Routines
   ====================================================================== */
void
Mac802_11e::send_timer()
{   
 Scheduler &s = Scheduler::instance();
    for(int pri = 0; pri < MAX_PRI; pri ++){
	switch(tx_state_[pri]) {
	/*
	 * Sent a RTS, but did not receive a CTS.
	 */
	case MAC_RTS:
		RetransmitRTS(pri);
		break;
	/*
	 * Sent a CTS, but did not receive a DATA packet.
	 */
	case MAC_CTS:
		assert(pktCTRL_[pri]);
		Packet::free(pktCTRL_[pri]); pktCTRL_[pri] = 0;
		break;
	/*
	 * Sent DATA, but did not receive an ACK packet.
	 */
	case MAC_SEND:
		RetransmitDATA(pri);
		break;
	/*
	 * Sent an ACK, and now ready to resume transmission.
	 */
	case MAC_ACK:
		assert(pktCTRL_[pri]);
		Packet::free(pktCTRL_[pri]); pktCTRL_[pri] = 0;
		break;
	case MAC_IDLE:
		break;
	default:
		assert(0);
	}
    }
    //  if(mhDefer_.busy()) mhDefer_.stop();
    if(!cfb_active) tx_resume();
    
}

/* ======================================================================
   Outgoing Packet Routines
   ====================================================================== */
int
Mac802_11e::check_pktCTRL(int pri) 
{

	struct hdr_mac802_11e *mh;
	double timeout;

	if(pktCTRL_[pri] == 0)
		return -1;
	if(tx_state_[pri] == MAC_CTS || tx_state_[pri] == MAC_ACK)
		return -1;

	mh = HDR_MAC802_11E(pktCTRL_[pri]);
							  
	switch(mh->dh_fc.fc_subtype) {
	/*
	 *  If the medium is not IDLE, don't send the CTS.
	 */
	    case MAC_Subtype_CTS:
	      if(!is_idle()) {
			discard(pktCTRL_[pri], DROP_MAC_BUSY); pktCTRL_[pri] = 0;
			return 0;
	      }
		set_tx_state(pri, MAC_CTS);
		
		/*
		 * timeout:  cts + data tx time calculated by
		 *           adding cts tx time to the cts duration
		 *           minus ack tx time -- this timeout is
		 *           a guess since it is unspecified
		 *           (note: mh->dh_duration == cf->cf_duration)
		 */
		timeout = txtime(phymib_.getCTSlen(), basicRate_)
			+ DSSS_EDCA_MaxPropagationDelay			// XXX
			+ sec(mh->dh_duration)
			+ DSSS_EDCA_MaxPropagationDelay			// XXX
			- sifs_
			- txtime(phymib_.getACKlen(), basicRate_);
		
		break;
		/*
		 * IEEE 802.11 specs, section 9.2.8
		 * Acknowledments are sent after an SIFS, without regard to
		 * the busy/idle state of the medium.
		 */
	    case MAC_Subtype_ACK:
		set_tx_state(pri, MAC_ACK);

		timeout = txtime(phymib_.getACKlen(), basicRate_);
		
		break;
	default:
		fprintf(stderr, "check_pktCTRL:Invalid MAC Control subtype\n");
		exit(1);
	}
	transmit(pktCTRL_[pri], timeout);
	return 0;
}

int
Mac802_11e::check_pktRTS(int pri) 
{

	struct hdr_mac802_11e *mh;
	double timeout;

	assert(mhBackoff_.backoff(pri) == 0);
	if(pktRTS_[pri] == 0)
 		return -1;
	//struct hdr_cmn *ch = HDR_CMN(pktRTS_);
	mh = HDR_MAC802_11E(pktRTS_[pri]);

 	switch(mh->dh_fc.fc_subtype) {
	case MAC_Subtype_RTS:
	  if(! is_idle()) {
		    inc_cw(pri); 
		    mhBackoff_.start(pri, getCW(pri), is_idle());

		    return 0;
	  }
		set_tx_state(pri, MAC_RTS);
		timeout = txtime(phymib_.getRTSlen(), basicRate_)
			+ DSSS_EDCA_MaxPropagationDelay			// XXX
			+ sifs_
			+ txtime(phymib_.getCTSlen(), basicRate_)
			+ DSSS_EDCA_MaxPropagationDelay;			// XXX
		break;
	default:
	    fprintf(stderr, "check_pktRTS:Invalid MAC Control subtype\n");
		exit(1);
	}
	transmit(pktRTS_[pri], timeout);
	return 0;
}

int 
Mac802_11e::check_pktTx(int pri)
{

        struct hdr_mac802_11e *mh;
	double timeout;
	assert(mhBackoff_.backoff(pri) == 0);
	
	if(pktTx_[pri] == 0) {
	    return -1;
	}
	
	mh = HDR_MAC802_11E(pktTx_[pri]);
       	//int len = HDR_CMN(pktTx_)->size();
	switch(mh->dh_fc.fc_subtype) {
	case MAC_Subtype_Data:
	    
	    /*if(!is_idle()){
	      sendRTS(pri, ETHER_ADDR(mh->dh_da));
	      inc_cw(LEVEL(pktTx_[pri]));
	      mhBackoff_.start(LEVEL(pktTx_[pri]), getCW(LEVEL(pktTx_[pri])), is_idle());
	      return 0;
	    }*/
	    
	    set_tx_state(pri, MAC_SEND);
	    if((u_int32_t)ETHER_ADDR(mh->dh_da) != MAC_BROADCAST)
		timeout = txtime(pktTx_[pri])
		            + DSSS_EDCA_MaxPropagationDelay		// XXX
			    + sifs_
			    + txtime(phymib_.getACKlen(), basicRate_)
			    + DSSS_EDCA_MaxPropagationDelay;		// XXX
		else
		    timeout = txtime(pktTx_[pri]);
		break;
	    default:
	    fprintf(stderr, "check_pktTx:Invalid MAC Control subtype\n");
		//printf("pktRTS:%x, pktCTS/ACK:%x, pktTx:%x\n",pktRTS_, pktCTRL_,pktTx_);
		exit(1);
	}
	transmit(pktTx_[pri], timeout);
	return 0;
}
/*
 * Low-level transmit functions that actually place the packet onto
 * the channel.
 */
void
Mac802_11e::sendRTS(int pri, int dst)
{

	Packet *p = Packet::alloc();
	hdr_cmn* ch = HDR_CMN(p);
	struct rts_frame *rf = (struct rts_frame*)p->access(hdr_mac::offset_);
	
	assert(pktTx_[pri]);
	assert(pktRTS_[pri] == 0);

	/*
	 *  If the size of the packet is larger than the
	 *  RTSThreshold, then perform the RTS/CTS exchange.
	 *
	 *  XXX: also skip if destination is a broadcast
	 */
	if( (u_int32_t) HDR_CMN(pktTx_[pri])->size() < macmib_.RTSThreshold ||
	    (u_int32_t) dst == MAC_BROADCAST) {
		Packet::free(p);
		//p = 0;
		return;
	}

	ch->uid() = 0;
	ch->ptype() = PT_MAC;
	ch->size() = phymib_.getRTSlen();
	ch->iface() = -2;
	ch->error() = 0;

	bzero(rf, MAC_HDR_LEN);

	rf->rf_fc.fc_protocol_version = MAC_ProtocolVersion;
 	rf->rf_fc.fc_type	= MAC_Type_Control;
 	rf->rf_fc.fc_subtype	= MAC_Subtype_RTS;
 	rf->rf_fc.fc_to_ds	= 0;
 	rf->rf_fc.fc_from_ds	= 0;
 	rf->rf_fc.fc_more_frag	= 0;
 	rf->rf_fc.fc_retry	= 0;
 	rf->rf_fc.fc_pwr_mgt	= 0;
 	rf->rf_fc.fc_more_data	= 0;
 	rf->rf_fc.fc_wep	= 0;
 	rf->rf_fc.fc_order	= 0;

	//rf->rf_duration = RTS_DURATION(pktTx_);
	STORE4BYTE(&dst, (rf->rf_ra));
	
	/* store rts tx time */
 	ch->txtime() = txtime(ch->size(), basicRate_);
	
	STORE4BYTE(&index_, (rf->rf_ta));
	/* calculate rts duration field */
	rf->rf_duration = usec(sifs_
			       + txtime(phymib_.getCTSlen(), basicRate_)
			       + sifs_
			       + txtime(pktTx_[pri])
			       + sifs_
			       + txtime(phymib_.getACKlen(), basicRate_));
	
	
	pktRTS_[pri] = p;
}

void
Mac802_11e::sendCTS(int pri, int dst, double rts_duration)
{

	Packet *p = Packet::alloc();
	hdr_cmn* ch = HDR_CMN(p);
	struct cts_frame *cf = (struct cts_frame*)p->access(hdr_mac::offset_);

	assert(pktCTRL_[pri] == 0);

	ch->uid() = 0;
	ch->ptype() = PT_MAC;
	ch->size() = phymib_.getCTSlen();
	ch->iface() = -2;
	ch->error() = 0;
	//ch->direction() = hdr_cmn::DOWN;
	bzero(cf, MAC_HDR_LEN);

	cf->cf_fc.fc_protocol_version = MAC_ProtocolVersion;
	cf->cf_fc.fc_type	= MAC_Type_Control;
	cf->cf_fc.fc_subtype	= MAC_Subtype_CTS;
 	cf->cf_fc.fc_to_ds	= 0;
 	cf->cf_fc.fc_from_ds	= 0;
 	cf->cf_fc.fc_more_frag	= 0;
 	cf->cf_fc.fc_retry	= 0;
 	cf->cf_fc.fc_pwr_mgt	= 0;
 	cf->cf_fc.fc_more_data	= 0;
 	cf->cf_fc.fc_wep	= 0;
 	cf->cf_fc.fc_order	= 0;
	
	//cf->cf_duration = CTS_DURATION(rts_duration);
	STORE4BYTE(&dst, (cf->cf_ra));
	
	/* store cts tx time */
	ch->txtime() = txtime(ch->size(), basicRate_);
	
	/* calculate cts duration */
	cf->cf_duration = usec(sec(rts_duration)
			       - sifs_
			       - txtime(phymib_.getCTSlen(), basicRate_));
	
	pktCTRL_[pri] = p;
	
}

void
Mac802_11e::sendACK(int pri, int dst)
{

	Packet *p = Packet::alloc();
	hdr_cmn* ch = HDR_CMN(p);
	struct ack_frame *af = (struct ack_frame*)p->access(hdr_mac::offset_);
	assert(pktCTRL_[pri] == 0);

	ch->uid() = 0; // ACK-UID
	ch->ptype() = PT_MAC;
	ch->size() = phymib_.getACKlen();
	ch->iface() = -2;
	ch->error() = 0;
	HDR_IP(p)->prio() = pri; //same priority as data packet
	bzero(af, MAC_HDR_LEN);

	af->af_fc.fc_protocol_version = MAC_ProtocolVersion;
 	af->af_fc.fc_type	= MAC_Type_Control;
 	af->af_fc.fc_subtype	= MAC_Subtype_ACK;
 	af->af_fc.fc_to_ds	= 0;
 	af->af_fc.fc_from_ds	= 0;
 	af->af_fc.fc_more_frag	= 0;
 	af->af_fc.fc_retry	= 0;
 	af->af_fc.fc_pwr_mgt	= 0;
 	af->af_fc.fc_more_data	= 0;
 	af->af_fc.fc_wep	= 0;
 	af->af_fc.fc_order	= 0;

	//af->af_duration = ACK_DURATION();
	STORE4BYTE(&dst, (af->af_ra));

	/* store ack tx time */
 	ch->txtime() = txtime(ch->size(), basicRate_);
	
	/* calculate ack duration */
 	af->af_duration = 0;	
	
	pktCTRL_[pri] = p;
}

void
Mac802_11e::sendDATA(int pri, Packet *p)
{

	hdr_cmn* ch = HDR_CMN(p);
	struct hdr_mac802_11e* dh = HDR_MAC802_11E(p);
	assert(pktTx_[pri] == 0);

	/*
	 * Update the MAC header
	 */
	ch->size() += phymib_.getHdrLen11();

	dh->dh_fc.fc_protocol_version = MAC_ProtocolVersion;
	dh->dh_fc.fc_type       = MAC_Type_Data;
	dh->dh_fc.fc_subtype    = MAC_Subtype_Data;
	//printf(".....p = %x, mac-subtype-%d\n",p,dh->dh_fc.fc_subtype);
	
	dh->dh_fc.fc_to_ds      = 0;
	dh->dh_fc.fc_from_ds    = 0;
	dh->dh_fc.fc_more_frag  = 0;
	dh->dh_fc.fc_retry      = 0;
	dh->dh_fc.fc_pwr_mgt    = 0;
	dh->dh_fc.fc_more_data  = 0;
	dh->dh_fc.fc_wep        = 0;
	dh->dh_fc.fc_order      = 0;

	/* store data tx time */
	if((u_int32_t)ETHER_ADDR(dh->dh_da) != MAC_BROADCAST) {
		/* store data tx time for unicast packets */
		ch->txtime() = txtime(ch->size(), dataRate_);
		
		//dh->dh_duration = DATA_DURATION();
		
		dh->dh_duration = usec(txtime(phymib_.getACKlen(), basicRate_) 
 				       + sifs_);
	} else {
		/* store data tx time for broadcast packets (see 9.6) */
		ch->txtime() = txtime(ch->size(), basicRate_);
		
		dh->dh_duration = 0;
	}

	pktTx_[pri] = p;
}

/* ======================================================================
   Retransmission Routines
   ====================================================================== */
void
Mac802_11e::RetransmitRTS(int pri)
{

	assert(pktTx_[pri]);
	assert(pktRTS_[pri]);
	assert(mhBackoff_.backoff(pri) == 0);

	macmib_.RTSFailureCount++;

	ssrc_[pri] += 1;			// STA Short Retry Count

	if(ssrc_[pri] >= macmib_.ShortRetryLimit) {
		discard(pktRTS_[pri], DROP_MAC_RETRY_COUNT_EXCEEDED); pktRTS_[pri] = 0;
		/* tell the callback the send operation failed 
		   before discarding the packet */
		hdr_cmn *ch = HDR_CMN(pktTx_[pri]);
		if (ch->xmit_failure_) {
                        /*
                         *  Need to remove the MAC header so that 
                         *  re-cycled packets don't keep getting
                         *  bigger.
                         */
                        ch->size() -= phymib_.getHdrLen11();
                        ch->xmit_reason_ = XMIT_REASON_RTS;
                        ch->xmit_failure_(pktTx_[pri]->copy(),
                                          ch->xmit_failure_data_);
                }
		//printf("(%d)....discarding RTS:%x\n",index_,pktRTS_);
		rst_cw(pri);		
		discard(pktTx_[pri], DROP_MAC_RETRY_COUNT_EXCEEDED); pktTx_[pri] = 0;
		ssrc_[pri] = 0;
		
	} else {
		//printf("(%d)...retxing RTS:%x\n",index_,pktRTS_);
		struct rts_frame *rf;
		rf = (struct rts_frame*)pktRTS_[pri]->access(hdr_mac::offset_);
		rf->rf_fc.fc_retry = 1;

		inc_cw(LEVEL(pktTx_[pri]));
		mhBackoff_.start(LEVEL(pktTx_[pri]), getCW(pri), is_idle());
	}
}

void
Mac802_11e::RetransmitDATA(int pri)
{
    
	struct hdr_cmn *ch;
	struct hdr_mac802_11e *mh;
	u_int32_t *rcount, *thresh;

	assert(mhBackoff_.backoff(pri) == 0);
	
	assert(pktTx_[pri]);
	assert(pktRTS_[pri] == 0);

	ch = HDR_CMN(pktTx_[pri]);
	mh = HDR_MAC802_11E(pktTx_[pri]);
	
	/*
	 *  Broadcast packets don't get ACKed and therefore
	 *  are never retransmitted.
	 */
	if((u_int32_t)ETHER_ADDR(mh->dh_da) == MAC_BROADCAST) {
	  /*
	   * Backoff at end of TX.
	   */
	  if(!cfb_ || rx_state_ != MAC_IDLE){
		rst_cw(pri);
		mhBackoff_.start(pri, getCW(pri), is_idle());
		Packet::free(pktTx_[pri]); pktTx_[pri] = 0;
		return;
	  } else{
	    // if this is the first packet in cfb, we must take its
	    // duration into account, too.
	    if(cfb_dur == 0) {
	      //cout<<"Mac "<<index<<", setting cfb_dur after Broadcast\n";
	      cfb_dur = txtime(pktTx_[pri])
		            + sifs_;
		            //+ txtime(phymib_.getACKlen(), basicRate_);
	    }
	    assert(pktTx_[pri]);
	    Packet::free(pktTx_[pri]); pktTx_[pri] = 0;
	    cfb(pri);
	    return;
	    }
	} else if(cfb_) cfb_dur = 0;

	macmib_.ACKFailureCount++;
	rtx_[pri] = 1;
	if((u_int32_t) ch->size() <= macmib_.RTSThreshold) {
		rcount = &ssrc_[pri];
		thresh = &macmib_.ShortRetryLimit;
	}
	else {
		rcount = &slrc_[pri];
		thresh = &macmib_.LongRetryLimit;
	}

	(*rcount)++;

	if(*rcount > *thresh) {
	  numbytes_[pri] -= ch->size() - phymib_.getHdrLen11();
	  rtx_[pri] = 0;
	  macmib_.FailedCount++;
	  /* tell the callback the send operation failed 
	     before discarding the packet */
	  hdr_cmn *ch = HDR_CMN(pktTx_[pri]);
	  if (ch->xmit_failure_) {
	    ch->size() -= phymib_.getHdrLen11();
	    ch->xmit_reason_ = XMIT_REASON_ACK;
	    ch->xmit_failure_(pktTx_[pri]->copy(),
			      ch->xmit_failure_data_);
                }
	  rst_cw(pri);
	  discard(pktTx_[pri], DROP_MAC_RETRY_COUNT_EXCEEDED); pktTx_[pri] = 0;
	  //printf("(%d)DATA discarded: count exceeded\n",index_);
	  *rcount = 0;
		
		
	}
	else {
		struct hdr_mac802_11e *dh;
		dh = HDR_MAC802_11E(pktTx_[pri]);
		dh->dh_fc.fc_retry = 1;

		sendRTS(pri, ETHER_ADDR(mh->dh_da));
		//printf("(%d)retxing data:%x..sendRTS..\n",index_,pktTx_);
		inc_cw(LEVEL(pktTx_[pri]));
		mhBackoff_.start(pri, getCW(pri), is_idle());
	}
}

/* ======================================================================
   Incoming Packet Routines
   ====================================================================== */
void
Mac802_11e::send(Packet *p, Handler *h)

{

        int pri = LEVEL(p);
	start_handle_[pri]=Scheduler::instance().clock();
	double rTime;
	struct hdr_mac802_11e* dh = HDR_MAC802_11E(p);

	/* 
	 * drop the packet if the node is in sleep mode
	 XXX sleep mode can't stop node from sending packets
	 */
	EnergyModel *em = netif_->node()->energy_model();
	if (em && em->sleep()) {
		em->set_node_sleep(0);
		em->set_node_state(EnergyModel::INROUTE);
	}
	callback_[pri] = h;
	sendDATA(pri, p); // framing and calculation of  tx Duration 
	sendRTS(pri, ETHER_ADDR(dh->dh_da)); //check whether size exceeds RTSthreshold 

	/*
	 * Assign the data packet a sequence number.
	 */
	dh->dh_scontrol = sta_seqno_++;

	/*
	 *  If the medium is IDLE, we must wait for a DIFS
	 *  Space before transmitting.
	 */
        assert(mhDefer_.defer(pri) == 0); 
	
	if(mhBackoff_.backoff(pri) == 0) { //Mac can be still  in post-backoff
	  if(is_idle()) { 
			/*
			 * If we are already deferring, there is no
			 * need to reset the Defer timer.
			 */
			if(mhDefer_.defer(pri) == 0) {
			  rTime = ((Random::random() % getCW(LEVEL(p))) * phymib_.getSlotTime());
			    mhDefer_.start(LEVEL(p), getAIFS(LEVEL(p))); // + rTime);// - phymib_.getSlotTime());
				

			}			
		}
	/*
	 * If the medium is NOT IDLE, then we start
	 * the backoff timer.
	 */
		else {
		    mhBackoff_.start(LEVEL(p),getCW(LEVEL(p)), is_idle());
		}
	}  
	    
}

void
Mac802_11e::recv(Packet *p, Handler *h)
{
   	struct hdr_cmn *hdr = HDR_CMN(p);
	/*
	 * Sanity Check
	 */
	//assert(initialized());

	/*
	 *  Handle outgoing packets.
	 */
	if(hdr->direction() == hdr_cmn::DOWN) {
	    Scheduler &s = Scheduler::instance();
	    send(p, h);
	    return;
        }
	/*
	 *  Handle incoming packets.
	 *
	 *  We just received the 1st bit of a packet on the network
	 *  interface.
	 *
	 */
	/*
	 *  If the interface is currently in transmit mode, then
	 *  it probably won't even see this packet.  However, the
	 *  "air" around me is BUSY so I need to let the packet
	 *  proceed.  Just set the error flag in the common header
	 *  to that the packet gets thrown away.
	 */
	Scheduler &s = Scheduler::instance();
	if(tx_active_ && hdr->error() == 0 ) {
        		hdr->error() = 1;
	
	}

	if(rx_state_ == MAC_IDLE) {
		set_rx_state(MAC_RECV);
		pktRx_ = p;

		/*
		 * Schedule the reception of this packet, in
		 * txtime seconds.
		 */
		mhRecv_.start(txtime(p));
	} else {
		/*
		 *  If the power of the incoming packet is smaller than the
		 *  power of the packet currently being received by at least
                 *  the capture threshold, then we ignore the new packet.
		 */
		if(pktRx_->txinfo_.RxPr / p->txinfo_.RxPr >= p->txinfo_.CPThresh) {
			capture(p);
		} else {
			collision(p);
		}
	}
}

void
Mac802_11e::recv_timer()
{ 

    Scheduler &s = Scheduler::instance();
	u_int32_t src; 
	hdr_cmn *ch = HDR_CMN(pktRx_);
	hdr_mac802_11e *mh = HDR_MAC802_11E(pktRx_);
	u_int32_t dst = ETHER_ADDR(mh->dh_da);
	// XXX debug
	//struct cts_frame *cf = (struct cts_frame*)pktRx_->access(hdr_mac::offset_);
	//u_int32_t src = ETHER_ADDR(mh->dh_sa);
	
	u_int8_t  type = mh->dh_fc.fc_type;
	u_int8_t  subtype = mh->dh_fc.fc_subtype;

	assert(pktRx_);
	assert(rx_state_ == MAC_RECV || rx_state_ == MAC_COLL);
	
        /*
         *  If the interface is in TRANSMIT mode when this packet
         *  "arrives", then I would never have seen it and should
         *  do a silent discard without adjusting the NAV.
         */
        if(tx_active_) {
                Packet::free(pktRx_);
                goto done;
        }

	/*
	 * Handle collisions.
	 */
	if(rx_state_ == MAC_COLL) {
	    discard(pktRx_, DROP_MAC_COLLISION);
	    set_nav(usec(eifs_));
	    eifs_nav_ = eifs_;
	    goto done;
	}
	
	/*
	 * Check to see if this packet was received with enough
	 * bit errors that the current level of FEC still could not
	 * fix all of the problems - ie; after FEC, the checksum still
	 * failed.
	 */
	if( ch->error() ) {
	    Packet::free(pktRx_);
	    set_nav(usec(eifs_));
	    eifs_nav_ = eifs_;
	    goto done;
	}
	
	/*
	 * avoid Nav-reset bug:
	 * if received packet has no  errors and had no collision, but nav 
	 * was set due to an earlier collision, nav has to be reset!
	 */
         if(mhNav_.busy()) reset_eifs_nav();
	
	/*
	 * IEEE 802.11 specs, section 9.2.5.6
	 *	- update the NAV (Network Allocation Vector)
	 */
	if(dst != (u_int32_t)index_) {
	    set_nav(mh->dh_duration);
	}

        /* tap out - */
        if (tap_ && type == MAC_Type_Data &&
            MAC_Subtype_Data == subtype ) 
		tap_->tap(pktRx_);
	/*
	 * Adaptive Fidelity Algorithm Support - neighborhood infomation 
	 * collection
	 *
	 * Hacking: Before filter the packet, log the neighbor node
	 * I can hear the packet, the src is my neighbor
	 */
	if (netif_->node()->energy_model() && 
	    netif_->node()->energy_model()->adaptivefidelity()) {
		src = ETHER_ADDR(mh->dh_sa);
		netif_->node()->energy_model()->add_neighbor(src);
	}
	/*
	 * Address Filtering
	 */
	if(dst != (u_int32_t)index_ && dst != MAC_BROADCAST) {
		/*
		 *  We don't want to log this event, so we just free
		 *  the packet instead of calling the drop routine.
		 */
		discard(pktRx_, "---");
		goto done;
	}

	switch(type) {

	case MAC_Type_Management:
		discard(pktRx_, DROP_MAC_PACKET_ERROR);
		goto done;
		break;

	case MAC_Type_Control:
		switch(subtype) {
		case MAC_Subtype_RTS:
			recvRTS(pktRx_);
			break;
		case MAC_Subtype_CTS:
			recvCTS(pktRx_);
			break;
		case MAC_Subtype_ACK:
			recvACK(pktRx_);
			break;
		default:
			fprintf(stderr,"recvTimer1:Invalid MAC Control Subtype %x\n",
				subtype);
			exit(1);
		}
		break;
	case MAC_Type_Data:
		switch(subtype) {
		case MAC_Subtype_Data:
			recvDATA(pktRx_);
			break;
		default:
			fprintf(stderr, "recv_timer2:Invalid MAC Data Subtype %x\n",
				subtype);
			exit(1);
		}
		break;
	default:
		fprintf(stderr, "recv_timer3:Invalid MAC Type %x\n", subtype);
		exit(1);
	}
 done:
	pktRx_ = 0;
	rx_resume();
}


void
Mac802_11e::recvRTS(Packet *p)
{

        int pri = LEVEL(p);
	struct rts_frame *rf = (struct rts_frame*)p->access(hdr_mac::offset_);

	if(tx_state_[pri] != MAC_IDLE) {
		discard(p, DROP_MAC_BUSY);
		return;
	}

	/*
	 *  If I'm responding to someone else, discard this RTS.
	 */
	if(pktCTRL_[pri]) {
		discard(p, DROP_MAC_BUSY);
		return;
	}

	sendCTS(pri, ETHER_ADDR(rf->rf_ta), rf->rf_duration);

	tx_resume();

	mac_log(p);
}

/*
 * txtime()	- pluck the precomputed tx time from the packet header
 */
double
Mac802_11e::txtime(Packet *p)
 {
	 struct hdr_cmn *ch = HDR_CMN(p);
	 double t = ch->txtime();
	 if (t < 0.0) {
		 drop(p, "XXX");
 		exit(1);
	 }
	 return t;
 }

 
/*
 * txtime()	- calculate tx time for packet of size "psz" bytes 
 *		  at rate "drt" bps
 */
double
Mac802_11e::txtime(double psz, double drt)
{
  double dsz = psz - phymib_.getPLCPhdrLen();
  int plcp_hdr = phymib_.getPLCPhdrLen() << 3;
  int datalen = (int)dsz << 3;
  
  double t = (((double)plcp_hdr)/phymib_.getPLCPDataRate()) + (((double)datalen)/drt);
  return(t);
}



void
Mac802_11e::recvCTS(Packet *p)
{

        int pri = LEVEL(p);
	if(tx_state_[pri] != MAC_RTS) {
		discard(p, DROP_MAC_INVALID_STATE);
		return;
	}
	assert(pktRTS_[pri]);
	Packet::free(pktRTS_[pri]); pktRTS_[pri] = 0;

	assert(pktTx_[pri]);
	// debug
	//struct hdr_mac802_11 *mh = HDR_MAC802_11(pktTx_);
	//printf("(%d):recvCTS:pktTx_-%x,mac-subtype-%d & pktCTS_:%x\n",index_,pktTx_,mh->dh_fc.fc_subtype,p);
	
	mhSend_.stop();

	/*
	 * The successful reception of this CTS packet implies
	 * that our RTS was successful.  Hence, we can reset
	 * the Short Retry Count and the CW.
	 */
	//ssrc_ = 0;
	//rst_cw();
	//	if(mhDefer_.busy()) mhDefer_.stop();

	tx_resume();

	mac_log(p);
}

void
Mac802_11e::recvDATA(Packet *p)
{

        int pri = LEVEL(p);
	struct hdr_mac802_11e *dh = HDR_MAC802_11E(p);
	u_int32_t dst, src, size;

	{	struct hdr_cmn *ch = HDR_CMN(p);

		dst = ETHER_ADDR(dh->dh_da);
		src = ETHER_ADDR(dh->dh_sa);
		size = ch->size();

		/*
		 * Adjust the MAC packet size - ie; strip
		 * off the mac header
		 */
		ch->size() -= phymib_.getHdrLen11();
		ch->num_forwards() += 1;
	}

	/*
	 *  If we sent a CTS, clean up...
	 */
	if(dst != MAC_BROADCAST) {
		if(size >= macmib_.RTSThreshold) {
			if (tx_state_[pri] == MAC_CTS) {
				assert(pktCTRL_[pri]);
				Packet::free(pktCTRL_[pri]); pktCTRL_[pri] = 0;
				mhSend_.stop();
				/*
				 * Our CTS got through.
				 */
				printf("(%d): RECVING DATA!\n",index_);
				//ssrc_ = 0;
				//rst_cw();
			}
			else {
				discard(p, DROP_MAC_BUSY);
				printf("(%d)..discard DATA\n",index_);
				return;
			}
			sendACK(pri, src);
			tx_resume(); 
		}
		/*
		 *  We did not send a CTS and there's no
		 *  room to buffer an ACK.
		 */
		else {
			if(pktCTRL_[pri]) {
				discard(p, DROP_MAC_BUSY);
				return;
			}
			
			sendACK(pri, src);
			if(mhSend_.busy() == 0){
			    tx_resume();
			}
		}
	}

	/* ============================================================
	    Make/update an entry in our sequence number cache.
	   ============================================================ */

	/* Changed by Debojyoti Dutta. This upper loop of if{}else was 
	   suggested by Joerg Diederich <dieder@ibr.cs.tu-bs.de>. 
	   Changed on 19th Oct'2000 */

        if(dst != MAC_BROADCAST) {
                if (src < (u_int32_t) cache_node_count_) {
		            Host *h = &cache_[src];

                        if(h->seqno && h->seqno == dh->dh_scontrol) {
			    discard(p, DROP_MAC_DUPLICATE);
			    return;
                        }
                        h->seqno = dh->dh_scontrol;
		    
                } else {
			static int count = 0;
			if (++count <= 10) {
				printf ("MAC_802_11e: accessing MAC cache_ array out of range (src %u, dst %u, size %d)!\n", src, dst, cache_node_count_);
				if (count == 10)
					printf ("[suppressing additional MAC cache_ warnings]\n");
			};
		};
	}
	
	/*

	 *  Pass the packet up to the link-layer.
	 *  XXX - we could schedule an event to account
	 *  for this processing delay.
	 */
	//p->incoming = 1;
	// XXXXX NOTE: use of incoming flag has been depracated; In order to track direction of pkt flow, direction_ in hdr_cmn is used instead. see packet.h for details. 
	uptarget_->recv(p, (Handler*) 0);
}


void
Mac802_11e::recvACK(Packet *p)
{

        int pri = LEVEL(p);
	struct hdr_cmn *ch = HDR_CMN(p);
	if(tx_state_[pri] != MAC_SEND) {
	    discard(p, DROP_MAC_INVALID_STATE);
	return;
	}
	//printf("(%d)...................recving ACK:%x\n",index_,p);
	
	mhSend_.stop();
	
	/*
	 * The successful reception of this ACK packet implies
	 * that our DATA transmission was successful.  Hence,
	 * we can reset the Short/Long Retry Count and the CW.
	 */
	if((u_int32_t) ch->size() <= macmib_.RTSThreshold)
		ssrc_[pri] = 0;
	else
		slrc_[pri] = 0;

	/* succesful transmission => give delay
	 * to Akaroa
	 */
	if(rtx_[pri]) rtx_[pri] = 0;
	double delay=Scheduler::instance().clock() - start_handle_[pri];
	#if AKAROA > 0
	if(AKAROA index_ > 0) {
	  AkObservation((6 * (index_ - 1)) + (pri + 4), delay);
	  start_handle_[pri]=0;
	}
	#endif

	sending = 0;
	check_backoff_timer();
        /*
	 * Backoff before sending again.
	 */
	if(!cfb_ || ch->size() > macmib_.RTSThreshold) {
	  assert(mhBackoff_.backoff(pri) == 0);
	  rst_cw(pri);
	  mhBackoff_.start(pri, getCW(pri), is_idle());
	  assert(pktTx_[pri]);
	  Packet::free(pktTx_[pri]); pktTx_[pri] = 0;
	  tx_resume();

	}
	else{
	  // if this is the first packet in cfb, we must take its
	  // duration into account, too.
	  if(cfb_dur == 0) {
	      cfb_dur = txtime(pktTx_[pri])
		            + sifs_
		            + txtime(phymib_.getACKlen(), basicRate_);
	  }
	  pktRx_ = 0;
	  rx_resume();
	  assert(pktTx_[pri]);
	  Packet::free(pktTx_[pri]); pktTx_[pri] = 0;
	  cfb(pri);
	}
	mac_log(p);
}

void Mac802_11e::cfb(int pri)
{
  double timeout;
  struct hdr_mac802_11e *mh;
  
  // next packet out of queue
  //cout<<"packets in queue:"<<queue_->pri_[pri].getLen()<<"\n";
  if(queue_->pri_[pri].getLen() > 0) {
      Packet* p = queue_->pri_[pri].deque(); 
      // framing
      sendDATA(pri, p);
      hdr_cmn *ch = HDR_CMN(pktTx_[pri]);
      mh = HDR_MAC802_11E(pktTx_[pri]);
      //cout<<"Mac "<<index_<<" in cfb(), pri "<<pri<<", cfb_bytes "<<cfb_bytes<<" + "<<ch->size()<<", cfb_maxbytes "<<cfb_maxbytes_<<"\n";
      if((u_int32_t)ETHER_ADDR(mh->dh_da) != MAC_BROADCAST) {
	  cfb_dur +=  sifs_ 
                      + txtime(pktTx_[pri])
		      + sifs_
                      + txtime(phymib_.getACKlen(), basicRate_);
	  cfb_broadcast = 0;
      } else {
	      cfb_dur += sifs_ 
	              + txtime(pktTx_[pri]);
              cfb_broadcast = 1;
      }
  } else cfb_dur = txop_limit_[pri] + 1; 
 
  if(cfb_dur <= txop_limit_[pri]) {
    // send
    if((u_int32_t)ETHER_ADDR(mh->dh_da) != MAC_BROADCAST)
      timeout = txtime(pktTx_[pri])
	                    + DSSS_EDCA_MaxPropagationDelay	
			    + sifs_
			    + txtime(phymib_.getACKlen(), basicRate_)
			    + DSSS_EDCA_MaxPropagationDelay;

    else
      timeout = txtime(pktTx_[pri]);    
    cfb_active = 1;
    mhSifs_.start(pri, sifs_);
  }
  else {
    cfb_dur = 0;
    cfb_broadcast = 0;
    assert(mhBackoff_.backoff(pri) == 0);
    rst_cw(pri);
    mhBackoff_.start(pri, getCW(pri), is_idle());
    //assert(pktTx_[pri]);
    //Packet::free(pktTx_[pri]); pktTx_[pri] = 0;
    tx_resume();
  }
}

// request parameters for each priority from the corresponding queues
double Mac802_11e::getAIFS(int pri)
{
    if(!AIFSset){
      levels = queue_->getLevels();
      for(int i = 0; i < levels; i++ ){
	slotnum = queue_->pri_[i].getAIFS();
	aifs_[i] = sifs_ + (slotnum * phymib_.getSlotTime());
	txop_limit_[i] = queue_->pri_[i].getTXOPLimit();
	//	    cout<<"Mac "<<index_<<", pri: "<<i<<", txop_limit:"<<txop_limit_[i]<<"\n";
      }
      AIFSset = 1;
    }
    return aifs_[pri];
}


int Mac802_11e::getCW(int level)
{
    if(!CWset){
	levels = queue_->getLevels();
	for(int i = 0; i < levels; i++ ){
	    cw_[i] = queue_->pri_[i].getCW_MIN();
	    cwmin_[i] = queue_->pri_[i].getCW_MIN(); 
	    cwmax_[i] = queue_->pri_[i].getCW_MAX(); 
	}
	CWset = 1;
    }
    return cw_[level];
}

void
Mac802_11e::setQ(PriQ* priqueue){
    queue_ = priqueue;
}

inline void 
Mac802_11e::reset_eifs_nav() {
  if (eifs_nav_ > 0) {
    double now = Scheduler::instance().clock();
    
    assert(nav_ > now);
    assert(mhNav_.busy());
    
    mhNav_.stop();
    nav_ -= eifs_nav_;
    eifs_nav_ = 0.0;
    if (nav_ > now) {
      mhNav_.start(nav_ - now);
    } else {
      nav_ = now;
      check_backoff_timer();
    }
  }
}


bool Mac802_11e::inc_retryCounter(int pri) {
  u_int32_t *rcount, *thresh;
  struct hdr_cmn *ch = HDR_CMN(pktTx_[pri]);
  if((u_int32_t) ch->size() <= macmib_.RTSThreshold) {
    ssrc_[pri]++;
    rcount = &ssrc_[pri];
    thresh = &macmib_.ShortRetryLimit;
  }
  else {
    slrc_[pri]++;
    rcount = &slrc_[pri];
    thresh = &macmib_.LongRetryLimit;
  }
  if(*rcount > *thresh) {
    rtx_[pri] = 0;
    macmib_.FailedCount++;
    rst_cw(pri);
    discard(pktTx_[pri], DROP_MAC_RETRY_COUNT_EXCEEDED); pktTx_[pri] = 0;
    *rcount = 0;
    return 1;
  } else
     return 0;
}
