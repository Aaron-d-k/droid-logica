The memory is basically a list of 32-bit 2's complement integers, like [0,0,4,5]

Address 0 is inaccessable and execution starts at address 2.

## Instruction Format

TODO: describe layout

## List of opcodes

| code  | inputs unused          | description | 
|---|---|---|
|nop    | output, input1, input 2| does nothing. <p> useful as a jump instruction |
| write | input2 | writes value in input1 to output
TODO: complete table
