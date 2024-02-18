/* 

This calculates and displays Fibonacci numbers

Notice the use of the split instruction to write a value into 
some instructions' input and its succeeding instructions' input.

*/

loopstart: 
    write prev=0 -> &prev_copy;
    write curr=1 -> &prev;
    add curr_copy prev_copy -> &next;

    split next -> &next_copy;
    split next_copy -> &curr;
    split _ -> &to_disp;

    /*we do this xor stuff since the display instruction works using toggles.*/
    xor prev_disp=0 to_disp -> &disp;
    write _ -> &prev_disp;
    display disp;

goto &loopstart;
