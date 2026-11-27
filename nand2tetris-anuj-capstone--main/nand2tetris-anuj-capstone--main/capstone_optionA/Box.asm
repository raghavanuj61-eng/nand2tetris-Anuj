// K = 40: starts at screen row 40, is 20 rows tall, and 16 pixels wide.
// Screen address = 16384 + (40 * 32) = 17664. One word is 16 pixels.

(POLL)
@KBD
D=M
@DRAW
D;JGT
@ERASE
0;JMP

(DRAW)
@17664
D=A
@address
M=D
@20
D=A
@rows
M=D
(DRAW_LOOP)
@address
A=M
M=-1
@32
D=A
@address
M=D+M
@rows
MD=M-1
@DRAW_LOOP
D;JGT
@POLL
0;JMP

(ERASE)
@17664
D=A
@address
M=D
@20
D=A
@rows
M=D
(ERASE_LOOP)
@address
A=M
M=0
@32
D=A
@address
M=D+M
@rows
MD=M-1
@ERASE_LOOP
D;JGT
@POLL
0;JMP
