# proc priority is called in ns-mobilenode_802_11e.tcl if interface-queue 
# (in the run-script) is set to Queue/DTail/PriQ.
#
# here the different backoff-priority parameters may  be set for each PriQ
# syntax: $queue Prio(rity) [0..3] PF/AIFS/CW_MIN [..]
#
# TXOPLimit values (in seconds) for 802.11b are taken from the 802.11e  version 13 draft,
# activation of CFB in ns-2.x/tcl/lan/ns-mac.tcl by setting cfb_ to 1.

# ATTENTION: after editing, run make once again!

# 802.11b parameters (default EDCA parameter set), aCWmin=31, aCWmax=1023
proc priority { ifq_name } {
   upvar $ifq_name ifq
    
    # parameters for Queue 0
    $ifq Prio 0 PF 2
    $ifq Prio 0 AIFS 2
    $ifq Prio 0 CW_MIN 7           ;# (aCWmin+1)/4 - 1 
    $ifq Prio 0 CW_MAX 15          ;# (aCWmin+1)/2 - 1 
    $ifq Prio 0 TXOPLimit 0.003264
    
    #parameters for Queue 1
    $ifq Prio 1 PF 2
    $ifq Prio 1 AIFS 2
    $ifq Prio 1 CW_MIN 15          ;# (aCWmin+1)/2 - 1 
    $ifq Prio 1 CW_MAX 31          ;# aCWmin
    $ifq Prio 1 TXOPLimit 0.006016

    #parameters for Queue 2
    $ifq Prio 2 PF 2
    $ifq Prio 2 AIFS 3
    $ifq Prio 2 CW_MIN 31         ;# aCWmin
    $ifq Prio 2 CW_MAX 1023       ;# aCWmax
    $ifq Prio 2 TXOPLimit 0
       
    #parameters for Queue 3
    $ifq Prio 3 PF 2
    $ifq Prio 3 AIFS 7
    $ifq Prio 3 CW_MIN 31         ;# aCWmin
    $ifq Prio 3 CW_MAX 1023       ;# aCWmax
    $ifq Prio 3 TXOPLimit 0
}
