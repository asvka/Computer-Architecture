import sys


class CPU:
    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.sp = 7
        self.running = True
        self.pc = 0
        self.flag = 0b00000000
        self.branch_table = {
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b00000001: self.HLT,
            0b10100010: self.MUL,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b00010001: self.RET,
            0b01010000: self.CALL,
            0b10100000: self.ADD,
            0b10100111: self.CMP,
            0b01010100: self.JMP,
            0b01010110: self.JNE,
            0b01010101: self.JEQ,
        }

    def LDI(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.reg[operand_a] = operand_b
        self.pc += 3

    def HLT(self):
        self.running = False
        self.pc += 1

    def PRN(self):
        operand_a = self.ram_read(self.pc + 1)
        print(self.reg[operand_a])
        self.pc += 2

    def MUL(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu('MUL', operand_a, operand_b)
        self.pc += 3

    def PUSH(self):
        reg_index = self.ram_read(self.pc + 1)
        self.reg[self.sp] -= 1
        self.ram_write(self.reg[self.sp], self.reg[reg_index])
        self.pc += 2

    def POP(self):
        reg_index = self.ram_read(self.pc + 1)
        self.reg[reg_index] = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1
        self.pc += 2

    def CALL(self):
        given_reg = self.ram[self.pc + 1]
        self.sp -= 1
        self.ram[self.sp] = self.pc + 2
        self.pc = self.reg[given_reg]

    def RET(self):
        self.pc = self.ram[self.sp]
        self.reg[7] += 1

    def ADD(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu('ADD', operand_a, operand_b)
        self.pc += 3

    def CMP(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu('CMP', operand_a, operand_b)
        self.pc += 3

    def JMP(self):
        reg_index = self.ram_read(self.pc + 1)
        self.pc = self.reg[reg_index]

    def JEQ(self):
        if self.flag == 0b00000001:
            reg_index = self.ram_read(self.pc + 1)
            self.pc = self.reg[reg_index]
        else:
            self.pc += 2

    def JNE(self):
        if self.flag != 0b00000001:
            reg_index = self.ram_read(self.pc + 1)
            self.pc = self.reg[reg_index]
        else:
            self.pc += 2

    def load(self):
        address = 0
        if len(sys.argv) != 2:
            print(f'Usage: {sys.argv} filename')
            sys.exit(1)
        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    split_line = line.split('#')
                    value = split_line[0].strip()
                    if value == '':
                        continue
                    num = int(value, 2)
                    print(num)
                    self.ram[address] = num
                    address += 1
        except FileNotFoundError:
            print(f'{sys.argv[1]} not found')
            sys.exit(2)

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def alu(self, op, reg_a, reg_b):
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'DIV':
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 0b00000001
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000010
            if self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b00000011
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        while self.running:
            IR = self.ram_read(self.pc)

            if IR in self.branch_table:
                self.branch_table[IR]()