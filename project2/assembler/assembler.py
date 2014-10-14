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
        'r0' :      '00000',
        'r1' :      '00001',
        'r2' :      '00010',
        'r3' :      '00011',
        'r4' :      '00100',
        'r5' :      '00101',
        'r6' :      '00110',
        'r7' :      '00111',
        'r8' :      '01000',
        'r9' :      '01001',
        'r10':      '01010',
        'r11':      '01011',
        'r12':      '01100',
        'r13':      '01101',
        'r14':      '01110',
        'r15':      '01111',
        'r16':      '10000',
        'r17':      '10001',
        'r18':      '10010',
        'r19':      '10011',
        'r20':      '10100',
        'r21':      '10101',
        'r22':      '10110',
        'r23':      '10111',
        'r24':      '11000',
        'r25':      '11001',
        'r26':      '11010',
        'r27':      '11011',
        'r28':      '11100',
        'r29':      '11101',
        'r30':      '11110',
        'r31':      '11111'
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
        for line in f.xreadlines():
            print file_line_number,
            if re.match(r'^\s*$', line):
                print 'Line is empty'
                pass
            if re.match(r'^\s*;', line):
                print 'Line is a comment'
                pass
            if re.match(r'\s*.ORIG', line):
                print 'Line has orig'
                curr = line.split()
                origs.append(curr[1])
                pass
            if re.match(r'\s([a-zA-Z]+)', line):
                print 'Line has instruction'
                pass
            if re.match(r'[a-zA-Z0-9]+:', line):
                print 'Line has section label'
                pass
            if re.match(r'\s*.NAME', line):
                print 'Line has NAME variables'
                curr = ''.join([e for i, e in enumerate(line.split()) if i > 0 ])
                curr = curr.split('=')
                names[curr[0]] = curr[1]
                pass
            file_line_number += 1
    print names
    print origs
    import ipdb; ipdb.set_trace()


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

def bin2hex(b_str, prefix):
    ''' return binary string to hex format'''
    return hex(int(b_str, 2))

def write_line_number(file, count):
    file.write(hex(count)[2:].zfill(8))
    file.write(' : ')


if __name__ == '__main__':
    main()
