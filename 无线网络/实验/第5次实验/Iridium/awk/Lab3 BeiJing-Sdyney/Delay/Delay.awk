BEGIN {
	highest_packet_id=0;
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

if (packet_id > highest_packet_id) 
	highest_packet_id =packet_id;

if (start_time[packet_id]==0)
	start_time[packet_id] =time;

if(flow_id ==0&&action !="d") 
{
 	if(action=="r"&&to=="67") {
		end_time[packet_id]=time;
			   } 
else
	{end_time[packet_id]=-1;}


}

}

END {
	for (packet_id=0;packet_id <= highest_packet_id;packet_id++) {
			start=start_time[packet_id];
			end=end_time[packet_id];
			delay=end-start;
	if (start < end) printf( "%f %f\n",start,delay)
 }

}