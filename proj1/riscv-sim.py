import sys
fName = sys.argv[1]

with open(fName, 'rb') as file:
    byteData = file.read() # bytes 객체

    # instruction을 2진수 string으로
    binDataString = [format(byte, '08b') for byte in byteData]
    binToWordList = [binDataString[i:i+4] for i in range(0, len(binDataString), 4)]
    instructionsEn= [''.join(binByte) for binByte in binToWordList]
    instructionsDian = [i[::-1] for i in instructionsEn]
    instructions = []
    for i in instructionsDian:
        swapped = ''
        for j in range(0,32,8):
            swapped += i[j+7] + i[j+6] + i[j+5] + i[j+4] + i[j+3] + i[j+2] + i[j+1] +i[j]
        instructions.append(swapped)

    # instruction을 16진수 string으로
    hexDataString = [format(byte, '02x') for byte in byteData]
    hexToWordList = [hexDataString[i:i+4] for i in range(0, len(hexDataString), 4)]
    instructionsHEn = [''.join(hexByte) for hexByte in hexToWordList]
    instructionsHDian = [i[::-1] for i in instructionsHEn]
    instructionsH = []
    for i in instructionsHDian:
        swapped = ''
        for j in range(0,8,2):
            swapped += i[j+1] + i[j]
        instructionsH.append(swapped)

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

def riscvInstruction(inst: str):
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
            elif func7 == '0100000':
                iName = 'sub'
        elif func3 == '001':
            if func7 == '0000000':
                iName = 'sll'
        elif func3 == '010':
            if func7 == '0000000':
                iName = 'slt'
        elif func3 == '011':
            if func7 == '0000000':
                iName = 'sltu'
        elif func3 == '100':
            if func7 == '0000000':
                iName = 'xor'
        elif func3 == '101':
            if func7 == '0000000':
                iName = 'srl'
            elif func7 == '0100000':
                iName = 'sra'
        elif func3 == '110':
            if func7 == '0000000':
                iName = 'or'
        elif func3 == '111':
            if func7 == '0000000':
                iName = 'and'
        
        if iName == 'unknown':
            return 'unknown instruction'
        else:
            return f'{iName} x{rd}, x{rs1}, x{rs2}'
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
            else:
                if func7 == '0000000':
                    iName = 'srli'
                elif func7 == '0100000':
                    iName = 'srai'
            
            if iName == 'unknown':
                return 'unknown instruction'
            else:
                return f'{iName} x{rd}, x{rs1}, {shamt}'
        else:
            imm = inst[0:12]
            rs1 = inst[12:17]
            rd = inst[20:25]
            
            imm = binToSigned(imm)
            rs1 = binToUnsigned(rs1)
            rd = binToUnsigned(rd)
            
            if func3 == '000':
                iName = 'addi'
            elif func3 == '010':
                iName = 'slti'
            elif func3 == '011':
                iName = 'sltiu'
            elif func3 == '100':
                iName = 'xori'
            elif func3 == '110':
                iName = 'ori'
            elif func3 == '111':
                iName = 'andi'
            
            if iName == 'unknown':
                return 'unknown instruction'
            else:
                return f'{iName} x{rd}, x{rs1}, {imm}'
    # I format(load)
    elif opcode == '0000011':
        imm = inst[0:12]
        rs1 = inst[12:17]
        func3 = inst[17:20]
        rd = inst[20:25]
        
        imm = binToSigned(imm)
        rs1 = binToUnsigned(rs1)
        rd = binToUnsigned(rd)
        
        if func3 == '000':
            iName = 'lb'
        elif func3 == '001':
            iName = 'lh'
        elif func3 == '010':
            iName = 'lw'
        elif func3 == '100':
            iName = 'lbu'
        elif func3 == '101':
            iName = 'lhu'
        
        if iName == 'unknown':
            return 'unknown instruction'
        else:
            return f'{iName} x{rd}, {imm}(x{rs1})'
    # S format
    elif opcode == '0100011':
        imm1 = inst[0:7]
        rs2 = inst[7:12]
        rs1 = inst[12:17]
        func3 = inst[17:20]
        imm2 = inst[20:25]
        
        imm = imm1 + imm2
        imm = binToSigned(imm)
        rs2 = binToUnsigned(rs2)
        rs1 = binToUnsigned(rs1)
        
        if func3 == '000':
            iName = 'sb'
        elif func3 == '001':
            iName = 'sh'
        elif func3 == '010':
            iName = 'sw'
        
        if iName == 'unknown':
            return 'unknown instruction'
        else:
            return f'{iName} x{rs2}, {imm}(x{rs1})'
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
        rs2 = binToUnsigned(rs2)
        rs1 = binToUnsigned(rs1)
        
        if func3 == '000':
            iName = 'beq'
        elif func3 == '001':
            iName = 'bne'
        elif func3 == '100':
            iName = 'blt'
        elif func3 == '101':
            iName = 'bge'
        elif func3 == '110':
            iName = 'bltu'
        elif func3 == '111':
            iName = 'bgeu'
        
        if iName == 'unknown':
            return 'unknown instruction'
        else:
            return f'{iName} x{rs1}, x{rs2}, {imm}'
    # UJ format
    elif opcode == '1101111':
        imm1 = inst[0]
        imm4 = inst[1:11]
        imm3 = inst[11]
        imm2 = inst[12:20]
        rd = inst[20:25]
        
        imm = imm1 + imm2 + imm3 + imm4 + '0'
        imm = binToSigned(imm)
        rd = binToUnsigned(rd)
        
        iName = 'jal'
        return f'{iName} x{rd}, {imm}'
    elif opcode == '1100111':
        imm = inst[0:12]
        rs1 = inst[12:17]
        func3 = inst[17:20]
        rd = inst[20:25]
        
        imm = binToSigned(imm)
        rs1 = binToUnsigned(rs1)
        rd = binToUnsigned(rd)
        
        if func3 == '000':
            iName = 'jalr'
        
        if iName == 'unknown':
            return 'unknown instruction'
        else:
            return f'{iName} x{rd}, {imm}(x{rs1})'
    # U format
    elif opcode == '0110111' or opcode == '0010111':
        imm = inst[0:20]
        rd = inst[20:25]
        
        imm = imm + '000000000000'
        imm = binToSigned(imm)
        rd = binToUnsigned(rd)
        
        if opcode == '0110111':
            iName = 'lui'
        else:
            iName = 'auipc'
        return f'{iName} x{rd}, {imm}'
    else:
        return 'unknown instruction'

for i in range(len(instructions)):
    print(f'inst {i}: {instructionsH[i]}', end=' ')
    print(riscvInstruction(instructions[i]))