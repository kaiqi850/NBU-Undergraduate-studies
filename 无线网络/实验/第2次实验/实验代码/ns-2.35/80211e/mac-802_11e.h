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

#ifndef ns_mac_80211e_h
#define ns_mac_80211e_h

#include "priq.h"
#include "mac-timers_802_11e.h"
#include "mac/mac-802_11.h"
#include "marshall.h"
//#include "iostream.h"

#define DEBUG 0
#define MAX_PRI 4 //max number of priority queues

#define GET_ETHER_TYPE(x)		GET2BYTE((x))
#define SET_ETHER_TYPE(x,y)            {u_int16_t t = (y); STORE2BYTE(x,&t);}
#define LEVEL(p) HDR_IP(p)->prio()

/* ======================================================================
   Frame Formats
   ====================================================================== */
/* 
#define	MAC_ProtocolVersion	0x00

#define MAC_Type_Management	0x00
#define MAC_Type_Control	0x01
#define MAC_Type_Data		0x02
#define MAC_Type_Reserved	0x03

#define MAC_Subtype_RTS		0x0B
#define MAC_Subtype_CTS		0x0C
#define MAC_Subtype_ACK		0x0D
#define MAC_Subtype_Data	0x00
*/

/*
struct frame_control {
	u_char		fc_subtype		: 4;
	u_char		fc_type			: 2;
	u_char		fc_protocol_version	: 2;

	u_char		fc_order		: 1;
	u_char		fc_wep			: 1;
	u_char		fc_more_data		: 1;
	u_char		fc_pwr_mgt		: 1;
	u_char		fc_retry		: 1;
	u_char		fc_more_frag		: 1;
	u_char		fc_from_ds		: 1;
	u_char		fc_to_ds		: 1;
};

struct rts_frame {
	struct frame_control	rf_fc;
	u_int16_t		rf_duration;
	u_char			rf_ra[ETHER_ADDR_LEN];
	u_char			rf_ta[ETHER_ADDR_LEN];
	u_char			rf_fcs[ETHER_FCS_LEN];
};

struct cts_frame {
	struct frame_control	cf_fc;
	u_int16_t		cf_duration;
	u_char			cf_ra[ETHER_ADDR_LEN];
	u_char			cf_fcs[ETHER_FCS_LEN];
};

struct ack_frame {
	struct frame_control	af_fc;
	u_int16_t		af_duration;
	u_char			af_ra[ETHER_ADDR_LEN];
	u_char			af_fcs[ETHER_FCS_LEN];
};
*/
struct QoS_control {
	u_char		tid		: 4;
	u_char		eosp	       	: 1;
	u_char		ack_policy	: 2;

	u_char		reserved	: 1;
	u_char		txop_qs		: 8;
};

// XXX This header does not have its header access function because it shares
// the same header space with hdr_mac.
struct hdr_mac802_11e {
	struct frame_control	dh_fc;
	u_int16_t		dh_duration;
	u_char			dh_da[ETHER_ADDR_LEN];
	u_char			dh_sa[ETHER_ADDR_LEN];
	u_char			dh_bssid[ETHER_ADDR_LEN];
	u_int16_t		dh_scontrol;
//	u_char			dh_addr4[ETHER_ADDR_LEN];
	struct QoS_control      dh_qos;
	u_char			dh_body[0]; // XXX Non-ANSI
};

/* ======================================================================
   Definitions
   ====================================================================== */

#define DSSS_EDCA_MaxPropagationDelay        0.000002        // 2us   XXXX

class EDCA_PHY_MIB {
  friend class Mac802_11e;
public:
  EDCA_PHY_MIB(Mac802_11e *parent);       
 
  inline double getSlotTime() { return(SlotTime); }
  inline double getSIFS() { return(SIFSTime); }
  inline double getPIFS() { return(SIFSTime + SlotTime); }
  inline double getDIFS() { return(SIFSTime + 2 * SlotTime); }
  inline double getEIFS() {
    // see (802.11-1999, 9.2.10)
    //return(SIFSTime + getDIFS()
    //       + (8 *  getACKlen())/PLCPDataRate);
    // wiethoelter: at end of EIFS, DIFS is scheduled separately
    return(SIFSTime + (8 *  getACKlen())/PLCPDataRate);
  }
  inline u_int32_t getPreambleLength() { return(PreambleLength); }
  inline double getPLCPDataRate() { return(PLCPDataRate); }
  
