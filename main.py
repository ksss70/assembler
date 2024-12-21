import argparse
import struct
import json

MEMORY_SIZE = 1024

def parse_args():
    parser = argparse.ArgumentParser(description="Assembler and Interpreter for UVM")
    parser.add_argument("mode", choices=["assemble", "interpret"], help="Operation mode")
    parser.add_argument("input_file", help="Input file")
    parser.add_argument("--output_file", help="Output file")
    parser.add_argument("--log_file", help="Log file (JSON format)")
    parser.add_argument("--result_file", help="Result file for interpreter (JSON format)")
    parser.add_argument("--memory_range", help="Memory range for interpreter (start:end)")
    return parser.parse_args()

def assemble_instruction(a, b, c, d=0):
    instruction = (
        (a & 0xF) |
        ((b & 0xFFFFF) << 4) |
        ((c & 0x3FFF) << 24) |
        ((d & 0xFFFF) << 38)
    )
    return list(struct.pack("<Q", instruction))

def assemble(input_file, output_file, log_file):
    instructions = []
    with open(input_file, "r") as f:
        for line in f:
            if not line.strip():
                continue
            parts = {k: int(v) for k, v in (pair.split("=") for pair in line.strip().split(","))}
            instructions.append(parts)

    binary_data = []
    log_data = []
    for instruction in instructions:
        a, b, c = instruction["A"], instruction["B"], instruction["C"]
        d = instruction.get("D", 0)
        bytes_list = assemble_instruction(a, b, c, d)
        binary_data.extend(bytes_list)
        log_data.append({"A": a, "B": b, "C": c, "D": d, "Bytes": bytes_list})
    with open(log_file, "w") as log_json:
        json.dump(log_data, log_json, indent=4)
    with open(output_file, "wb") as bin_file:
        bin_file.write(bytearray(binary_data))


def interpret(input_file, result_file, memory_range):
    memory = [0] * MEMORY_SIZE
    with open(input_file, "rb") as f:
        binary_data = f.read()
    for i in range(0, len(binary_data), 8):
        if i + 8 > len(binary_data):
            break
        command = binary_data[i:i + 8]
        instruction = struct.unpack("<Q", command)[0]
        a = instruction & 0xF
        b = (instruction >> 4) & 0xFFFFF
        c = (instruction >> 24) & 0x3FFF
        d = (instruction >> 38) & 0xFFFF
        if a == 15:
            memory[b] = c
        elif a == 14:
            memory[b] = memory[memory[c]]
        elif a == 8:
            memory[memory[c]] = memory[b]
        elif a == 12:
            memory[memory[b]] = memory[c] >> memory[d]
    start, end = map(int, memory_range.split(":"))
    result_data = [{"Address": addr, "Value": memory[addr]} for addr in range(start, end + 1)]
    with open(result_file, "w") as result_json:
        json.dump(result_data, result_json, indent=4)

def main():
    args = parse_args()
    if args.mode == "assemble":
        if not args.output_file or not args.log_file:
            print("Error: --output_file and --log_file are required for assembly.")
            return
        assemble(args.input_file, args.output_file, args.log_file)
    elif args.mode == "interpret":
        if not args.result_file or not args.memory_range:
            print("Error: --result_file and --memory_range are required for interpretation.")
            return
        interpret(args.input_file, args.result_file, args.memory_range)

if __name__ == "__main__":
    main()

#python main.py assemble input.txt --output_file output.bin --log_file log.json
#python main.py interpret output.bin --result_file result.json --memory_range 0:10
