import sys
import ctypes

pc = 0
instructions = []
data = bytearray(0x10001)
regi = [0]*32
count = 0
pcMax = 0

# inst file 읽기
fInst = sys.argv[1]
with open(fInst, 'rb') as file:
    instOb = file.read()
    instByteString = [format(byte, '02x') for byte in instOb]
    instWordString = [instByteString[i:i+4] for i in range(0, len(instByteString), 4)]
    instructionsHEn = [''.join(hexByte) for hexByte in instWordString]
    instructionsHDian = [i[::-1] for i in instructionsHEn]
    for i in instructionsHDian:
        swapped = ''
        for j in range(0,8,2):
            swapped += i[j+1] + i[j]
        instructions.append(format(int(swapped, 16),'0>32b'))
    pcMax = len(instOb) - 1

if len(sys.argv) == 3: # data file 없을 때
    count = int(sys.argv[2])
elif len(sys.argv) == 4: # data file 있을 때
    fData = sys.argv[2]
    with open(fData, 'rb') as file:
        dataOb = file.read()
        data[:len(dataOb)] = dataOb
        data_hex = data.hex()
        seq = [data_hex[i:i+8] for i in range(0, len(data_hex), 8)]
        seq_reverse = []
        for i in range(len(seq)):
            seq_reverse.append(''.join([seq[i][j-2:j] for j in range(len(seq[i]), 0, -2)]))
        data = []
        for i in range(len(seq_reverse)):
            data.append(format(int(seq_reverse[i],16),'0>32b'))
    for i in range(len(data)):
        data[i] = int(data[i], 2)
    count = int(sys.argv[3])

# 2진수 string을 unsigned int로
def binToUnsigned(bi: str):
    usv = 0
    for i in range(len(bi)):
        usv += int(bi[-i-1])*2**i
    return usv

# 2진수 string을 signed int로
def binToSigned(bi: str):
    sv = 0
    if bi[0] == '1':
        for i in range(len(bi)-1):
            sv += int(bi[-i-1])*2**i
        sv += -2**(len(bi)-1)
    else:
        sv = binToUnsigned(bi)
    return sv

def signExtend(value, bits):
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)

