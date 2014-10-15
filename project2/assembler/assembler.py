#!/usr/bin/env python
import os.path, sys, re, copy
from collections import deque

header = {
        'width': 32,
        'depth': 2048,
        'address_radix': 'HEX',
        'data_radix': 'HEX'
        }

# 32 registers from r0 to r31
registers = {
        'A0'    :      '00000',     # r0 -> func arg
        'A1'    :      '00001',     # r1 -> func arg
        'A2'    :      '00010',     # r2 -> func arg
        'A3'    :      '00011',     # r3 -> caller saved
        'RV'    :      '00011',     # r3 -> return value, caller saved
        'T0'    :      '00100',     # r4 -> temp, caller saved
        'T1'    :      '00101',     # r5 -> temp, caller saved
        'S0'    :      '00110',     # r6 -> callee saved value
        'S1'    :      '00111',     # r7 -> callee saved value
        'S2'    :      '01000',     # r8 -> callee saved value
        'R9'    :      '01001',     # r9 -> reserved for assembler use
        'R10'   :      '01010',     # r10-> reserved for system use
        'R11'   :      '01011',     # r11-> reserved for system use
        'GP'    :      '01100',     # r12-> global pointer
        'FP'    :      '01101',     # r13-> frame pointer
        'SP'    :      '01110',     # r14-> stack pointer
        'RA'    :      '01111',     # r15-> return address
        'R16'   :      '10000',     # r16
        'R17'   :      '10001',     # r17
        'R18'   :      '10010',     # r18
        'R19'   :      '10011',     # r19
        'R20'   :      '10100',     # r20
        'R21'   :      '10101',     # r21
        'R22'   :      '10110',     # r22
        'R23'   :      '10111',     # r23
        'R24'   :      '11000',     # r24
        'R25'   :      '11001',     # r25
        'R26'   :      '11010',     # r26
        'R27'   :      '11011',     # r27
        'R28'   :      '11100',     # r28
        'R29'   :      '11101',     # r29
        'R30'   :      '11110',     # r30
        'R31'   :      '11111'      # r31
        }

# Instruction Set Architecture from project-isa.pdf file in binaries
# each opcode has 8 bits
opcodes = {
        'ADD':      '00000000',
        'SUB':      '00000001',
        'AND':      '00000100',
        'OR':       '00000101',
        'XOR':      '00000110',
        'NAND':     '00001100',
        'NOR':      '00001101',
        'NXOR':     '00001110',

        'ADDI':     '10000000',
        'SUBI':     '10000001',
        'ANDI':     '10000100',
        'ORI':      '10000101',
        'XORI':     '10000110',
        'NANDI':    '10001100',
        'NORI':     '10001101',
        'NXORI':    '10001110',
        'MVHI':     '10001011',

        'SW':       '10010000',
        'LW':       '01010000',

        'F':        '00100000',
        'EQ':       '00100001',
        'LT':       '00100010',
        'LTE':      '00100011',
        'T':        '00101000',
        'NE':       '00101001',
        'GTE':      '00101010',
        'GT':       '00101011',

        'FI':       '10100000',
        'EQI':      '10100001',
        'LTI':      '10100010',
        'LTEI':     '10100011',
        'TI':       '10101000',
        'NEI':      '10101001',
        'GTEI':     '10101010',
        'GTI':      '10101011',

        'BF':       '01100000',
        'BEQ':      '01100001',
        'BLT':      '01100010',
        'BLTE':     '01100011',
        'BEQZ':     '01100101',
        'BLTZ':     '01100110',
        'BLTEZ':    '01100111',

        'BT':       '01101000',
        'BNE':      '01101001',
        'BGTE':     '01101010',
        'BGT':      '01101011',
        'BNEZ':     '01101101',
        'BGTEZ':    '01101110',
        'BGTZ':     '01101111',

        'JAL':      '10110000',

        # Pseudo-instructions
        # B is implemented using BEQ
        'BR': '',

        # NOT is implemented using NAND
        'NOT': '',

        # BLE/BGE is implemented using LTE/GTE and BNEZ
        'BLE': '',
        'BGE': '',

        # CALL/RET/JMP is implemented using JAL
        'CALL': '',
        'RET': '',
        'JMP': '',
        }

names = {}
origs = []
words = {}
labels = set()

# look up instruciton type
isa_type_12_zero = set([
                'ADD', 'SUB', 'AND', 'OR', 'XOR', 'NAND', 'NOR', 'NXOR',
                'F', 'EQ', 'LT', 'LTE', 'T', 'NE', 'GTE', 'GT'])

