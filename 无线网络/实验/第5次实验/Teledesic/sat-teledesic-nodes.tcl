

if {![info exists ns]} {
	puts "Error: sat-teledesic-nodes.tcl is a supporting script for the "
	puts "       sat-teledesic.tcl script-- run `sat-teledesic.tcl' instead"
	exit
}

for {set a 1} {$a <= 12} {incr a} {
	for {set i [expr $a * 100]} {$i < [expr $a * 100 + 24]} {incr i} {
		if {$a % 2} {
			set stagger 0
		} else { 
			set stagger 7.5 
		}
		set imod [expr $i % 100]
		set n($i) [$ns node]
		$n($i) set-position $alt $inc [expr 15 * ($a - 1)] \
		    [expr $stagger + $imod * 15] $a 
	}
}
for {set a 1} {$a <= 12} {incr a} {
	for {set i [expr $a * 100]} {$i < [expr $a * 100 + 24]} {incr i} {
		if {$i % 100} {
			set next [expr $i - 1]
		} else {
			set next [expr $a * 100 + 23]
		}	
		$n($i) set_next $n($next)
	}
}

