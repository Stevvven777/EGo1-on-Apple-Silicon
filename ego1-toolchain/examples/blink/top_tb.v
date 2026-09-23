`timescale 1ns/1ps
module top_tb;
    reg clk = 0;
    wire led;
    integer cycle;
    top #(.COUNTER_BITS(4)) dut (.clk(clk), .led(led));
    always #5 clk = ~clk;
    initial begin
        $dumpfile("top.vcd");
        $dumpvars(0, top_tb);
        #1;
        if (led !== 1'b0) $fatal(1, "Initial LED state incorrect");
        for (cycle = 1; cycle <= 32; cycle = cycle + 1) begin
            @(posedge clk);
            #1;
            if (led !== ((cycle / 8) % 2 == 1))
                $fatal(1, "LED mismatch at cycle %0d", cycle);
        end
        $display("PASS: initial state, divider transitions, and counter wrap (32 clocks)");
        $finish;
    end
endmodule
