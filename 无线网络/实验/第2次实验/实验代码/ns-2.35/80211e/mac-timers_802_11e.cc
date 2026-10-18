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
#include <delay.h>
#include <connector.h>
#include <packet.h>
#include <random.h>
//#include <iostream.h>
#include <iostream>
using namespace std;
#define BDEBUG 0 

//#include <debug.h>
#include <arp.h>
#include <ll.h>
#include <mac.h>
#include "mac-timers_802_11e.h"
#include "mac-802_11e.h"

// set to 1 for EDCA, 0 for older EDCF
#define EDCA 0 
// set to one if retry counter should not be increased
// due to internal collision (not standard conform!)
#define NO_RTX_INC 0

#define INF   (1e12)
#define ROUND (1e-12)
#define MU(x)    x * (1e+6)


/* ======================================================================
   Timers
   ====================================================================== */

void
MacTimer_802_11e::start(double time)
{
	Scheduler &s = Scheduler::instance();
	assert(busy_ == 0);

	busy_ = 1;
	paused_ = 0;
	stime = s.clock();
	rtime = time;
	assert(rtime >= 0.0);
	s.schedule(this, &intr, rtime);
}



void
MacTimer_802_11e::stop(void)
{
	Scheduler &s = Scheduler::instance();

	assert(busy_);

	if(paused_ == 0)
		s.cancel(&intr);

	busy_ = 0;
	paused_ = 0;
	stime = 0.0;
	rtime = 0.0;
}



/* ======================================================================
   Defer Timer
   ====================================================================== */
void
DeferTimer_802_11e::start(int pri, double time)
{
	Scheduler &s = Scheduler::instance();
	bool another = 0;
	assert(defer_[pri] == 0);
	for(int i = 0; i < MAX_PRI; i++ ){	
		if(defer_[i] && busy_) {
			another = 1;
		}
	}
	
	if(another){
		pause();
	}
	busy_ = 1;

	defer_[pri] = 1;
	stime_[pri] = s.clock();
	rtime_[pri] = time; 
	double delay = INF;
	int prio = MAX_PRI + 1;
	for(int pri = 0; pri < MAX_PRI; pri++){
		if(defer_[pri]){
			stime_[pri] = s.clock();
			double delay_ = rtime_[pri]; 
			if((delay_ < delay)) {
				delay = delay_;
				prio = pri;
			}
		}
	}
	if(prio < MAX_PRI + 1) {
		assert(rtime_[prio] >=0);
		s.schedule(this, &intr, rtime_[prio]);
		paused_ = 0;
	} else {
		exit(0);

	}
}

void 
DeferTimer_802_11e::stop()
{
	busy_ = 0;
	for(int pri = 0; pri < MAX_PRI;pri++){
		if(defer_[pri]) mac->defer_stop(pri);
		defer_[pri] = 0;
		stime_[pri] = 0;
		rtime_[pri] = 0;
		
	}
	Scheduler &s = Scheduler::instance();
	s.cancel(&intr);
}
void
DeferTimer_802_11e::pause()
{
	Scheduler &s = Scheduler::instance();
	for(int pri = 0; pri < MAX_PRI; pri++ ){	
		if(defer_[pri] && busy_){
			double st = s.clock();            //now
			double rt = stime_[pri];   // Start-Time of defer
			double sr = st - rt;
			assert(busy_ && !paused_);
			if(rtime_[pri] - sr >= 0.0) {
				rtime_[pri] -= sr;
				assert(rtime_[pri] >= 0.0);	
			} else{
				if(rtime_[pri] + ROUND - sr >= 0.0){ 
					rtime_[pri] = 0;
				} else {
					cout<<"ERROR in DeferTimer::pause(), rtime_["<<pri<<"]  is "<<rtime_[pri]<<", sr:"<<sr<<"  \n";
					exit(0);
				}
			}
		}
	}
	s.cancel(&intr);
	paused_ = 1;
}


