#===================================
#     Simulation parameters setup
#===================================
set val(chan)   Channel/WirelessChannel    ;# channel type
set val(prop)   Propagation/TwoRayGround   ;# radio-propagation model
set val(netif)  Phy/WirelessPhy            ;# network interface type
set val(mac)    Mac/802_11e                 ;# MAC type
set val(ifq)    Queue/DTail/PriQ           ;# interface queue type
set val(ll)     LL                         ;# link layer type
set val(ant)    Antenna/OmniAntenna        ;# antenna model
set val(ifqlen) 50                         ;# max packet in ifq
set val(nn)     14                         ;# number of mobilenodes
set val(rp)     DSDV                       ;# routing protocol
set val(x)      1095                      ;# X dimension of topography
set val(y)      600                      ;# Y dimension of topography
set val(stop)   101.0                         ;# time of simulation end

#
# Initialize the SharedMedia interface with parameters to make
# it work like the 914MHz Lucent WaveLAN DSSS radio interface
#
Phy/WirelessPhy set CPThresh_ 10.0 ;# Capture threshold (db)
Phy/WirelessPhy set CSThresh_ 1.559e-11 ;# Carrier sense threshold(W)
#200m 8.91754e-10
#300m 1.76149e-10
#
#
Phy/WirelessPhy set RXThresh_ 1.76149e-10;# Receive power threshold(W)
Phy/WirelessPhy set Rb_ 2*1e6 ;# Bandwidth
Phy/WirelessPhy set Pt_ 0.2818 ;# Transmission power (W)
Phy/WirelessPhy set freq_ 914e6 ;# frequency
Phy/WirelessPhy set L_ 1.0 ;# system loss factor
#
# unity gain, omni-directional antennas
# set up the antennas to be centered in the node and 1.5 meters above it
#
Antenna/OmniAntenna set X_ 0
Antenna/OmniAntenna set Y_ 0
Antenna/OmniAntenna set Z_ 1.5
Antenna/OmniAntenna set Gt_ 1.0
Antenna/OmniAntenna set Gr_ 1.0
#
#
LL set mindelay_		50us
LL set delay_			25us
LL set bandwidth_		0	;# not used
#
#
#===================================
#        Initialization        
#===================================
#Create a ns simulator
set ns [new Simulator]

#Setup topography object
set topo       [new Topography]
$topo load_flatgrid $val(x) $val(y)
create-god $val(nn)

#Open the NS trace file
set tracefile [open test-802_11e.tr w]
$ns trace-all $tracefile

#Open the NAM trace file
set namfile [open test-802_11e.nam w]
$ns namtrace-all $namfile
$ns namtrace-all-wireless $namfile $val(x) $val(y)
set chan [new $val(chan)];#Create wireless channel

#===================================
#     Mobile node parameter setup
#===================================
$ns node-config -adhocRouting  $val(rp) \
                -llType        $val(ll) \
                -macType       $val(mac) \
                -ifqType       $val(ifq) \
                -ifqLen        $val(ifqlen) \
                -antType       $val(ant) \
                -propType      $val(prop) \
                -phyType       $val(netif) \
                -channel       $chan \
                -topoInstance  $topo \
                -agentTrace    ON \
                -routerTrace   ON \
                -macTrace      ON \
                -movementTrace ON

