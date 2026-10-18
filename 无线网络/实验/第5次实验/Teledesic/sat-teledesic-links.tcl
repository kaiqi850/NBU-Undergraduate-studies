
if {![info exists ns]} {
	puts "Error: sat-teledesic-links.tcl is a supporting script for the "
	puts "       sat-teledesic.tcl script-- run `sat-teledesic.tcl' instead"
	exit
}

for {set a 1} {$a <= 12} {incr a} {
	for {set i [expr $a * 100]} {$i < [expr $a * 100 + 24]} {incr i} {
		set imod [expr $i % 100]
		if {$imod == 23} {
			set next [expr $a * 100]
		} else {
			set next [expr $i + 1]
		}
		if {$imod == 23} {
			set next2 [expr $a * 100 + 1]
		} elseif {$imod == 22} {
			set next2 [expr $a * 100]
		} else {
			set next2 [expr $i + 2]
		}
		$ns add-isl intraplane $n($i) $n($next) $opt(bw_isl) $opt(ifq) $opt(qlim)
		$ns add-isl intraplane $n($i) $n($next2) $opt(bw_isl) $opt(ifq) $opt(qlim)
	}
}

for {set i 100} {$i < 124} {incr i} {
	set next [expr $i + 100]
	$ns add-isl interplane $n($i) $n($next) $opt(bw_isl) $opt(ifq) $opt(qlim)
}

for {set a 3} {$a <= 12} {incr a} {
	for {set i [expr $a * 100]} {$i < [expr $a * 100 + 24]} {incr i} {
		set prev [expr $i - 100]
		set prev2 [expr $i - 200]
		$ns add-isl interplane $n($i) $n($prev) $opt(bw_isl) $opt(ifq) $opt(qlim)
		$ns add-isl interplane $n($i) $n($prev2) $opt(bw_isl) $opt(ifq) $opt(qlim)
	}
}

# Plane 1 <-> Plane 12
for {set i 100} {$i < 112} {incr i} {
	set j [expr 1311 - $i]
	$ns add-isl crossseam $n($i) $n($j) $opt(bw_isl) $opt(ifq) $opt(qlim)
}
for {set i 112} {$i < 124} {incr i} {
	set j [expr 1335 - $i]
	$ns add-isl crossseam $n($i) $n($j) $opt(bw_isl) $opt(ifq) $opt(qlim)
}