void    
DeferTimer_802_11e::handle(Event *)
{       
	Scheduler &s = Scheduler::instance();
	double delay = INF;
	int prio = MAX_PRI + 1;

	for( int pri = 0; pri < MAX_PRI; pri++) {
		
		if(rtime_[pri] >= 0 && defer_[pri]){
			
			double delay_ = rtime_[pri];
			if((delay_ < delay) && defer_[pri]) {
				delay = delay_;
				prio = pri;
			}
		}
	}

	if(prio < MAX_PRI + 1){
		busy_ = 0;
		paused_ = 0;
		defer_[prio] = 0;
		stime_[prio] = 0.0;
		rtime_[prio] = 0.0;
		mac->deferHandler(prio);
	} else {
		cout<<"handling ERROR in DeferTimer::handler \n"; 
		exit(0);
	}
	
        //check if there is another DeferTimer active
	for( int pri = 0; pri < MAX_PRI; pri++) {
		if(rtime_[pri] >= 0 && defer_[pri]){
		  rtime_[pri] = 0.0;
		  stime_[pri] = 0.0;
		  defer_[pri] = 0;
		  mac->defer_stop(pri);
		}
	}	
}

int
DeferTimer_802_11e::defer(int pri) {
	return defer_[pri];
}
/* ======================================================================
   NAV Timer
   ====================================================================== */
void    
NavTimer_802_11e::handle(Event *)
{       
	busy_ = 0;
	paused_ = 0;
	stime = 0.0;
	rtime = 0.0;

	mac->navHandler();
}


/* ======================================================================
   Receive Timer
   ====================================================================== */
void    
RxTimer_802_11e::handle(Event *)
{       
	busy_ = 0;
	paused_ = 0;
	stime = 0.0;
	rtime = 0.0;
	mac->recvHandler();
}


/* ======================================================================
   Send Timer
   ====================================================================== */
void    
TxTimer_802_11e::handle(Event *)
{       
	busy_ = 0;
	paused_ = 0;
	stime = 0.0;
	rtime = 0.0;



	mac->sendHandler();
}


/* ======================================================================
   Interface Timer
   ====================================================================== */
void
IFTimer_802_11e::handle(Event *)
{
	Scheduler &s = Scheduler::instance();
	busy_ = 0;
	paused_ = 0;
	stime = 0.0;
	rtime = 0.0;
	mac->txHandler();
	
}
/* ======================================================================
 Defer Timer for SIFS
   ====================================================================== */
void
SIFSTimer_802_11e::start(int pri, double time)
{

	Scheduler &s = Scheduler::instance();
	if(busy_ == 1){cout<<"Mac "<<mac->index_<<", ERROR in SIFSTimer!"; exit(0);}
	assert(sifs_[pri] == 0);
	
	busy_ = 1;

        sifs_[pri] = 1;
	stime_[pri] = s.clock();
	rtime_[pri] = time; 
	s.schedule(this, &intr, rtime_[pri]);
}

void
SIFSTimer_802_11e::handle(Event *)
{
	Scheduler &s = Scheduler::instance();
	busy_ = 0;
	prio = 0;
		
	for(int pri = 0; pri < MAX_PRI; pri++){
		if(sifs_[pri]) { 
			prio = pri;
			break;
		}
	}
	
	for(int i = 0; i < MAX_PRI; i++){	
		sifs_[i]  = 0;
		stime_[i] = 0.0;
		rtime_[i] = 0.0;
	}
	mac->deferHandler(prio);
	
}
/* ======================================================================
   Backoff Timer
   ====================================================================== */

/*
 * round to the next slot, 
 * this is needed if a station initiates a transmission
 * and has not been synchronized by the end of last frame on channel
 */