#===================================
#        Nodes Definition        
#===================================
#Create 14 nodes
set n0 [$ns node]
$n0 set X_ 597
$n0 set Y_ 500
$n0 set Z_ 0.0
$ns initial_node_pos $n0 40
set n1 [$ns node]
$n1 set X_ 501
$n1 set Y_ 402
$n1 set Z_ 0.0
$ns initial_node_pos $n1 40
set n2 [$ns node]
$n2 set X_ 601
$n2 set Y_ 302
$n2 set Z_ 0.0
$ns initial_node_pos $n2 40
set n3 [$ns node]
$n3 set X_ 702
$n3 set Y_ 401
$n3 set Z_ 0.0
$ns initial_node_pos $n3 40
set n4 [$ns node]
$n4 set X_ 797
$n4 set Y_ 499
$n4 set Z_ 0.0
$ns initial_node_pos $n4 40
set n5 [$ns node]
$n5 set X_ 900
$n5 set Y_ 398
$n5 set Z_ 0.0
$ns initial_node_pos $n5 40
set n6 [$ns node]
$n6 set X_ 801
$n6 set Y_ 299
$n6 set Z_ 0.0
$ns initial_node_pos $n6 40
set n7 [$ns node]
$n7 set X_ 396
$n7 set Y_ 298
$n7 set Z_ 0.0
$ns initial_node_pos $n7 40
set n8 [$ns node]
$n8 set X_ 501
$n8 set Y_ 199
$n8 set Z_ 0.0
$ns initial_node_pos $n8 40
set n9 [$ns node]
$n9 set X_ 600
$n9 set Y_ 102
$n9 set Z_ 0.0
$ns initial_node_pos $n9 40
set n10 [$ns node]
$n10 set X_ 698
$n10 set Y_ 200
$n10 set Z_ 0.0
$ns initial_node_pos $n10 40
set n11 [$ns node]
$n11 set X_ 801
$n11 set Y_ 99
$n11 set Z_ 0.0
$ns initial_node_pos $n11 40
set n12 [$ns node]
$n12 set X_ 900
$n12 set Y_ 200
$n12 set Z_ 0.0
$ns initial_node_pos $n12 40
set n13 [$ns node]
$n13 set X_ 995
$n13 set Y_ 300
$n13 set Z_ 0.0
$ns initial_node_pos $n13 40

#===================================
#        Agents Definition        
#===================================
#Setup a TCP connection
set tcp0 [new Agent/TCP]
$ns attach-agent $n7 $tcp0
set sink1 [new Agent/TCPSink]
$ns attach-agent $n13 $sink1
$ns connect $tcp0 $sink1
$tcp0 set packetSize_ 1500

#Setup a UDP connection
set udp2 [new Agent/UDP]
$ns attach-agent $n0 $udp2
set null4 [new Agent/Null]
$ns attach-agent $n9 $null4
$ns connect $udp2 $null4
$udp2 set packetSize_ 1500

#Setup a UDP connection
set udp3 [new Agent/UDP]
$ns attach-agent $n4 $udp3
set null5 [new Agent/Null]
$ns attach-agent $n11 $null5
$ns connect $udp3 $null5
$udp3 set packetSize_ 1500


#===================================
#        Applications Definition        
#===================================
#Setup a FTP Application over TCP connection
set ftp0 [new Application/FTP]
$ftp0 attach-agent $tcp0
$ns at 1.0 "$ftp0 start"
$ns at 100.0 "$ftp0 stop"

#Setup a CBR Application over UDP connection
set cbr1 [new Application/Traffic/CBR]
$cbr1 attach-agent $udp2
$cbr1 set packetSize_ 1000
$cbr1 set rate_ 1.0Mb
$cbr1 set random_ null
$ns at 30.0 "$cbr1 start"
$ns at 100.0 "$cbr1 stop"

#Setup a CBR Application over UDP connection
set cbr2 [new Application/Traffic/CBR]
$cbr2 attach-agent $udp3
$cbr2 set packetSize_ 1000
$cbr2 set rate_ 1.0Mb
$cbr2 set random_ null
$ns at 40.0 "$cbr2 start"
$ns at 100.0 "$cbr2 stop"


#===================================
#        Termination        
#===================================
#Define a 'finish' procedure
proc finish {} {
    global ns tracefile namfile
    $ns flush-trace
    close $tracefile
    close $namfile
    exec nam test-802_11e.nam &
    exit 0
}
for {set i 0} {$i < $val(nn) } { incr i } {
    $ns at $val(stop) "\$n$i reset"
}
$ns at $val(stop) "$ns nam-end-wireless $val(stop)"
$ns at $val(stop) "finish"
$ns at $val(stop) "puts \"done\" ; $ns halt"
$ns run
