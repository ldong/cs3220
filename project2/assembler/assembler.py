#!/usr/bin/env python
import os.path

constants = {
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
    if os.path.isfile(fname):
        if fname[-4:] == '.a32':
            read_file(fname)
        else:
            print 'Please make sure it is a .a32 file'
    else:
        print 'File: {} does not exist'.format(fname)

    # for k, v in registers.iteritems():
        # print k, v


def read_file(fname):
    print 'Reading file: {}'.format(fname)

def parse_file(fname):
    pass

def write_file(output_file_name):
    pass

def write_header(output_file):
    # output_file.puts "WIDTH=#{DATA_BITS};"
    # output_file.puts "DEPTH=#{ADDRESSES};"
    # output_file.puts "ADDRESS_RADIX=HEX;"
    # output_file.puts "DATA_RADIX=HEX;"
    # output_file.puts "CONTENT BEGIN"
    pass

def write_footer(output_file):
    pass

if __name__ == '__main__':
    main()
