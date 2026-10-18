
BEGIN {
	total=0;
	drop=0;
	}

{	
	action=$1;
	time=$2;
	from=$3;
	to=$4;
	type=$5;
	size=$6;
	flow_id=$8;
	src=$9;
	dst=$10;
	seq_no=$11;
	packet_id=$12;

	if (from ==288 && action =="+")
		total++;
	if (flow_id ==0 && action=="d" )
		drop++;
}

END {
	printf ("number of packets send: %d lost: %d\n",total,drop)
    }