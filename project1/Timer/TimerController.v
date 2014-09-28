// By Tim Martin and Lin Dong
// 2014-09-26
module TimerController
(input CLOCK_50,
    input [9:0] SW,
    input [3:0] KEY,
    output [6:0] HEX0,
    output [6:0] HEX1,
    output [6:0] HEX2,
    output [6:0] HEX3,
    output [7:0] LEDG,
    output [9:0] LEDR
);

reg [31:0] clk_counter = 0;
reg [3:0] one_second_counter;
reg [3:0] ten_second_counter;
reg [3:0] one_minute_counter;
reg [3:0] ten_minute_counter;

reg [9:0] one_second_input;
reg [9:0] ten_second_input;
reg [9:0] one_minute_input;
reg [9:0] ten_minute_input;

TFlipFlop move_to_minutes (KEY[0], KEY[1], pressed_key_one);
TFlipFlop start_stop (KEY[0], KEY[2], pressed_key_two);

parameter [2:0] RESET_STATE       = 3'b000;
parameter [2:0] SET_SECONDS_STATE = 3'b001;
parameter [2:0] SET_MINUTES_STATE = 3'b010;
parameter [2:0] RUNNING_STATE     = 3'b011;
parameter [2:0] NOT_RUNNING_STATE = 3'b100;
parameter [2:0] LEDR_ON_STATE     = 3'b101;
parameter [2:0] LEDR_OFF_STATE    = 3'b110;
reg [2:0] state = 3'b000;

assign LEDG[2] = state[2];
assign LEDG[1] = state[1];
assign LEDG[0] = state[0];

assign LEDR[0] = (state == LEDR_ON_STATE);
assign LEDR[1] = (state == LEDR_ON_STATE);
assign LEDR[2] = (state == LEDR_ON_STATE);
assign LEDR[3] = (state == LEDR_ON_STATE);
assign LEDR[4] = (state == LEDR_ON_STATE);
assign LEDR[5] = (state == LEDR_ON_STATE);
assign LEDR[6] = (state == LEDR_ON_STATE);
assign LEDR[7] = (state == LEDR_ON_STATE);
assign LEDR[8] = (state == LEDR_ON_STATE);
assign LEDR[9] = (state == LEDR_ON_STATE);

always @(posedge CLOCK_50) begin
    if (!KEY[0]) begin
        state <= RESET_STATE;
    end

    if (state == RESET_STATE) begin
        one_second_counter <= 4'b0;
        ten_second_counter <= 4'b0;
        one_minute_counter <= 4'b0;
        ten_minute_counter <= 4'b0;
        state <= SET_SECONDS_STATE;
    end

    if (state == SET_SECONDS_STATE) begin
        one_second_input = SW[3:0];
        ten_second_input = SW[7:4];

        if (one_second_input >= 9) begin
            one_second_counter <= 4'd9;
        end else begin
            one_second_counter <= one_second_input;
        end

        if (ten_second_input >= 5) begin
            ten_second_counter <= 4'd5;
        end else begin
            ten_second_counter <= ten_second_input;
        end

        if (pressed_key_one) begin
            state <= SET_MINUTES_STATE;
        end
    end

    if (state == SET_MINUTES_STATE) begin
        one_minute_input = SW[3:0];
        ten_minute_input = SW[7:4];

        if (one_minute_input >= 9) begin
            one_minute_counter <= 4'd9;
        end else begin
            one_minute_counter <= one_minute_input;
        end

        if (ten_minute_input >= 5) begin
            ten_minute_counter <= 4'd5;
        end else begin
            ten_minute_counter <= ten_minute_input;
        end

        if (pressed_key_two) begin
            state <= RUNNING_STATE;
        end
    end

    if (state == NOT_RUNNING_STATE) begin
        if (pressed_key_two) begin
            state <= RUNNING_STATE;
        end
    end

    if (state == RUNNING_STATE ) begin
        clk_counter <= clk_counter + 1;
        if (!pressed_key_two) begin
            state <= NOT_RUNNING_STATE;
        end else if (one_second_counter == 0 && ten_second_counter == 0 && one_minute_counter == 0 && ten_minute_counter == 0) begin
            clk_counter <= 0;
            state <= LEDR_ON_STATE;
        end else begin
            if (clk_counter == 50000000) begin
                clk_counter <= 0;
                one_second_counter <= one_second_counter - 1;
                if (one_second_counter == 0) begin
                    one_second_counter <= 9;
                    ten_second_counter <= ten_second_counter - 1;
                    if (ten_second_counter == 0) begin
                        ten_second_counter <= 5;
                        one_minute_counter <= one_minute_counter - 1;
                        if (one_minute_counter == 0) begin
                            one_minute_counter <= 9;
                            ten_minute_counter <= ten_minute_counter - 1;
                        end
                    end
                end
            end
        end
    end

    if (state == LEDR_ON_STATE) begin
        clk_counter <= clk_counter + 1;
        if (clk_counter == 25000000) begin
            clk_counter <= 0;
            state <= LEDR_OFF_STATE;
        end
    end

    if (state == LEDR_OFF_STATE) begin
        clk_counter <= clk_counter + 1;
        if (clk_counter == 25000000) begin
            clk_counter <= 0;
            state <= LEDR_ON_STATE;
        end
    end
end

dec2_7seg u3 (ten_minute_counter, HEX3);
dec2_7seg u2 (one_minute_counter, HEX2);
dec2_7seg u1 (ten_second_counter, HEX1);
dec2_7seg u0 (one_second_counter, HEX0);

endmodule

module TFlipFlop(reset, clk, tOut);
input reset, clk;
output tOut;
reg tOut = 0;

always @(negedge reset or negedge clk) begin
    if (reset == 1'b0)
        tOut <= 0;
    else
        tOut <= ~tOut;
end
endmodule

module dec2_7seg(input [3:0] num, output [6:0] display);
assign display =
num == 0 ? ~7'b0111111 :
num == 1 ? ~7'b0000110 :
num == 2 ? ~7'b1011011 :
num == 3 ? ~7'b1001111 :
num == 4 ? ~7'b1100110 :
num == 5 ? ~7'b1101101 :
num == 6 ? ~7'b1111101 :
num == 7 ? ~7'b0000111 :
num == 8 ? ~7'b1111111 :
num == 9 ? ~7'b1100111 :
7'bxxxxxxx;   // Output is a don't care if illegal input
endmodule // dec2_7seg