isa_type_imm16 = set([
    'ADDI', 'SUBI', 'ANDI', 'ORI', 'XORI', 'NANDI', 'NORI', 'NXORI',
    'FI', 'EQI', 'LTI', 'LTEI', 'TI', 'NEI', 'GTEI', 'GTI'])

isa_type_lw_sw = set(['LW', 'SW'])

isa_type_mvhi = set(['MVHI'])
isa_type_jal = set(['JAL'])
isa_type_pcrel = set([
    'BF', 'BEQ', 'BLT', 'BLTE', 'BEQZ', 'BLTZ', 'BLTEZ',
    'BT', 'BNE', 'BGTE', 'BGT', 'BNEZ', 'BGTEZ', 'BGTZ'
    ])
isa_type_two_instructions = set(['BLT', 'BLE', 'BGT', 'BGE'])

isa_type_implemented = {
        'BR':   'BEQ',
        'SUBI': 'ADDI',
        'NOT':  'NAND',
        'BLT':  'LT',
        'BLE':  'LE',
        'BGT':  'GT',
        'BGE':  'GE',
        'CALL': 'JAL',
        'RET':  'JAL',
        'JMP':  'JAL'
        }

isa_has_3_operands = set([
     'ADD', 'SUB', 'AND', 'OR', 'XOR', 'NAND', 'NOR', 'NXOR',
     'ADDI', 'ANDI', 'ORI', 'XORI', 'NANDI', 'NORI', 'NXORI',
     'F', 'EQ', 'LT', 'LTE', 'T', 'NE', 'GTE', 'GT',
     'FI', 'EQI', 'LTI', 'LTEI', 'TI', 'NEI', 'GTEI', 'GTI',
     'SUBI',
     'BF', 'BEQ', 'BLT', 'BLTE',
     'BT', 'BNE', 'BGTE', 'BGT',
     'BLT', 'BLE', 'BGT', 'BGE'
    ])

isa_has_2_operands = set([
     'MVHI',
     'LW', 'SW',
     'BEQZ', 'BLTZ', 'BLTEZ',
     'BNEZ', 'BGTEZ', 'BGTZ',
     'JAL',
     'NOT',
     ])

isa_has_1_operands = set(['BR', 'CALL', 'RET', 'JMP'])

def main():
    fname = 'Test.a32'
    # fname = 'Sort.a32'
    # fname = raw_input('Enter the file name: ')
    if check_file(fname):
        file_suffix = '.mif'
        output_file_name = ''.join([fname[:-4], file_suffix])
        # buffer for instruction
        instructions = deque()
        instruction_line_number = read_file(fname, instructions)
        write_file(output_file_name, instructions, instruction_line_number)

def check_file(fname):
    if os.path.isfile(fname):
        if fname[-4:] == '.a32':
            return True
        else:
            print 'Please make sure it is a .a32 file'
    else:
        print 'File: {} does not exist'.format(fname)
    return False


def read_file(fname, instructions):
    print 'Reading file: {}'.format(fname)
    with open (fname, 'r') as f:
        file_line_number = 1
        file_mem_numbber = 1
        total_instructions = 0
        for line in f.xreadlines():
            print file_line_number,
            line = line.upper()
            if re.match(r'^\s*$', line):
                # print 'Line is empty'
                pass
            elif re.match(r'^\s*;', line):
                print 'Line is a comment'
            elif re.match(r'\s*.ORIG', line):
                print 'Line has orig'
                curr = line.split()
                origs.append(curr[1])
            elif re.match(r'\s([a-zA-Z]+)', line):
                print 'Line has instruction'
                # remove comments
                line = re.sub(r'\w*;.*$', '', line)
                curr = line.strip().split()
                opcode = curr[0].upper()
                if opcode not in isa_has_3_operands \
                    and opcode not in isa_has_2_operands \
                    and opcode not in isa_has_1_operands:
                    print line
                    print 'Current instruction has neither 1,2,3 operands at \
                            line {}'.format(file_line_number)
                    sys.exit(1)
                if opcode in isa_type_two_instructions:
                    # TODO
                    instr = line.split(',')
                    # import ipdb; ipdb.set_trace()
                    instructions.append(line)
                    instructions.append(line)
                    total_instructions += 2
                else:
                    instructions.append(line)
                    total_instructions += 1
            elif re.match(r'[a-zA-Z0-9]+:\s*', line):
                print 'Line has section label'
                instructions.append(line)
                label = line.strip()[:-1]
                # import ipdb; ipdb.set_trace()
                labels.add(label)
            elif re.match(r'\s*.NAME', line):
                print 'Line has NAME variables'
                curr = ''.join([e for i, e in enumerate(line.split()) if i > 0])
                curr = curr.split('=')
                names[curr[0]] = curr[1]
            else:
                print 'Something went wrong, this line is not a valid line'
                import ipdb; ipdb.set_trace()
            file_line_number += 1
            file_mem_numbber += 4
    print 'names: \n {}'.format(names)
    print 'origs: \n {}'.format(origs)
    print 'labels: \n {}'.format(labels)
    print 'total_instructions: \n {}'.format(total_instructions)
    return total_instructions

