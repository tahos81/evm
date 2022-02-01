class Stack:
    def __init__(self, max_depth=1024) -> None:
        self.stack = []
        self.max_depth = max_depth

    def push(self, item: int) -> None:
        if item < 0 or item > 2 ** 256 - 1:
            raise Exception({"item": item})

        if (len(self.stack) + 1) > self.max_depth:
            raise Exception()

        self.stack.append(item)

    def pop(self) -> int:
        if len(self.stack) == 0:
            raise Exception()

        return self.stack.pop()
    
    def __str__(self) -> str:
        return str(self.stack)

    def __repr__(self) -> str:
        return str(self)

class Memory:
    def __init__(self) -> None:
        self.memory = []

    def store(self, offset: int, value: int) -> None:
        if offset < 0 or offset > 2**256 - 1:
            raise Exception({"offset": offset, "value": value})

        if value < 0 or value > 2**8-1:
            raise Exception({"offset": offset, "value": value})

        if offset >= len(self.memory):
            self.memory.extend([0] * (offset - len(self.memory) + 1))

        self.memory[offset] = value

    def load(self, offset: int) -> int:
        if offset < 0:
            raise Exception({"offset": offset})

        if offset >= len(self.memory):
            return 0

        return self.memory[offset]
    
    def __str__(self) -> str:
        return str(self.memory)

    def __repr__(self) -> str:
        return str(self)

class ExecutionContext:
    def __init__(self, code=bytes(), pc=0, stack=Stack(), memory=Memory()) -> None:
        self.code = code
        self.stack = stack
        self.memory = memory
        self.pc = pc
        self.stopped = False

    def stop(self) -> None:
        self.stopped = True

    def read_code(self, num_bytes) -> int:
        value = int.from_bytes(self.code[self.pc : self.pc + num_bytes], byteorder="big")
        self.pc += num_bytes
        return value
    
    def __str__(self) -> str:
        return "stack: " + str(self.stack) + "\nmemory: " + str(self.memory)

    def __repr__(self) -> str:
        return str(self)

class Instruction:
    def __init__(self, opcode: int, name: str) -> None:
        self.opcode = opcode
        self.name = name
        
    def execute(self, context: ExecutionContext) -> None:
        raise Exception()
    
    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name
    
INSTRUCTIONS = []
INSTRUCTIONS_BY_OPCODE = {}

def register_instruction(opcode: int, name: str, execute_func: callable):
    instruction = Instruction(opcode, name)
    instruction.execute = execute_func 
    INSTRUCTIONS.append(instruction)

    assert opcode not in INSTRUCTIONS_BY_OPCODE
    INSTRUCTIONS_BY_OPCODE[opcode] = instruction

    return instruction

STOP = register_instruction(0x00, "STOP", (lambda ctx: ctx.stop()))
PUSH1 = register_instruction(
    0x60, 
    "PUSH1", 
    (lambda ctx: ctx.stack.push(ctx.read_code(1)))
)
ADD = register_instruction(
    0x01,
    "ADD",
    (lambda ctx: ctx.stack.push((ctx.stack.pop() + ctx.stack.pop()) % 2 ** 256))
)
MUL = register_instruction(
    0x02,
    "MUL",
    (lambda ctx: ctx.stack.push((ctx.stack.pop() * ctx.stack.pop()) % 2 ** 256)),
)
MSTORE8 = register_instruction(
    0x53,
    "MSTORE8",
    (lambda ctx: ctx.memory.store(ctx.stack.pop(), ctx.stack.pop() % 256)),
)
RETURN = register_instruction(
    0xF3,
    "RETURN",
    (lambda ctx: ctx.set_return_data(ctx.stack.pop(), ctx.stack.pop())),
)

def decode_opcode(context: ExecutionContext) -> Instruction:
    if context.pc < 0 or context.pc >= len(context.code):
        raise Exception({"code": context.code, "pc": context.pc})
    
    opcode = context.read_code(1)
    instruction = INSTRUCTIONS_BY_OPCODE.get(opcode)
    if instruction is None:
        raise Exception({"opcode": opcode})

    return instruction

def run(code: bytes) -> None:
    """
    Executes code in a fresh context.
    """
    context = ExecutionContext(code=code)

    while not context.stopped:
        pc_before = context.pc
        instruction = decode_opcode(context)
        instruction.execute(context)

        print(f"{instruction.name} @ pc={pc_before}")
        print(context)
        print()

def main():
    data = "600460015300"
    run(bytes.fromhex(data))

main()