def riscvInstruction(inst: str):
    global pc
    opcode = inst[25:32]
    iName = 'unknown'
    # R format
    if opcode == '0110011':
        func7 = inst[0:7]
        rs2 = inst[7:12]
        rs1 = inst[12:17]
        func3 = inst[17:20]
        rd = inst[20:25]
        
        rs2 = binToUnsigned(rs2)
        rs1 = binToUnsigned(rs1)
        rd = binToUnsigned(rd)
        
        if func3 == '000':
            if func7 == '0000000':
                iName = 'add'
                regi[rd] = regi[rs1] + regi[rs2]
            elif func7 == '0100000':
                iName = 'sub'
                regi[rd] = regi[rs1] - regi[rs2]
        elif func3 == '001':
            if func7 == '0000000':
                iName = 'sll'
                regi[rd] = regi[rs1] << (regi[rs2] & 0b11111)
        elif func3 == '010':
            if func7 == '0000000':
                iName = 'slt'
                if regi[rs1] < regi[rs2]:
                    regi[rd] = 1
                else:
                    regi[rd] = 0
        # elif func3 == '011':
        #     if func7 == '0000000':
        #         iName = 'sltu'
        elif func3 == '100':
            if func7 == '0000000':
                iName = 'xor'
                regi[rd] = regi[rs1] ^ regi[rs2]
        elif func3 == '101':
            if func7 == '0000000':
                iName = 'srl'
                regi[rd] = regi[rs1] >> (regi[rs2] & 0b11111)
                if (regi[rs2] & 0b11111) > 0:
                    mask = 0x7fffffff >> ((regi[rs2] & 0b11111) - 1)
                    regi[rd] = regi[rd] & mask
            elif func7 == '0100000':
                iName = 'sra'
                regi[rs1] = ctypes.c_int32(regi[rs1]).value
                regi[rd] = regi[rs1] >> (regi[rs2] & 0b11111)
        elif func3 == '110':
            if func7 == '0000000':
                iName = 'or'
                regi[rd] = regi[rs1] | regi[rs2]
        elif func3 == '111':
            if func7 == '0000000':
                iName = 'and'
                regi[rd] = regi[rs1] & regi[rs2]
        
        # if iName == 'unknown':
        #     return 'unknown instruction'
        # else:
        #     return f'{iName} x{rd}, x{rs1}, x{rs2}'
        pc = pc + 4
        return None
    # I format
    elif opcode == '0010011':
        func3 = inst[17:20]
        if func3 == '001' or func3 == '101':
            func7 = inst[0:7]
            shamt = inst[7:12]
            rs1 = inst[12:17]
            rd = inst[20:25]
            
            shamt = binToUnsigned(shamt)
            rs1 = binToUnsigned(rs1)
            rd = binToUnsigned(rd)
            
            if func3 == '001':
                if func7 == '0000000':
                    iName = 'slli'
                    regi[rd] = regi[rs1] << shamt
            else:
                if func7 == '0000000':
                    iName = 'srli'
                    regi[rd] = regi[rs1] >> shamt
                    if shamt > 0:
                        mask = 0x7fffffff >> shamt - 1
                        regi[rd] = regi[rd] & mask
                elif func7 == '0100000':
                    iName = 'srai'
                    regi[rs1] = ctypes.c_int32(regi[rs1]).value
                    regi[rd] = regi[rs1] >> shamt
            
            # if iName == 'unknown':
            #     return 'unknown instruction'
            # else:
            #     return f'{iName} x{rd}, x{rs1}, {shamt}'
            pc = pc + 4
            return None
        else:
            imm = inst[0:12]
            rs1 = inst[12:17]
            rd = inst[20:25]
            
            imm = binToSigned(imm)
            imm = signExtend(imm, 12)
            rs1 = binToUnsigned(rs1)
            rd = binToUnsigned(rd)
            
            if func3 == '000':
                iName = 'addi'
                regi[rd] = regi[rs1] + imm
            elif func3 == '010':
                iName = 'slti'
                if regi[rs1] < imm:
                    regi[rd] = 1
                else:
                    regi[rd] = 0
            # elif func3 == '011':
            #     iName = 'sltiu'
            elif func3 == '100':
                iName = 'xori'
                regi[rd] = regi[rs1] ^ imm
            elif func3 == '110':
                iName = 'ori'
                regi[rd] = regi[rs1] | imm
            elif func3 == '111':
                iName = 'andi'
                regi[rd] = regi[rs1] & imm
            
            # if iName == 'unknown':
            #     return 'unknown instruction'
            # else:
            #     return f'{iName} x{rd}, x{rs1}, {imm}'
            pc = pc + 4
            return None
    # I format(load)
    elif opcode == '0000011':
        imm = inst[0:12]
        rs1 = inst[12:17]
        func3 = inst[17:20]
        rd = inst[20:25]
        
        imm = binToSigned(imm)
        imm = signExtend(imm, 12)
        rs1 = binToUnsigned(rs1)
        rd = binToUnsigned(rd)
        
        # if func3 == '000':
        #     iName = 'lb'
        # elif func3 == '001':
        #     iName = 'lh'
        if func3 == '010':
            iName = 'lw'
            if regi[rs1] + imm == 0x20000000:
                userInput = int(input())
                regi[rd] = userInput
            else:
                regi[rd] = data[int((regi[rs1] + imm - 0x10000000) / 4)]
        # elif func3 == '100':
        #     iName = 'lbu'
        # elif func3 == '101':
        #     iName = 'lhu'
        
        # if iName == 'unknown':
        #     return 'unknown instruction'
        # else:
        #     return f'{iName} x{rd}, {imm}(x{rs1})'
        pc = pc + 4
        return None
    # S format
    elif opcode == '0100011':
        imm1 = inst[0:7]
        rs2 = inst[7:12]
        rs1 = inst[12:17]
        func3 = inst[17:20]
        imm2 = inst[20:25]
        
        imm = imm1 + imm2
        imm = binToSigned(imm)
        imm = signExtend(imm, 12)
        rs2 = binToUnsigned(rs2)
        rs1 = binToUnsigned(rs1)
        
        # if func3 == '000':
        #     iName = 'sb'
        # elif func3 == '001':
        #     iName = 'sh'
        if func3 == '010':
            iName = 'sw'
            if regi[rs1] + imm == 0x20000000:
                print(chr(regi[rs2]), end = '')
            else:
                data[int((regi[rs1] + imm - 0x10000000) / 4)] = regi[rs2]
        
        # if iName == 'unknown':
        #     return 'unknown instruction'
        # else:
        #     return f'{iName} x{rs2}, {imm}(x{rs1})'
        pc = pc + 4
        return None
    # SB format
    elif opcode == '1100011':
        imm1 = inst[0]
        imm3 = inst[1:7]
        rs2 = inst[7:12]
        rs1 = inst[12:17]
        func3 = inst[17:20]
        imm4 = inst[20:24]
        imm2 = inst[24]
        
        imm = imm1 + imm2 + imm3 + imm4 + '0'
        imm = binToSigned(imm)
        imm = signExtend(imm, 13)
        rs2 = binToUnsigned(rs2)
        rs1 = binToUnsigned(rs1)
        
        if func3 == '000':
            iName = 'beq'
            if regi[rs1] == regi[rs2]:
                pc = pc + imm
            else:
                pc = pc + 4
        elif func3 == '001':
            iName = 'bne'
            if regi[rs1] != regi[rs2]:
                pc = pc + imm
            else:
                pc = pc + 4
        elif func3 == '100':
            iName = 'blt'
            if regi[rs1] < regi[rs2]:
                pc = pc + imm
            else:
                pc = pc + 4
        elif func3 == '101':
            iName = 'bge'
            if regi[rs1] >= regi[rs2]:
                pc = pc + imm
            else:
                pc = pc + 4
        # elif func3 == '110':
        #     iName = 'bltu'
        # elif func3 == '111':
        #     iName = 'bgeu'
        
        # if iName == 'unknown':
        #     return 'unknown instruction'
        # else:
        #     return f'{iName} x{rs1}, x{rs2}, {imm}'
        return None
    # UJ format
    elif opcode == '1101111':
        imm1 = inst[0]
        imm4 = inst[1:11]
        imm3 = inst[11]
        imm2 = inst[12:20]
        rd = inst[20:25]
        
        imm = imm1 + imm2 + imm3 + imm4 + '0'
        imm = binToSigned(imm)
        imm = signExtend(imm, 21)
        rd = binToUnsigned(rd)
        
        iName = 'jal'
        regi[rd] = pc + 4
        pc = pc + imm
        # return f'{iName} x{rd}, {imm}'
        return None
    elif opcode == '1100111':
        imm = inst[0:12]
        rs1 = inst[12:17]
        func3 = inst[17:20]
        rd = inst[20:25]
        
        imm = binToSigned(imm)
        imm = signExtend(imm, 12)
        rs1 = binToUnsigned(rs1)
        rd = binToUnsigned(rd)
        
        if func3 == '000':
            iName = 'jalr'
            regi[rd] = pc + 4
            pc = regi[rs1] + imm
        # if iName == 'unknown':
        #     return 'unknown instruction'
        # else:
        #     return f'{iName} x{rd}, {imm}(x{rs1})'
        return None
    # U format
    elif opcode == '0110111' or opcode == '0010111':
        imm = inst[0:20]
        rd = inst[20:25]
        
        imm = imm + '000000000000'
        imm = binToSigned(imm)
        rd = binToUnsigned(rd)
        
        if opcode == '0110111':
            iName = 'lui'
            regi[rd] = imm
        else:
            iName = 'auipc'
            regi[rd] = pc + imm
        # return f'{iName} x{rd}, {imm}'
        pc = pc + 4
        return None
    else:
        return 'unknown instruction'

# excuting
while count > 0 and pc <= pcMax:
    riscvInstruction(instructions[int(pc/4)])
        # python은 자료형을 명시적으로 표현하지 않아서 이렇게 해줘야 음수일 때 앞이 1인 32비트가 유지됨.
    regi[0] = 0x00000000
    for i in range(1, 32):
        regi[i] = regi[i] & 0xffffffff
    count -= 1

#result
for i in range(32):
    print(f"x{i}: 0x{regi[i]:08x}")