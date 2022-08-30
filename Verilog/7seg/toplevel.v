module toplevel(
  // 25MHz clock input
  input clk,
  // Tile
  output [11:0] tile3
);

 reg [36:0] timer;

 wire [11:0] val = timer[36:25];
 wire [2:0] ca;
 wire  a,b,c,d,e,f,g;
 assign tile3 = {c, 'b1, d, 'b1, b, e, a, f, g, ca};
 

 always @(posedge clk) timer <= timer + 1;
 
 wire [3:0] dig = (ca == 'b011 ? val[3:0] : ca == 'b101 ? val[7:4] : val[11:8]);

 h27seg hex (
   .hex(dig),
   .s7({g, f, e, d, c, b, a})
 );

 seven_seg_display seg7 (
   .clk(clk),
   .ca(ca)
 );

endmodule