def parse_instruction(idx, instruction, instructions):
    rd, rs1, rs2, imm12, imm16, immHi, pcrel  = None, None, None, None, None, None, None
    curr = instruction.strip().split()
    opcode = curr[0].upper()
    if opcode in isa_has_3_operands:
        curr = ''.join([e for i, e in enumerate(curr) if i > 0])
        curr = curr.split(',')
        if opcode in isa_type_12_zero:
            imm12 = '000000000000'
            rd = curr[0]
            rs1 = curr[1]
            rs2 = curr[2]
        elif opcode in isa_type_imm16:
            rd = curr[0]
            rs1 = curr[1]
            imm16 = curr[2]
        elif opcode in isa_type_pcrel:
            rs1 = curr[0]
            rs2 = curr[1]
            target = curr[2]
            import ipdb; ipdb.set_trace()
            if target in labels:
                pcrel = find_pcrel(idx, target, opcode, instructions)
                print 'Pcrel: ' + pcrel
            else:
                # pcrel = '0' + names.get(curr[1])[6:] or curr[1][2:]
                # import ipdb; ipdb.set_trace()
                pass
    elif opcode in isa_has_2_operands:
        curr = ''.join([e for i, e in enumerate(curr) if i > 0])
        # import ipdb; ipdb.set_trace()
        if opcode in isa_type_mvhi:
            curr = curr.split(',')
            rd = curr[0]
            imm16 = get_imm16(curr[1])
            immHi = '0' + imm16
        elif opcode in isa_type_lw_sw:
            curr = ''.join(curr.replace(',',' '))
            curr = ''.join(curr.replace('(',' '))
            curr = curr.replace(')','')
            curr = curr.split()
            if opcode == 'LW':
                rd = curr[0]
                imm16 = get_imm16(curr[1])
                rs1 = curr[2]
            else:
                rs2 = curr[0]
                imm16 = get_imm16(curr[1])
                rs1 = curr[2]
        elif opcode in isa_type_pcrel:
            rs1 = curr[0]
            target = curr[1]
            if target in names:
                a = find_pcrel(idx, target, opcode, instructions)
            # pcrel = '0' + names.get(curr[1])[6:] or curr[1][2:]
                # import ipdb; ipdb.set_trace()
            # import ipdb; ipdb.set_trace()
        elif opcode == 'JAL':
            pass
            # import ipdb; ipdb.set_trace()
        elif opcode == 'NOT':
            pass
            # import ipdb; ipdb.set_trace()
        else:
            print 'Something went wrong here'
            import ipdb; ipdb.set_trace()
        # rd = curr[0]
        # rs1 = curr[1]
        # if opecode in
        # elif opcode in :
    elif opcode in isa_has_1_operands:
        curr = ''.join([e for i, e in enumerate(curr) if i > 0])
        curr = curr.split(',')
        if opcode == 'BR':
            imm16 = curr[0]
        elif opcode == 'CALL':
            pass
        elif opcode == 'RET':
            pass
        elif opcode == 'JMP':
            pass
        else:
            print 'current line has isa_has_1_operand, ant its not part of it'
            sys.exit(1)
    binary = convert_instruction_to_binary(instruction, rd, rs1, rs2, imm16)
    return binary

def get_imm16(target):
    ''' get the imm from target, regardless its a immdiate value or a variable'''
    if target in names:
        if names.get(target)[:2].upper() == '0X':
            imm16 = names.get(target)[6:]
        else:
            imm16 = names.get(target)
    else:
        imm16 = target
    return imm16

