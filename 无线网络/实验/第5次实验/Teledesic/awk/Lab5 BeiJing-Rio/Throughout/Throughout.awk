

BEGIN {flag=0;
	i=0;
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

if(action=="r" && to=="289" && flow_id==0) {
   pkt_size_sum[i+1]=pkt_size_sum[i]+size;
   if(flag==0) {
       start_time=time; 
	flag=1;   
		  }

   end_time[i] = time;
   i++;
							}
}

END {
printf("%.4f\t%.4f\n",end_time[0],0);   
for(j=1;j<i;j++) {
	time=end_time[j]-start_time;
  	th=pkt_size_sum[j]*8/time/1000;
  	printf("%.4f\t%.4f\n", end_time[j],th)
   		   }
printf("%.4f\t%.4f\n",end_time[i-1],0);
}			