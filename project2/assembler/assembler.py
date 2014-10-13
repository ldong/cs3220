#!/usr/bin/env python
import os.path
import sys

header = {
        'width': 32,
        'depth': 2048,
        'address_radix': 'HEX',
        'data_radix': 'HEX'
        }

registers = {
        "zero": "00000",
        "a0": "00001",
        "a1": "00010",
        "a2": "00011",
        "a3": "00100",
        "r5": "00101",
        "r6": "00110",
        "r7": "00111",
        "t0": "01000",
        "t1": "01001",
        "t2": "01010",
        "t3": "01011",
        "t4": "01100",
        "t5": "01101",
        "t6": "01110",
        "t7": "01111",
        "s0": "10000",
        "s1": "10001",
        "s2": "10010",
        "s3": "10011",
        "s4": "10100",
        "s5": "10101",
        "s6": "10110",
        "s7": "10111",
        "r24": "11000",
        "r25": "11001",
        "r26": "11010",
        "r27": "11011",
        "r28": "11100",
        "r29": "11101",
        "r30": "11110",
        "r31": "11111"
        }

opcode_hash = {
        "alur": '000000',
        "andi":"000001",
        "ori":"000010",
        "hi":"000011",
        "addi":"000100",
        "lw":"010000",
        "sw":"010001",
        "jal":"100000",
        "beq":"100001",
        "bne":"100101"
        }



def main():
    fname = raw_input('Enter the file name: ')
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
        print f.read()


def parse_file(fname):
    pass


def write_file(output_file_name):
    with open (output_file_name, 'w') as f:
        write_header(f)
        write_contents(f)
        write_footer(f)

def write_contents(file):
    file.write('\n')
    file.write('Empty')
    file.write('\n')

def write_header(file):
    file.write('WIDTH={};'.format(header.get('width')))
    file.write('\n')
    file.write('DEPTH={};'.format(header.get('depth')))
    file.write('\n')
    file.write('ADDRESS_RADIX={};'.format(header.get('address_radix')))
    file.write('\n')
    file.write('DATA_RADIX={};'.format(header.get('data_radix')))
    file.write('\n')
    file.write('CONTENT BEGIN')
    file.write('\n')

def write_footer(file):
    file.write('END;')

if __name__ == '__main__':
    main()
