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
/* Ported from CMU/Monarch's code, nov'98 -Padma.*/

#ifndef __mac_timers_802_11e_h__
#define __mac_timers_802_11e_h__

#define MAX_PRI 4 
/* ======================================================================
   Timers
   ====================================================================== */
class Mac802_11e;

class MacTimer_802_11e : public Handler {
public:
	MacTimer_802_11e(Mac802_11e* m, double s = 0) : mac(m), slottime(s) {
		busy_ = paused_ = 0; stime = rtime = 0.0;
	}

	virtual void handle(Event *e) = 0;

	virtual void start(double time);
	virtual void stop(void);
	virtual void pause(void) { assert(0); }
	virtual void resume(void) { assert(0); }

	inline int busy(void) { return busy_; } 
	inline int paused(void) { return paused_; }
	inline double expire(void) {
		return ((stime + rtime) - Scheduler::instance().clock());
	}

protected:
	Mac802_11e	*mac;
	int		busy_;
	int		paused_;
	Event		intr;
	double		stime;	// start time
	double		rtime;	// remaining time
	double		slottime;
};


class BackoffTimer_802_11e : public MacTimer_802_11e {
public:
	BackoffTimer_802_11e(Mac802_11e *m, double s) : MacTimer_802_11e(m, s) 
	{
		for (int pri = 0; pri < MAX_PRI; pri++){
			AIFSwait_[pri] = 0.0;
			stime_[pri] = rtime_[pri] = 0;
			backoff_[pri] = 0;
			decremented_[pri] = 0.0;
		}
		levels = 0;
	}

	void	start(int pri, int cw, int idle);
	void	handle(Event *e);
	void	pause(void);
	void	resume();
	int     backoff(int pri);

private:
	inline void round_time(int pri);
	inline bool rounding(double x, double y);
	int     backoff_[MAX_PRI]; //for handler
	void    restart();
	double	AIFSwait_[MAX_PRI];
	double  rtime_[MAX_PRI];
	
	double  stime_[MAX_PRI];
	double  decremented_[MAX_PRI];
	int     levels; // get number of levels out of priq.cc or mac-802_11e.cc
	bool    pause_restart;
};

class DeferTimer_802_11e : public MacTimer_802_11e {
public:
	DeferTimer_802_11e(Mac802_11e *m, double s) : MacTimer_802_11e(m,s) {
		for(int i=0;i<MAX_PRI;i++) {
			defer_[i] = 0;
			rtime_[i] = stime_[i] = 0;
		}
		prio = -1;
	}

	void	start(int pri, double time);
	void    pause(void);
	void    stop(void);
	void	handle(Event *e);
	int     defer(int pri);
private:
	int prio;
	int defer_[MAX_PRI];
 	double rtime_[MAX_PRI];
	double stime_[MAX_PRI];
};

class SIFSTimer_802_11e : public MacTimer_802_11e {
public:
	SIFSTimer_802_11e(Mac802_11e *m, double s) : MacTimer_802_11e(m,s) {
		for(int i=0;i<MAX_PRI;i++) {
			sifs_[i] = 0;
			rtime_[i] = stime_[i] = 0;
		}
		prio = -1;
	}

	void	start(int pri, double time);
	void	handle(Event *e);
private:
	int    prio;
	int    sifs_[MAX_PRI];
	double rtime_[MAX_PRI];
	double stime_[MAX_PRI];
};

class IFTimer_802_11e : public MacTimer_802_11e {
public:
	IFTimer_802_11e(Mac802_11e *m) : MacTimer_802_11e(m) {}
	void	handle(Event *e);
};


class NavTimer_802_11e : public MacTimer_802_11e {
public:
	NavTimer_802_11e(Mac802_11e *m) : MacTimer_802_11e(m) {}

	void	handle(Event *e);
};

class RxTimer_802_11e : public MacTimer_802_11e {
public:
	RxTimer_802_11e(Mac802_11e *m) : MacTimer_802_11e(m) {}

	void	handle(Event *e);
};

class TxTimer_802_11e : public MacTimer_802_11e {
public:
	TxTimer_802_11e(Mac802_11e *m) : MacTimer_802_11e(m) {}

	void	handle(Event *e);
};

class AkaroaTimer : public MacTimer_802_11e {
public:
	AkaroaTimer(Mac802_11e *m) : MacTimer_802_11e(m) {}
	void start();
	void handle(Event *e);
};
	
#endif /* __mac_timers_802_11e_h__ */

