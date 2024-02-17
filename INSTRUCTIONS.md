The memory is basically a list of 32-bit 2's complement integers, like [0,0,4,5] with 0 based indexing.

Address 0 is inaccessable. Execution starts by running the instruction at address 2.

## Instruction Format

Each instruction consists of the following numbers in memory in this orer:  (the last three parts are optional)

`<next-instruction> <opcode> [output] [input1] [input2]`

So every instruction takes up 2-5 spaces in memory.

### Next instruction
This basically tells the processor which instruction to execute next. It points to the starting location of the next instruction. Since every instruction has this, jumps are practically free.

This part is also what allows it to support variable length instruction without any extra complications.
### Opcode

Here is the list of currently supported opcode:

opcode | name  | inputs unused          | description | 
|---|---|---|---|
|0|nop    | output, input1, input2| does nothing. <p> In some cases, useful as a jump instruction |
|1|inc| input2 | writes input value +1 to output location
|2| write | input2 | writes value in input1 to output location
|3| add | | writes sum of input values to output location
|4| xor | |bitwise xor of inputs
|5| cmov || if input2 &ge; 0, then it writes value in input1 to output
|6| and || bitwise and of inputs
|7| shr | input2 | writes input value logically right shifted by one bit to the output location
|8| split | input2| writes value in input1 to output location and the output location plus 4. For example, if output=5, then it writes input1 to memory location 5 and 9. <p> This may seem arbitrary, but it turns out to be very useful while coding
|9| display| output, input2| toggles the pixels in the display corresponding to the set bits in input1. <p> To use this to display some number, you will probably need to clear the display or use xor to determine which bits to togglr 

### Output

It is the address where the instruction has to write its output. Other than in `split`, this is not used for anything else.

### Input[1,2]

It contains the input as values. 

It is very important to note that the values are directly used, and that it does not specify the address of the instructions. Or in other words, it only supports the immediate addressing mode.

 This also means that reading arbritrary memory locations is non-trivial.


--------------------
Coding using this is extremely inconvenient for obvious reasons. To simplify coding, use the assembler and the language outline in [ASSEMBLY.md](ASSEMBLY.md)