def convert_instruction_to_binary(instruction, rd, rs1, rs2, imm):
    ''' convert instruction into binary'''
    binary = 0
    inst_binary = opcodes.get(rd)
    return binary

def convert_instruction_to_correct_instruction(instruction, rd, rs1, rest):
    ''' return a tuble of instruction binarys '''
    first_instruction = 0
    second_instruction= 0

    if instruction.upper() in isa_type_implemented:
        temp_instruction = isa_type_implemented.get(instruction)
        if temp_instruction == 'BEQ':
            pass
        elif temp_instruction == 'ADDI':
            pass
        elif temp_instruction == 'NAND':
            pass
        elif temp_instruction == 'LT':
            pass
        elif temp_instruction == 'LE':
            pass
        elif temp_instruction == 'GT':
            pass
        elif temp_instruction == 'GE':
            pass
        # convert one instruction into two instructions
        elif temp_instruction == 'JAL':
            if instruction == 'CALL':
                pass
            elif instruction == 'RET':
                pass
            elif instruction == 'JMP':
                pass
    elif instruction.upper() in isa_type_12_zero:
        # 12 bits
        zeros = '000000000000'
        r2 = rest
        first_instruction = convert_instruction_to_binary(instruction, rd, rs1, r2, zeros)
    elif instruction.upper() in isa_type_imm:
        imm = None
        first_instruction = convert_instruction_to_binary(instruction, rd, rs1, r2, imm)
    elif instruction.upper() in isa_type_mvhi:
        immHi = None
        first_instruction = convert_instruction_to_binary(instruction, rd, '0000', None, immHi)
    elif instruction.upper() in isa_type_jal:
        # 16 bits
        shImm = None
        first_instruction = convert_instruction_to_binary(instruction, rd, rs1, None, shImm)
    elif instruction.upper() in isa_type_pcrel:
        # 16 bits
        pcrel = None
        first_instruction = convert_instruction_to_binary(instruction, None, rs1, rs2, imm)
    else:
        print 'Instruction {} not found, exiting program'.format(instruction)
        sys.exit(1)
    return (first_instruction, second_instruction)


def write_file(output_file_name, instructions, instruction_line_number):
    with open (output_file_name, 'w') as f:
        write_header(f)
        # buffer for binary traslations
        instructions_binaries = deque()
        instructions_copy = copy.copy(instructions)
        for lnumber in xrange(instruction_line_number):
            write_instruction(f, instructions.popleft())
            write_line_number(f, lnumber)
            # write_binary(f, binstructions)
            write_change_line(f)
        write_footer(f)
        write_change_line(f)
        for idx, instruction in enumerate(instructions_copy):
            f.write(instruction)
            binary = parse_instruction(idx, instruction, instructions_copy)
            # write_change_line(f)

def write_binary(file, content):
    pass

def write_instruction(file, content):
    file.write('-- @ ')
    file.write(content)


def write_line_number(file, line_number):
    write_line_number(file, line_number)


def write_header(file):
    file.write('WIDTH={};'.format(header.get('width')))
    write_change_line(file)

    file.write('DEPTH={};'.format(header.get('depth')))
    write_change_line(file)

    file.write('ADDRESS_RADIX={};'.format(header.get('address_radix')))
    write_change_line(file)

    file.write('DATA_RADIX={};'.format(header.get('data_radix')))
    write_change_line(file)

    file.write('CONTENT BEGIN')
    write_change_line(file)


def write_fill_dead(file, start, end):
    content = '[{}.clear.{}] : DEAD;'.format(start, end)
    file.write(content)

def find_pcrel(curr_idx, target, opcode, instructions):
    ''' calculate the index difference between curr and target '''
    target_idx, pcrel = None, None
    for i, c in enumerate(instructions):
        if target == c.strip()[:-1]:
            target_idx = i
    if opcode in isa_type_two_instructions:
        pcrel = target_idx - curr_idx
    else:
        pcrel = target_idx - curr_idx - 1
    import ipdb; ipdb.set_trace()
    return pcrel

def write_footer(file):
    file.write('END;')

def write_change_line(file):
    file.write('\n')

def bin2hex(b_str):
    ''' return binary string to hex format'''
    if(len(b_str) != 32):
        print 'its not 32 bits, go fix it'
        sys.exit(1)
    return hex(int(b_str, 2))

def write_line_number(file, count):
    file.write(hex(count)[2:].zfill(8))
    file.write(' : ')


if __name__ == '__main__':
    main()
