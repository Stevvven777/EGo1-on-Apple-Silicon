`timescale 1ns/1ps
module top #(parameter integer COUNTER_BITS = 26) (
    input wire clk,
    output wire led
);
    reg [COUNTER_BITS-1:0] counter;
    initial counter = 0;
    always @(posedge clk) counter <= counter + 1'b1;
    assign led = counter[COUNTER_BITS-1];
endmodule