inline void 
BackoffTimer_802_11e::round_time(int pri)
{
	if(BDEBUG>2) printf("now %4.8f Mac: %d in BackoffTimer::round_time\n",
			   Scheduler::instance().clock(), mac->index_);
	if(BDEBUG==1) printf("1 now %4.8f Mac: %d slottime %2.2f rtime_[pri] %2.2f \n", 
	       Scheduler::instance().clock(),mac->index_,MU(slottime),MU(rtime_[pri]));
	//	double slottime = mac->phymib_.getSlotTime();
	double rmd = remainder(rtime_[pri], slottime);
	if(rmd + ROUND < 0){
		printf("ERROR: in BackoffTimer_802_11e:: round_time, remainder < 0 ?! rmd: %4.20f\n",rmd);
		exit(1);
	}
	if(rmd > ROUND){
		if(BDEBUG==1) printf("2 now %4.8f Mac: %d round_time slot-duration: %2.2f rtime: %2.2f r/s %f floor %f \n", 
		       Scheduler::instance().clock(),mac->index_, MU(slottime),MU(rtime_[pri]),rtime_[pri]/slottime,floor(rtime_[pri]/slottime));
		rtime_[pri] = ceil(rtime_[pri]/slottime)*slottime;
	} else {
		if(BDEBUG==1) printf("3 now %4.8f Mac: %d round_time slot-duration: %2.2f rtime: %2.2f r/s %f ceil %f \n", 
		       Scheduler::instance().clock(),mac->index_, MU(slottime),MU(rtime_[pri]),rtime_[pri]/slottime, ceil(rtime_[pri]/slottime));
		rtime_[pri] = floor(rtime_[pri]/slottime)*slottime;
	}
	if(BDEBUG==1) printf("4 now %4.8f Mac: %d round_time slot-duration: %2.2f us remainder: %2.2f us slots %2.2f \n", 
	       Scheduler::instance().clock(),mac->index_,MU(slottime),MU(rmd), rtime_[pri]/slottime);
}

void
BackoffTimer_802_11e::handle(Event *)
{
	if(BDEBUG>2) printf("now %4.8f Mac: %d begin of BackoffTimer::handle\n",
			   Scheduler::instance().clock(), mac->index_);
	Scheduler &s = Scheduler::instance();
	paused_ = 0;
	double delay = INF;
	int prio = MAX_PRI + 1;
	
	for(int pri = 0; pri < MAX_PRI; pri++){
		
		double delay_ = rtime_[pri] + AIFSwait_[pri];
		if((delay_ < delay) && backoff_[pri] && !rounding(delay,delay_)) {
			delay = delay_;
			prio = pri;
		}
	}
	
	if(!EDCA && !rounding(s.clock(), stime_[prio] + rtime_[prio] + AIFSwait_[prio])){
	       	printf("now %4.8f Mac: %d BackoffTimer::handle but no priority matches ?! stime_[%d] %2.8f rtime_[%d] %2.2f AIFSwait_[%d] %2.2f \n",
		       s.clock(), mac->index_, prio, stime_[prio], prio, MU(rtime_[prio]), prio, MU(AIFSwait_[prio]));
		exit(1);
	}
	if(prio < MAX_PRI + 1) {
			busy_ = 0;
		        stime_[prio] = 0;
			rtime_[prio] = 0;
			backoff_[prio] = 0;
			AIFSwait_[prio] = 0.0;
			decremented_[prio]=0;
		//mac->backoffHandler(prio); now done further down at the end of Handler!	
	} else {
		cout<<"ERROR: wrong priority in BackoffTimer::handler()";
		exit(0);
	}
	
	busy_ = 0;
	bool another=0;

	for(int pri = 0; pri < MAX_PRI; pri++){
		if(backoff_[pri]) { //check if there is another backoff process
			
			if(rounding(rtime_[pri] + AIFSwait_[pri],delay)) {
				// check if other priority is not a postbackoff, 
				// i.e., packet to tx is available
				if(mac->pktTx_[pri]) {
					mac->inc_cw(pri);
					if(NO_RTX_INC) {
						AIFSwait_[pri] = 0;
						stime_[pri] = s.clock(); //Start-Time
						rtime_[pri] = (Random::random() % (mac->getCW(pri) + 1)) * slottime; 
						backoff_[pri] = 1;
						another=1;
					} else {
						if(mac->inc_retryCounter(pri)) {
							// maximum retry limit exceeded,
							// deletion of packet done in inc_retryCounter(),
							// now reset Backoff variables
							stime_[pri] = 0;
							rtime_[pri] = 0;
							backoff_[pri] = 0;
							AIFSwait_[pri] = 0.0;
						} else {
							AIFSwait_[pri] = 0;
							stime_[pri] = s.clock(); //Start-Time
							rtime_[pri] = (Random::random() % (mac->getCW(pri) + 1)) * slottime; 
							backoff_[pri] = 1;
							another=1;
						}
					}
				} else {
					// end of postbackoff: reset stime_, rtime_, ...
					stime_[pri] = 0;
					rtime_[pri] = 0;
					backoff_[pri] = 0;
					AIFSwait_[pri] = 0.0;
				}
			} else
				another=1;
		}
	}	
        if(another) busy_=1;

	if(busy_ && !paused_){
		if(BDEBUG>2) printf("now %4.8f Mac: %d BackoffTimer::handle calling pause and restart\n",
				    Scheduler::instance().clock(), mac->index_);
		pause(); //pause + restart because the finished backoff could have been a postbackoff!
		restart();
	}

	mac->backoffHandler(prio);	
	if(BDEBUG>2) printf("now %4.8f Mac: %d end of BackoffTimer::handle\n",
			   Scheduler::instance().clock(), mac->index_);
}

