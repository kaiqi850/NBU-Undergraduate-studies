
global ns
set ns [new Simulator]

HandoffManager/Term set elevation_mask_ 8.2
HandoffManager/Term set term_handoff_int_ 10

HandoffManager/Sat set sat_handoff_int_ 10
HandoffManager/Sat set latitude_threshold_ 60 
HandoffManager/Sat set longitude_threshold_ 10 

HandoffManager set handoff_randomization_ true
SatRouteObject set metric_delay_ true
SatRouteObject set data_driven_computation_ true
ns-random 1
Agent set ttl_ 32


global opt
set opt(chan)           Channel/Sat
set opt(bw_down)        1.5Mb
set opt(bw_up)          1.5Mb
set opt(bw_isl)         25Mb
set opt(phy)            Phy/Sat
set opt(mac)            Mac/Sat
set opt(ifq)            Queue/DropTail
set opt(qlim)           50
set opt(ll)             LL/Sat
set opt(wiredRouting) 	OFF

set opt(alt)            780
set opt(inc)            86.4


set outfile [open out.tr w]
$ns trace-all $outfile

$ns node-config -satNodeType polar \
		-llType $opt(ll) \
		-ifqType $opt(ifq) \
		-ifqLen $opt(qlim) \
		-macType $opt(mac) \
		-phyType $opt(phy) \
		-channelType $opt(chan) \
		-downlinkBW $opt(bw_down) \
		-wiredRouting $opt(wiredRouting) 

set alt $opt(alt)
set inc $opt(inc)

source sat-iridium-nodes.tcl
source sat-iridium-links.tcl

$ns node-config -satNodeType terminal
set n100 [$ns node]
$n100 set-position 39.54 116.28; # BeiJing
set n101 [$ns node]
$n101 set-position 31.12 121.26; # ShangHai

$n100 add-gsl polar $opt(ll) $opt(ifq) $opt(qlim) $opt(mac) $opt(bw_up) \
  $opt(phy) [$n0 set downlink_] [$n0 set uplink_]
$n101 add-gsl polar $opt(ll) $opt(ifq) $opt(qlim) $opt(mac) $opt(bw_up) \
  $opt(phy) [$n0 set downlink_] [$n0 set uplink_]

$ns trace-all-satlinks $outfile

set udp0 [new Agent/UDP]
$ns attach-agent $n100 $udp0
set cbr0 [new Application/Traffic/CBR]
$cbr0 attach-agent $udp0
$cbr0 set interval_ 60.01

set null0 [new Agent/Null]
$ns attach-agent $n101 $null0

$ns connect $udp0 $null0
$ns at 1.0 "$cbr0 start"

set satrouteobject_ [new SatRouteObject]
$satrouteobject_ compute_routes

$ns at 86400.0 "finish"

proc finish {} {
	global ns outfile 
	$ns flush-trace
	close $outfile

	exit 0
}

$ns run

