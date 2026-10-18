#讀取使用者設定的參數
proc getopt {argc argv} {
	global opt
        lappend optlist nn
        for {set i 0} {$i < $argc} {incr i} {
		set opt($i) [lindex $argv $i]
	}
}

#1 mapping type (0: 802.11e, 1: static mapping, 2: dynamic mapping); 
#2 number of voice flows (AC_3) ;
#3 number of video flows (AC_2) ; 
#4 number of TCP flows   (AC_1) ; 
#5 number of CBR flows   (AC_0) ;

getopt $argc $argv


set packetSize   1500
set max_fragmented_size   1024

set val(chan)           Channel/WirelessChannel    ;# channel type
set val(prop)           Propagation/TwoRayGround   ;# radio-propagation model
set val(netif)          Phy/WirelessPhy            ;# network interface type
set val(mac)            Mac/802_11e                ;# MAC type
set val(ifq)            Queue/DTail/PriQ    	   ;# interface queue type
set val(ll)             LL                         ;# link layer type
set val(ant)            Antenna/OmniAntenna        ;# antenna model
set val(ifqlen)         50                         ;# max packet in ifq
set val(rp) 		AODV
set opt(choice)    	$opt(0)
set opt(voiceflow)    	$opt(1)
set opt(videoflow) 	$opt(2)
set opt(TCPflow)	$opt(3)
set opt(CBRflow) 	$opt(4)

Mac/802_11e set dataRate_          1.0e6           ;# 1Mbps
Mac/802_11e set basicRate_         1.0e6           ;# 1Mbps

set ns [new Simulator]

set f [open test.tr w]
$ns trace-all $f


# set up topography object
set topo       [new Topography]
$topo load_flatgrid 500 500
 
# Create God
create-god 2

# create channel 
set chan [new $val(chan)]

$ns node-config -adhocRouting $val(rp) \
                -llType $val(ll) \
                -macType $val(mac) \
                -ifqType $val(ifq) \
                -ifqLen $val(ifqlen) \
                -antType $val(ant) \
                -propType $val(prop) \
                -phyType $val(netif) \
                -channel $chan \
                -topoInstance $topo \
                -agentTrace OFF \
                -routerTrace OFF \
                -macTrace OFF \
                -movementTrace OFF 

for {set i 0} {$i < 2} {incr i} {
        set node_($i) [$ns node]
        $node_($i) random-motion 0
}

#MH(0) --> MH(1)  only tow host
$node_(0) set X_ 30.0
$node_(0) set Y_ 30.0
$node_(0) set Z_ 0.0

$node_(1) set X_ 200.0
$node_(1) set Y_ 30.0
$node_(1) set Z_ 0.0

#1st priority traffic (VoIP)
for {set i 0} {$i < $opt(voiceflow) } {incr i} {
	set udpA_($i) [new Agent/UDP]
	$udpA_($i) set prio_ 0
	$ns attach-agent $node_(0) $udpA_($i)
	set nullA_($i) [new Agent/Null]
	$ns attach-agent $node_(1) $nullA_($i)
	$ns connect $udpA_($i) $nullA_($i)

	set voip_($i) [new Application/Traffic/CBR]
	$voip_($i) attach-agent $udpA_($i)
	$voip_($i) set packet_size_ 160
	$voip_($i) set rate_ 64k
	$voip_($i) set random_ false
	$ns at 5.0 "$voip_($i) start"
	$ns at 50.0 "$voip_($i) stop"
}

