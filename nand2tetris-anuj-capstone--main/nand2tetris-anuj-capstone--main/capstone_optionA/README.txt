NAND2TETRIS PYTHON HACK ASSEMBLER — OPTION A
Roll number: 2501410040
K = 40; K mod 3 = 1
Assigned extra feature: clear invalid-instruction errors with source line numbers.

FILES
- assembler.py: two-pass Hack assembler
- Add.asm, Max.asm, Rect.asm, Pong.asm: original supplied programs (unchanged)
- Add.hack, Max.hack, Rect.hack, Pong.hack: regenerated machine-code outputs
- Box.asm, Box.hack: custom K=40 box program and its assembled output

RUN (from this folder)
  python assembler.py Add.asm
  python assembler.py Max.asm
  python assembler.py Rect.asm
  python assembler.py Pong.asm
  python assembler.py Box.asm

Each command creates/replaces the matching .hack file in this folder.

OPTION A EXTRA FEATURE
Invalid instructions show a readable message and the original .asm line number.
Example test file:
  @10
  D=Q
Expected error:
  Assembly error: line 2: invalid instruction 'D=Q' (check dest, comp, and jump)

BOX SETTINGS
K = 40
Start row = 40
Height = 20 rows
Width = 16 * ((40 mod 4) + 1) = 16 pixels
Starting screen word = 16384 + (40 * 32) = 17664

TESTING NOTE
The four regenerated outputs were byte-for-byte compared with the .hack files
that were already included in the supplied ZIP. All four matched. This is not
an independent comparison against a separately generated official assembler output.
All five generated .hack files were also checked to contain only 16-bit binary
instructions.
