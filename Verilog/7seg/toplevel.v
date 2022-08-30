module toplevel(
  // 25MHz clock input
  input clk,
  // Tile
  output [11:0] tile3
);

// # Tile 3
// set_io -nowarn tile3[0] B1
// set_io -nowarn  tile3[1] B2
// set_io -nowarn  tile3[2] C4
// set_io -nowarn  tile3[3] C3
// set_io -nowarn  tile3[4] C2
// set_io -nowarn  tile3[5] C1
// set_io -nowarn  tile3[6] E1
// set_io -nowarn  tile3[7] D1
// set_io -nowarn  tile3[8] D2
// set_io -nowarn  tile3[9] D3
// set_io -nowarn  tile3[10] E2
// set_io -nowarn  tile3[11] E3

// set_io a C1
// set_io b D1
// set_io c E3
// set_io d D3
// set_io e E1
// set_io f C2
// set_io g C3
// set_io dp D2
// set_io ca[0] C4
// set_io ca[1] B2
// set_io ca[2] B1

 reg [36:0] timer;

 wire [11:0] val = timer[36:25];
 wire [2:0] ca;
 wire  g, f, e, d, c, b, a;
 assign tile3 = {c, 1, d, 1, b, e, a, f, g, ca};
 

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