void
BackoffTimer_802_11e::start(int pri, int cw, int idle)
{
	if(BDEBUG>2) printf("now %4.8f Mac: %d in BackoffTimer::start for pri %d busy_ %d \n",
			    Scheduler::instance().clock(), mac->index_,pri, busy_);

	Scheduler &s = Scheduler::instance();
	
	if(busy_) { //already a backoff running!
		stime_[pri] = s.clock(); //Start-Time
		rtime_[pri] = (Random::random() % (cw + 1)) * slottime;
		AIFSwait_[pri] = 0.0;
		decremented_[pri]=0;
		if(BDEBUG>2)printf("now: %4.8f Mac: %d starting backoff during others: setting AIFS_[%d] to zero\n",
		       s.clock(), mac->index_, pri);
		backoff_[pri] = 1;
		if(idle == 0){
			if(!paused_){
				pause();
			}
		}
		else {
			assert(rtime_[pri] >= 0.0);
			if(!paused_) {
				pause();
				AIFSwait_[pri] = mac->getAIFS(pri); 
				//cout<<"Mac "<<mac->index_<<": now: "<<Scheduler::instance().clock()<<"pause and restart for prio "<<pri<<"\n";
				restart();
			}
		}
		if(BDEBUG>2) printf("now %4.8f Mac: %d end of BackoffTimer::start stime_[%d] %4.8f rtime_[%d] %2.2f AIFSwait_[%d] %2.2f\n",
				    Scheduler::instance().clock(), mac->index_, pri, stime_[pri], pri, MU(rtime_[pri]), pri, MU(AIFSwait_[pri]));
	} else {
		backoff_[pri] = 1;
		busy_ = 1;
		stime_[pri] = s.clock(); //Start-Time
		rtime_[pri] = (Random::random() % (cw + 1)) * slottime;

		AIFSwait_[pri] = mac->getAIFS(pri);  

		if(idle == 0){
			paused_ = 1;
		}
		else {
			assert(rtime_[pri] >= 0.0);
			s.schedule(this, &intr, rtime_[pri] + AIFSwait_[pri]);
		}
		if(BDEBUG>2) printf("now %4.8f Mac: %d end of BackoffTimer::start, timer scheduled stime_[%d] %4.8f rtime_[%d] %2.8f AIFSwait_[%d] %2.2f \n",
				    Scheduler::instance().clock(), mac->index_, pri, stime_[pri], pri, MU(rtime_[pri]), pri, MU(AIFSwait_[pri]));
	}
}
   
inline bool BackoffTimer_802_11e::rounding(double x, double y)
{
	if(BDEBUG>2) printf("now %4.8f Mac: %d in BackoffTimer::rounding\n",
			   Scheduler::instance().clock(), mac->index_);
	/*
	 * check whether x is within y +/- 1e-12 
	 */
	if(x > y && x < y + ROUND )
		return 1;
	else if(x < y && x > y - ROUND )
		return 1;
	else if (x == y)
		return 1;
	else 
		return 0;
}

