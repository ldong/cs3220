#!/usr/bin/env python
import os.path, sys, re


header = {
        'width': 32,
        'depth': 2048,
        'address_radix': 'HEX',
        'data_radix': 'HEX'
        }

# 32 registers from r0 to r31
registers = {
        'zero' :      '00000', # r0'
        'at'   :      '00001', # r1'
        'v0'   :      '00010', # r2'
        'v1'   :      '00011', # r3'
        'a0'   :      '00100', # r4'
        'a1'   :      '00101', # r5'
        'a2'   :      '00110', # r6'
        'a3'   :      '00111', # r7'
        't0'   :      '01000', # r8'
        't1'   :      '01001', # r9'
        't2'   :      '01010', # r10
        't3'   :      '01011', # r11
        't4'   :      '01100', # r12
        't5'   :      '01101', # r13
        't6'   :      '01110', # r14
        't7'   :      '01111', # r15
        's0'   :      '10000', # r16
        's1'   :      '10001', # r17
        's2'   :      '10010', # r18
        's3'   :      '10011', # r19
        's4'   :      '10100', # r20
        's5'   :      '10101', # r21
        's6'   :      '10110', # r22
        's7'   :      '10111', # r23
        't8'   :      '11000', # r24
        't9'   :      '11001', # r25
        'k0'   :      '11010', # r26
        'k1'   :      '11011', # r27
        'gp'   :      '11100', # r28
        'sp'   :      '11101', # r29
        'fp'   :      '11110', # r30
        'ra'   :      '11111'  # r31
        }

# Instruction Set Architecture from project-isa.pdf file in binaries
opcodes = {
        'ADD':      '00000000',
        'SUB':      '00000001',
        'AND':      '00000100',
        'OR':       '00000101',
        'XOR':      '00000110',
        'NAND':     '00001100',
        'NOR':      '00001101',
        'XNOR':     '00001110',

        'ADDI':     '10000000',
        'SUBI':     '10000001',
        'ANDI':     '10000100',
        'ORI':      '10000101',
        'XORI':     '10000110',
        'NANDI':    '10001100',
        'NORI':     '10001101',
        'XNORI':    '10001110',
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

        # N is implemented using BEQ
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


instruction_line_number = 0
names = {}
origs = []

# look up instruciton type
isa_type_12_zero = set([
                'ADD', 'SUB', 'AND', 'OR', 'XOR', 'NAND', 'NOR', 'XNOR',
                'F', 'EQ', 'LT', 'LTE', 'T', 'NE', 'GTE', 'GT'])
isa_type_imm = set([
    'ADDI', 'SUBI', 'ANDI', 'ORI', 'XORI', 'NANDI', 'NORI', 'XNORI',
    'LW', 'SW',
    'FI', 'EQI', 'LTI', 'LTEI', 'TI', 'NEI', 'GTEI', 'GTI'])
isa_type_mvhi = set(['MVHI'])
isa_type_jal = set(['JAL'])
isa_type_pcrel = set([
    'BF', 'BEQ', 'BLT', 'BLTE', 'BEQZ', 'BLTZ', 'BLTEZ'
    ])
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

def main():
    fname = 'Test.a32'
    # fname = raw_input('Enter the file name: ')
    if check_file(fname):
        file_suffix = '.mif'
        output_file_name = ''.join([fname[:-4], file_suffix])
        read_file(fname)
        write_file(output_file_name)

def check_file(fname):
    if os.path.isfile(fname):
        if fname[-4:] == '.a32':
            return True
        else:
            print 'Please make sure it is a .a32 file'
    else:
        print 'File: {} does not exist'.format(fname)
    return False


def read_file(fname):
    print 'Reading file: {}'.format(fname)
    with open (fname, 'r') as f:
        file_line_number = 1
        total_instructions = 0
        for line in f.xreadlines():
            print file_line_number,
            if re.match(r'^\s*$', line):
                # print 'Line is empty'
                pass
            if re.match(r'^\s*;', line):
                # print 'Line is a comment'
                pass
            if re.match(r'\s*.ORIG', line):
                print 'Line has orig'
                curr = line.split()
                origs.append(curr[1])
            if re.match(r'\s([a-zA-Z]+)', line):
                print 'Line has instruction'
                curr = line.split()
                instruction = curr[0]
                curr = ''.join([e for i, e in enumerate(line.split()) if i > 0])
                curr = curr.split(',')
                rd = curr[0]
                rs1 = curr[1]
                rs2 = curr[2]
                import ipdb; ipdb.set_trace()
                total_instructions += 1
            if re.match(r'[a-zA-Z0-9]+:', line):
                print 'Line has section label'
                pass
            if re.match(r'\s*.NAME', line):
                print 'Line has NAME variables'
                curr = ''.join([e for i, e in enumerate(line.split()) if i > 0])
                curr = curr.split('=')
                names[curr[0]] = curr[1]
                pass
            file_line_number += 1
    print names
    print origs
    import ipdb; ipdb.set_trace()


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

def parse_file(fname):
    pass


def write_file(output_file_name):
    with open (output_file_name, 'w') as f:
        write_header(f)
        write_contents(f, instruction_line_number)
        write_footer(f)

def write_contents(file, line_number):
    file.write('\n')
    for i in xrange(10):
        write_line_number(file, line_number)
        line_number = line_number + 1
        file.write('\n')


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
