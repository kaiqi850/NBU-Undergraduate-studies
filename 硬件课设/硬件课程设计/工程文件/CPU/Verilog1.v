`timescale 1ns/1ns

module pwm_tb;
	reg         clk ; 
	reg         rst_n ;
	wire    		led;

    pwm dut(
        .clk(clk),
        .rst_n(rst_n),
		  .led(led)
    );

    initial begin
        #5;
		  rst_n=1;
		  #1;
		  rst_n=0;
		  #1;
		  rst_n=1;
		  #1;
		  clk=1;
		  forever #1 clk = ~clk; // ±÷”
    end
	 
endmodule