void
BackoffTimer_802_11e::pause()
{
	Scheduler &s = Scheduler::instance();
	//the caculation below make validation pass for linux though it
	// looks dummy

	for (int pri = 0; pri < MAX_PRI; pri++) {
		if(backoff_[pri] && !rounding(stime_[pri],s.clock()) && !rounding(decremented_[pri],s.clock())) {
			double st = s.clock();            //now
			double rt = stime_[pri] + AIFSwait_[pri]; // start-Time of backoff + waiting time
			double sr = st - rt; // is < 0,  if stime is back for less than AIFSwait, thus a slot 
			                     // decrement must not appear
		
			int slots =0;
		
			if(BDEBUG>2) printf("now %4.8f Mac: %d BackoffTimer::pause beginning stime_[%d] %4.8f rtime_[%d] %2.2f AIFSwait[%d] %2.2f slottime %2.2f diff/slottime %2.2f \n",
					    s.clock(), mac->index_, pri, stime_[pri], pri, MU(rtime_[pri]), pri, MU(AIFSwait_[pri]),MU(slottime), sr/slottime);
			if(rounding(sr,0.0)){ // now - stime is equal to AIFSWAIT
				// include EDCA rule: slot decrement due to full AIFS period
				if(EDCA && (rtime_[pri] > slottime) ) {
					rtime_[pri] -= slottime;
					/* P802.11e/D13.0
					 * Section 9.9.1.3:
					 * one and only one of the following actions is allowed at slot boundaries:
					 * - decrement of backoff timer, or
					 * - initiate transmission, or
					 * - backoff procedure due to internal collision, or
					 * - do nothing.
					 * Thus we need to assure that a station does not initiate a transmission 
					 * immediately after decreasing rtime.The check is done in restart()/resume() 
					 * by comparing the time of decrement and simulated time.
					 */
					decremented_[pri]=st; // time of decrement 
				} else if (!rounding(stime_[pri],st)){ 
					// this backoff has just been started in this moment, while others are busy,
					// do nothing
					if(BDEBUG>2) printf("now %4.8f Mac: %d BackoffTimer::pause new EDCA rule stime_[%d] %4.8f rtime_[%d] %2.2f AIFSwait[%d] %2.2f slottime %2.2f diff/slottime %2.2f \n",
							    s.clock(), mac->index_, pri, stime_[pri], pri, MU(rtime_[pri]), pri, MU(AIFSwait_[pri]),MU(slottime), sr/slottime); 

				} else {
					if(BDEBUG>2) printf("now %4.8f Mac: %d BackoffTimer::pause new EDCA rule, but rtime < slottime! stime_[%d] %4.8f rtime_[%d] %2.2f AIFSwait[%d] %2.2f slottime %2.2f diff/slottime %2.2f\n",
							    s.clock(), mac->index_, pri, stime_[pri], pri, MU(rtime_[pri]), pri, MU(AIFSwait_[pri]),MU(slottime), sr/slottime); 
					exit(1);
				}
			} else if(sr > 0 + ROUND) {
				slots = int (floor((sr + ROUND)/slottime)); 
			}

			assert(busy_ && !paused_);
			if( (rtime_[pri] - (slots * slottime) > 0.0) || (rtime_[pri] - (slots * slottime) > ROUND) ) {
				if(EDCA)rtime_[pri] -= ((slots + 1) * slottime); // +1 slot for new EDCA rule 
				else rtime_[pri] -= (slots * slottime); 
				decremented_[pri]=st;
				assert(rtime_[pri] >= 0.0);	
			} else{
				if(rounding(rtime_[pri] - (slots * slottime),0.0)) { // difference within rounding errors 
					rtime_[pri] = 0;
					decremented_[pri]=st;
				} else {
					printf("ERROR in BackoffTimer::pause(), rtime_[%d]  %2.4f sr %2.4f slots: %d, SlotTime: %2.4f slots*slottime %2.4f \n", 
					       pri, MU(rtime_[pri]), MU(sr), slots, slottime, MU(slots*slottime));
					exit(0);
				}	
			}
			/*
			 * decrease of AIFSwait is required because pause() and restart() can
			 * be called immediately afterwards (in case of postbackoff), so that
			 * normal backoff operation must proceed
			 */
			if(st - stime_[pri] >= mac->getAIFS(pri)) AIFSwait_[pri] = 0.0;
			else{
				AIFSwait_[pri] -= st - stime_[pri];
				if(AIFSwait_[pri] < 0) AIFSwait_[pri] = 0;
			}
			if(BDEBUG>2) printf("now %4.8f Mac: %d BackoffTimer::pause end stime_[%d] %4.8f rtime_[%d] %2.2f AIFSwait[%d] %2.2f slottime %2.2f diff/slottime %2.2f \n",
					    s.clock(), mac->index_,pri, stime_[pri], pri, MU(rtime_[pri]), pri, MU(AIFSwait_[pri]),MU(slottime), sr/slottime);
		}
	}
	s.cancel(&intr);
	paused_ = 1;
}