#2nd priority traffic (Video, Foreman)
for {set i 0} {$i < $opt(videoflow) } {incr i} {
	set udp($i) [new Agent/my_UDP]
	$ns attach-agent $node_(0) $udp($i)
	$udp($i) set packetSize_ $packetSize
	$udp($i) set_filename sd_foreman_$i
	set null($i) [new Agent/myEvalvid_Sink] 
	$ns attach-agent $node_(1) $null($i)
	$ns connect $udp($i) $null($i)
	$null($i) set_filename rd_foreman_$i
	
	set original_file_name($i) foreman_qcif.st
	set trace_file_name($i) video($i).dat
	set original_file_id($i) [open $original_file_name($i) r]
	set trace_file_id($i) [open $trace_file_name($i) w]

	set pre_time 0
	set totalByte_I 0
	set totalByte_P 0
	set totalByte_B 0
	set totalPkt_I 0
	set totalPkt_P 0
	set totalPkt_B 0
	
	while {[eof $original_file_id($i)] == 0} {
	    gets $original_file_id($i) current_line
	     
	    scan $current_line "%d%s%d%d%f" no_ frametype_ length_ tmp1_ tmp2_
	    set time [expr int(($tmp2_ - $pre_time)*1000000.0)]
	          
	    if { $frametype_ == "I" } {
	  	set type_v 1
	  	set prio_p 1
	  	set totalByte_I  [expr int($totalByte_I + $length_)]
	  	set totalPkt_I [expr int($totalPkt_I + $tmp1_)]
	    }	
	
	    if { $frametype_ == "P" } {
	  	set type_v 2
	  	set prio_p 1
	  	set totalByte_P  [expr int($totalByte_P + $length_)] 
	  	 set totalPkt_P [expr int($totalPkt_P + $tmp1_)]
	    }	
	
	    if { $frametype_ == "B" } {
	  	set type_v 3
	  	set prio_p 1
	  	set  totalByte_B  [expr int($totalByte_B + $length_)]
	  	set totalPkt_B [expr int($totalPkt_B + $tmp1_)]
	    }	
	    
	    if { $frametype_ == "H" } {
	  	set type_v 1                          
	  	set prio_p 1
	  	set totalByte_I  [expr int($totalByte_I + $length_)] 
	  	set totalPkt_I [expr int($totalPkt_I + $tmp1_)]
	    }
	
	    puts  $trace_file_id($i) "$time $length_ $type_v $prio_p $max_fragmented_size"
	    set pre_time $tmp2_
	}
	
	set totalPkt  [expr int($totalPkt_I+$totalPkt_P+$totalPkt_B)] 
	set totalByte  [expr int($totalByte_I+$totalByte_P+$totalByte_B)] 
	
	close $original_file_id($i)
	close $trace_file_id($i)
	set end_sim_time $tmp2_
	puts "end_sim_time: $end_sim_time"
	
	set trace_file($i) [new Tracefile]
	$trace_file($i) filename $trace_file_name($i)
	set video($i) [new Application/Traffic/myEvalvid]
	$video($i) attach-agent $udp($i)
	$video($i) attach-tracefile $trace_file($i)
	
	$ns at [expr 10.0 ] "$video($i) start"
	$ns at [expr 50.0] "$video($i) stop"
	$ns at [expr 50.0] "$null($i) closefile"
	$ns at [expr 50.0] "$null($i) printstatus"

}

#3rd priority traffic (CBR)
for {set i 0} {$i < $opt(CBRflow) } {incr i} {
	set udpB_($i) [new Agent/UDP]
	$udpB_($i) set prio_ 2
	$ns attach-agent $node_(0) $udpB_($i)
	set nullB_($i) [new Agent/Null]
	$ns attach-agent $node_(1) $nullB_($i)
	$ns connect $udpB_($i) $nullB_($i)

	set cbr_($i) [new Application/Traffic/CBR]
	$cbr_($i) attach-agent $udpB_($i)
	$cbr_($i) set packet_size_ 200
	$cbr_($i) set rate_ 125k
	$cbr_($i) set random_ false
	$ns at 20.0 "$cbr_($i) start"
	$ns at 35.0 "$cbr_($i) stop"
}


#4th priority traffic (TCP)
for {set i 0} {$i < $opt(TCPflow) } {incr i} {
	set tcp($i) [new Agent/TCP]
	$tcp($i) set prio_ 3
	$ns attach-agent $node_(0) $tcp($i)
	set sink($i) [new Agent/TCPSink]
	$ns attach-agent $node_(1) $sink($i)
	$ns connect $tcp($i) $sink($i)
	set ftp($i) [new Application/FTP]
	$ftp($i) set type_ FTP
	$ftp($i) attach-agent $tcp($i)
	$ns at 15.0 "$ftp($i) start"
	$ns at 30.0 "$ftp($i) stop"
}
 
set n0_ifq [$node_(0) set ifq_(0)]
$n0_ifq set choice $opt(choice)
$n0_ifq set threshold1 10	# low threshold of queue length
$n0_ifq set threshold2 40	# high threshold of queue length
$n0_ifq set prob0 0		# Prob_I
$n0_ifq set prob1 0.6		# Prob_P
$n0_ifq set prob2 0.9		# Prob_B

$ns at 0.0 "record4"

set f4 [open queuelength_choice_$opt(choice)_voice_$opt(voiceflow)_video_$opt(videoflow)_FTP_$opt(TCPflow)_CBR_$opt(CBRflow).txt w]

proc record4 {} {
	global ns n0_ifq f4
        set time 0.01
        set now [$ns now]
        set qlen0 0
        set qlen1 0
        set qlen2 0
        set qlen3 0
	puts $f4 "$now 	[$n0_ifq set qlen0]	[$n0_ifq set qlen1]	[$n0_ifq set qlen2]	[$n0_ifq set qlen3]	"
	$ns at [expr $now+$time] "record4"
}



for {set i 0} {$i < 2} {incr i} {
        $ns initial_node_pos $node_($i) 30
        $ns at 50.0 "$node_($i) reset";
}

$ns at 50.0 "finish"
$ns at 50.1 "puts \"NS EXITING...\"; $ns halt"


#INSERT ANNOTATIONS HERE
proc finish {} {
        global ns f
        $ns flush-trace
        close $f
}

puts "Starting Simulation..."
$ns run


