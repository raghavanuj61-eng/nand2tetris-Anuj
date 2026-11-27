"""A small two-pass assembler for the 16-bit Hack computer."""

import sys
from pathlib import Path

# Hack comp field: each value is the seven-bit a+c1..c6 code.
COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "M": "1110000",
    "!D": "0001101", "!A": "0110001", "!M": "1110001",
    "-D": "0001111", "-A": "0110011", "-M": "1110011",
    "D+1": "0011111", "A+1": "0110111", "M+1": "1110111",
    "D-1": "0001110", "A-1": "0110010", "M-1": "1110010",
    "D+A": "0000010", "D+M": "1000010",
    "D-A": "0010011", "D-M": "1010011",
    "A-D": "0000111", "M-D": "1000111",
    "D&A": "0000000", "D&M": "1000000",
    "D|A": "0010101", "D|M": "1010101",
}

DEST = {
    "": "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111",
}

JUMP = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}


def make_symbol_table():
    """Return all predefined Hack symbols and register names."""
    table = {
        "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
        "SCREEN": 16384, "KBD": 24576,
    }
    for number in range(16):
        table["R" + str(number)] = number
    return table


def clean_source(input_path):
    """Remove comments/whitespace but retain each original source line number."""
    cleaned = []
    with input_path.open("r", encoding="utf-8") as source:
        for line_number, original in enumerate(source, start=1):
            line = original.split("//", 1)[0]
            line = "".join(line.split())
            if line:
                cleaned.append((line, line_number))
    return cleaned


def valid_symbol(name):
    """Check the Hack symbol naming rules."""
    if not name or not (name[0].isalpha() or name[0] in "_.$:"):
        return False
    return all(char.isalnum() or char in "_.$:" for char in name)


def first_pass(instructions, symbols):
    """Find labels and record the ROM address of the next real instruction."""
    rom_address = 0
    for instruction, line_number in instructions:
        if instruction.startswith("("):
            if not instruction.endswith(")") or instruction.count("(") != 1:
                raise ValueError("line {}: invalid label instruction '{}'".format(
                    line_number, instruction))
            label = instruction[1:-1]
            if not valid_symbol(label):
                raise ValueError("line {}: invalid label name '{}'".format(
                    line_number, label))
            if label in symbols:
                raise ValueError("line {}: duplicate or reserved label '{}'".format(
                    line_number, label))
            symbols[label] = rom_address
        elif instruction.endswith(")"):
            raise ValueError("line {}: invalid instruction '{}'".format(
                line_number, instruction))
        else:
            rom_address += 1
    return symbols


def assemble_a(instruction, line_number, symbols, next_variable):
    """Translate @value into a 16-bit A-instruction."""
    value = instruction[1:]
    if not value:
        raise ValueError("line {}: invalid A-instruction '{}': missing value".format(
            line_number, instruction))

    if value.isdigit():
        address = int(value)
    elif valid_symbol(value):
        if value not in symbols:
            symbols[value] = next_variable[0]
            next_variable[0] += 1
        address = symbols[value]
    else:
        raise ValueError("line {}: invalid A-instruction '{}'".format(
            line_number, instruction))

    if address < 0 or address > 32767:
        raise ValueError("line {}: A-instruction value must be 0..32767".format(
            line_number))
    return format(address, "016b")


def assemble_c(instruction, line_number):
    """Translate dest=comp;jump into a 16-bit C-instruction."""
    if instruction.count("=") > 1 or instruction.count(";") > 1:
        raise ValueError("line {}: invalid C-instruction '{}'".format(
            line_number, instruction))

    if ";" in instruction:
        before_jump, jump = instruction.split(";", 1)
    else:
        before_jump, jump = instruction, ""

    if "=" in before_jump:
        dest, comp = before_jump.split("=", 1)
    else:
        dest, comp = "", before_jump

    if dest not in DEST or comp not in COMP or jump not in JUMP:
        raise ValueError("line {}: invalid instruction '{}' (check dest, comp, and jump)".format(
            line_number, instruction))
    if not comp or (not dest and not jump):
        raise ValueError("line {}: invalid C-instruction '{}'".format(
            line_number, instruction))

    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


def assemble(input_path):
    """Run both passes and write a .hack file beside the input file."""
    instructions = clean_source(input_path)

    # PASS 1: labels are added before any A-instructions are translated.
    symbols = make_symbol_table()
    first_pass(instructions, symbols)

    # PASS 2: translate instructions and allocate variables from RAM[16].
    next_variable = [16]
    machine_code = []
    for instruction, line_number in instructions:
        if instruction.startswith("("):
            continue  # Labels do not become machine instructions.
        if instruction.startswith("@"):
            binary = assemble_a(instruction, line_number, symbols, next_variable)
        else:
            binary = assemble_c(instruction, line_number)
        machine_code.append(binary)

    output_path = input_path.with_suffix(".hack")
    with output_path.open("w", encoding="ascii", newline="\n") as output:
        for binary in machine_code:
            output.write(binary + "\n")
    return output_path, len(machine_code)


def main():
    if len(sys.argv) != 2:
        print("Usage: python assembler.py <file.asm>")
        return 2

    input_path = Path(sys.argv[1])
    if input_path.suffix.lower() != ".asm":
        print("Error: please provide an .asm file.")
        return 2
    if not input_path.is_file():
        print("Error: file not found: {}".format(input_path))
        return 2

    try:
        output_path, count = assemble(input_path)
    except (OSError, UnicodeError, ValueError) as error:
        print("Assembly error: {}".format(error))
        return 1

    print("Created {} ({} instructions).".format(output_path, count))
    return 0


if __name__ == "__main__":
    sys.exit(main())