void
BackoffTimer_802_11e::resume()
{
	if(BDEBUG>2) printf("now %4.8f Mac: %d in BackoffTimer::resume\n",
			   Scheduler::instance().clock(), mac->index_);
	double delay = INF;
	int prio = MAX_PRI + 1;
	Scheduler &s = Scheduler::instance();
	
	for(int pri = 0; pri < MAX_PRI; pri++){
		if(backoff_[pri]){
			double delay_=0;
			round_time(pri);
			AIFSwait_[pri] = mac->getAIFS(pri);
			stime_[pri] = s.clock();
			if(EDCA && rounding(decremented_[pri],s.clock())) delay_ = rtime_[pri] + AIFSwait_[pri] + slottime;
			else delay_ = rtime_[pri] + AIFSwait_[pri];
			//decremented_[pri]=0;
			if((delay_ < delay) && backoff_[pri]) {
				delay = delay_;
				prio = pri;
			}
			if(BDEBUG>2) printf("now %4.8f Mac: %d BackoffTimer::resume check for smallest delay stime_[%d] %4.8f rtime_[%d] %2.2f AIFSwait[%d] %2.2f slottime %2.2f \n",
					    s.clock(), mac->index_, pri, stime_[pri], pri, MU(rtime_[pri]), pri, MU(AIFSwait_[pri]),MU(slottime));
		}
	}
	if(prio < MAX_PRI + 1) {
		assert(rtime_[prio] + AIFSwait_[prio] >=0);
		s.schedule(this, &intr, rtime_[prio] + AIFSwait_[prio]);
		paused_ = 0;
	} else {
		cout<<"ERROR: wrong priority in BackoffTimer::resume() \n";
		exit(0);
	}
	if(BDEBUG>2) printf("now %4.8f Mac: %d BackoffTimer::resume next: prio %d stime_[%d] %4.8f rtime_[%d] %2.2f AIFSwait[%d] %2.2f slottime %2.2f \n",
			    s.clock(), mac->index_,prio, prio, stime_[prio], prio, MU(rtime_[prio]), prio, MU(AIFSwait_[prio]),MU(slottime));
}

void
BackoffTimer_802_11e::restart()
{
	if(BDEBUG>2) printf("now %4.8f Mac: %d in BackoffTimer::restart\n",
			   Scheduler::instance().clock(), mac->index_);
	busy_ = 1;
	double delay = INF;
	int prio = MAX_PRI + 1;
	Scheduler &s = Scheduler::instance();
	
	for(int pri = 0; pri < MAX_PRI; pri++){
		if(backoff_[pri]) {
			double delay_=0;
			round_time(pri);
			stime_[pri] = s.clock();
			if(EDCA && rounding(decremented_[pri],s.clock())) delay_ = rtime_[pri] + AIFSwait_[pri] + slottime;
			else delay_ = rtime_[pri] + AIFSwait_[pri];
			//decremented_[pri]=0;
			if(delay_ < delay) {
				delay = delay_;
				prio = pri;
			}
		}
	}
	if(prio < MAX_PRI + 1) {
		assert(rtime_[prio] + AIFSwait_[prio] >=0);
		s.schedule(this, &intr, rtime_[prio] + AIFSwait_[prio]);
		paused_ = 0;
	} else {
		cout<<"ERROR: wrong priority in BackoffTimer::restart() \n";
		exit(0);
	}
}


int
BackoffTimer_802_11e::backoff(int pri)
{
	return backoff_[pri];
}

/*
 * Timer for throughput measurement 
 */ 
void AkaroaTimer::start()
{
	Scheduler &s = Scheduler::instance();
	s.schedule(this, &intr,mac->interval_);
}

void AkaroaTimer::handle(Event *)
{
	mac->calc_throughput();
}
