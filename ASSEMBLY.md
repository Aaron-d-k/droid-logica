(Read [INSTRUCTIONS.md](INSTRUCTIONS.md) first in order to understand this properly)

# Assembly Syntax
The assembly language is a very low level wrapper over the machine code, so there is a one-to-one correspondence between each statement in the assembly language and each instruction in the machine code. This language supports `/*c-style comments*/`.

Any piece of code consists of many lines separated by semicolons. Each line can have 3 parts: a label, the instruction (optionally with input and outputs), and the next instruction. Both the first and third part are optional.

An example of a line with all the parts are:

`label_for_instuction: add inp1=-1 inp2=5 -> &outp ; goto &label_for_next_instruction;`

or a minimalistic display instruction:

`display to_disp;`

### The Label
Each instruction may optionally have a label, which can be used to refer to the starting memory location of the instruction in any other instruction.

The label is separated from the rest of the stuff by a colon. Every label can be later referred only as `&label` or `&label + <offset>`.

### Goto
It comes after a semicolon at the end of the instruction. It is optional. If not given, then the next instruction in code is assumed to be executed next.

### The main part of the instruction

This has 3 parts: an opcode, inputs and outputs.

The opcode is a name corresponding to each instruction. This part is compulsory. A list of valid opcodes can be found [here](INSTRUCTIONS.md).

The inputs and outputs are optional. Each input has 2 parts separated by `=`: a label and an initial value. The initial value is optional, but the label is compulsory. The label can be set to `_` if you need a placeholder label.

The initial value can either be a number, or it can be the label of some instruction or the input to some other instruction.

The output is separated from the inputs by a `->`. It refers to some label, which can either be the label of some instruction (for self modifying code), or the label of some input in some instruction.

## Example code

This code adds 3 and 4 and displays the result:
```
add _=3 _=4 -> to_display;
display to_display;
```

For a more advanced example, check out [fibonacci.s](scripts/assembler/fibonacci.s).