  inline u_int32_t getPLCPhdrLen() {
    return((PreambleLength + PLCPHeaderLength) >> 3);
  }

  inline u_int32_t getHdrLen11() {
    return(getPLCPhdrLen() + sizeof(struct hdr_mac802_11e)
	   + ETHER_FCS_LEN);
  }
  
  inline u_int32_t getRTSlen() {
    return(getPLCPhdrLen() + sizeof(struct rts_frame));
  }
  
  inline u_int32_t getCTSlen() {
    return(getPLCPhdrLen() + sizeof(struct cts_frame));
  }
        
  inline u_int32_t getACKlen() {
    return(getPLCPhdrLen() + sizeof(struct ack_frame));
  }

private:
  double          SlotTime;
  double          SIFSTime;
  u_int32_t       PreambleLength;
  u_int32_t       PLCPHeaderLength;
  double          PLCPDataRate;
};


class EDCA_MAC_MIB {
  friend class Mac802_11e;
  
 public:
  EDCA_MAC_MIB(Mac802_11e *parent);

 private:
  u_int32_t       RTSThreshold;
  u_int32_t       ShortRetryLimit;
  u_int32_t       LongRetryLimit;

 public:
  u_int32_t       FailedCount;    
  u_int32_t       RTSFailureCount;
  u_int32_t       ACKFailureCount;
 
 public:
  inline u_int32_t getRTSThreshold() { return(RTSThreshold);}
  inline u_int32_t getShortRetryLimit() { return(ShortRetryLimit);}
  inline u_int32_t getLongRetryLimit() { return(LongRetryLimit);}
};

/* ======================================================================
   The actual 802.11e MAC class.
   ====================================================================== */
class Mac802_11e : public Mac {
	friend class DeferTimer_802_11e;
	friend class SIFSTimer_802_11e;
	friend class BackoffTimer_802_11e;
	friend class IFTimer_802_11e;
	friend class NavTimer_802_11e;
	friend class RxTimer_802_11e;
	friend class TxTimer_802_11e;
	friend class AkaroaTimer; 

public:
	Mac802_11e();
	void		recv(Packet *p, Handler *h);
	inline int	hdr_dst(char* hdr, int dst = -2);
	inline int	hdr_src(char* hdr, int src = -2);
	inline int	hdr_type(char* hdr, u_int16_t type = 0);
	void setQ(PriQ* priqueue);	
	PriQ* queue_;  // for pointer to Queues in priq.cc
	double     getAIFS(int pri);
	void       defer_stop(int pri);
	void       calc_throughput();
	double     idle_time;
 protected:
	inline void transmit(Packet *p, double t);
	inline void set_rx_state(MacState x);
	inline void set_tx_state(int pri, MacState x);
	void	backoffHandler(int pri);
	void	deferHandler(int pri);
	void	navHandler(void);
	void	recvHandler(void);
	void	sendHandler(void);
	void	txHandler(void);
        // methods for priority-parameters
	int     getCW(int level);
	double interval_;

private:
	int   	command(int argc, const char*const* argv);
	void check_backoff_timer();
	bool     AIFSset;
	bool     CWset;
	int     cw_[MAX_PRI];
	int     cwmin_[MAX_PRI];
	int     cwmax_[MAX_PRI];
	double  txop_limit_[MAX_PRI];
	Handler*  callback_[MAX_PRI];
        
        /*
	 * Called by the timers.
	 */
	void		recv_timer(void);
	void		send_timer(void);
	int		check_pktCTRL(int pri);
	int		check_pktRTS(int pri);
	int		check_pktTx(int pri);
	int             levels;
	int             slotnum;
	double          aifs_[MAX_PRI];
	Packet*          packets_[MAX_PRI];
        
        /*
	 * Packet Transmission Functions.
	 */
	void	send(Packet *p, Handler *h);
	void 	sendRTS(int pri, int dst);
	void	sendCTS(int pri, int dst, double duration);
	void	sendACK(int pri, int dst);
	void	sendDATA(int pri, Packet *p);
	void	RetransmitRTS(int pri);
	void	RetransmitDATA(int pri);

	/*
	 * Packet Reception Functions.
	 */
	void	recvRTS(Packet *p);
	void	recvCTS(Packet *p);
	void	recvACK(Packet *p);
	void	recvDATA(Packet *p);

	void		capture(Packet *p);
	void		collision(Packet *p);
	void		discard(Packet *p, const char* why);
	void		rx_resume(void);
	void		tx_resume(void);

	inline int	is_idle(void);
	
	/*
	 * Debugging Functions.
	 */
	void		trace_pkt(Packet *p);
	void		dump(char* fname);

	inline int initialized() {
	    	return (cache_ && logtarget_ && Mac::initialized());
	}
	void mac_log(Packet *p) {
		logtarget_->recv(p, (Handler*) 0);
	}
	double txtime(Packet *p);
	double txtime(double psz, double drt);
	double txtime(int bytes) { /* clobber inherited txtime() */ abort(); }

	inline void inc_cw(int level) {
	    //get persistence factor
	    pf = queue_->pri_[level].getPF();
	    cw_old = cw_[level];
	    //calculate new cw_[pri] 
	    cw_[level] = ((cw_old + 1) * pf) - 1;
	    if(cw_[level] > cwmax_[level]) cw_[level] = cwmax_[level];
	}
	inline void rst_cw(int level) { 
               cw_[level] = cwmin_[level]; 
        }

	inline double sec(double t) { return(t *= 1.0e-6); }
	inline u_int16_t usec(double t) {
		u_int16_t us = (u_int16_t)floor((t *= 1e6) + 0.5);
		/* u_int16_t us = (u_int16_t)rint(t *= 1e6); */
		return us;
	}
	inline void set_nav(u_int16_t us) {
		double now = Scheduler::instance().clock();
		double t = us * 1e-6;

		if((now + t) > nav_) {
			nav_ = now + t;
			if(mhNav_.busy()){
				mhNav_.stop();
				
			}
			mhNav_.start(t);
		}
	}

	inline void reset_eifs_nav();
	bool inc_retryCounter(int pri);	    

protected:
	EDCA_PHY_MIB phymib_;
	EDCA_MAC_MIB macmib_;

private:
	double          eifs_nav_;
	double		basicRate_;
 	double		dataRate_;
	int             numbytes_[MAX_PRI]; // for Akaroa Observation
	double start_handle_[MAX_PRI]; // for delay investigation
	double          throughput;
	double          jitter;
	int             rtx_[MAX_PRI];
        int    pf;
	int cw_old;

	/*
	 * Contention Free Burst
	 */
	int     cfb_;
	int     cfb_broadcast;
	double  cfb_dur; 
	int     cfb_active;
	void    cfb(int pri);

	/*
	 * Mac Timers
	 */
	IFTimer_802_11e		mhIF_;          	// interface timer
	NavTimer_802_11e	mhNav_;		        // NAV timer
	RxTimer_802_11e		mhRecv_;		// incoming packets
	TxTimer_802_11e 	mhSend_;         	// outgoing packets

	DeferTimer_802_11e	mhDefer_;       	// defer timer
	SIFSTimer_802_11e       mhSifs_;                // defer timer for sifs, not stoppable!
	BackoffTimer_802_11e	mhBackoff_;	        // backoff timer
	AkaroaTimer             AK;
	/* ============================================================
	   Internal MAC State
	   ============================================================ */
	double		nav_;		// Network Allocation Vector

	MacState	rx_state_;	// incoming state (MAC_RECV or MAC_IDLE)
	MacState	tx_state_[MAX_PRI];	// outgoint state
	int		tx_active_;          	// transmitter is ACTIVE
	int		sending;          	// transmitter is ACTIVE
	Packet		*pktRTS_[MAX_PRI];	// outgoing RTS packet
	Packet		*pktCTRL_[MAX_PRI];	// outgoing non-RTS packet
        Packet          *pktTx_[MAX_PRI];
	//u_int32_t	cw_;		 // Contention Window
	u_int32_t	ssrc_[MAX_PRI];  // STA Short Retry Count
	u_int32_t	slrc_[MAX_PRI];  // STA Long Retry Count
	double		sifs_;		 // Short Interface Space
	double		pifs_;		 // PCF Interframe Space
	double		difs_;		 // DCF Interframe Space
	double		eifs_;  // Extended Interframe Space
	
        //double		tx_sifs_;
	//double		tx_pifs_;
	//double		tx_difs_;

	//int		min_frame_len_;

	NsObject*	logtarget_;

	/* ============================================================
	   Duplicate Detection state
	   ============================================================ */
	u_int16_t	sta_seqno_;	// next seqno that I'll use
	int		cache_node_count_;
	Host		*cache_;
};
#endif /* __mac_80211e_h__ */

