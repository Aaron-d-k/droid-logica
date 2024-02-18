/*

This is a program to display prime numbers.
It proceeds by the naive algorithm.
Most of the code here is used to find modulo using bitwise operations

*/

notprime:
    add currnumcand=3 _=2 -> &currnumcand2;
    split currnumcand2 -> &currnumcand3;
    split currnumcand3 -> &currnumcand4;

    write _ -> &nextdisp;
    write currnumcand4 -> &currnumcand;
    split candidate -> &num;

    shr num -> &num_copy1;
    write _ -> &n;


    write _=1 -> &currfactor;


    factorloop:

        inc currfactor -> &nextfactor;

        split nextfactor -> &nextfactor2;
        split nextfactor2 -> &nextfactor3;
        write _ -> &currfactor;
        write nextfactor3 -> &d;
        xor nextfactor4 _=-1 -> &neg_nextfactor;
        add neg_nextfactor num_copy1 -> &isdivesrem;
        
        write _=&prime -> &factorloopcond;
        cmov _=&modfindingstart isdivesrem -> &factorloopcond;

        factorloopcond: nop;

        modfindingstart:

        xor n _=-1 -> &neg_n_left_m1__1;
        split neg_n_left_m1__1 -> &nnlm1_2;

        write nnlm1_2 -> &neg_n_left_m1;
        inc _ -> &neg_n1;


        write d -> &nextmul;
        write _=-2 -> &i1;


        write _=&nmc -> &mulcopy;
        write _=&currmul_c3 -> &mulcopy+2;

        write _=&loop1 -> &loop1count;
        write _=&i1 -> &loop1count+2;


        loop1: 
            
            split nextmul -> &cmpmul;

            add neg_n1 cmpmul -> &muldiff;

            split currmul -> &currmul_c1;

            cmov _=&endloop1 muldiff -> &mulcopy;


            mulcopy: write currmul_c1 -> &currmul_c3;

            nmc: add currmul_c2 currmul_c3 -> &nextmul;

            loop1count: inc i1 -> &i1;

        goto &loop1;

        endloop1:
        /* we will extract values from loop by modifying the code*/
        write _=&loop1count -> &mulcopy;
        write _=&shifted_d -> &mulcopy+2;

        write _=&divpart2 -> &loop1count;
        write _=&shiftlen -> &loop1count+2;
        goto &mulcopy;

        divpart2:
        /* now onto the actual modulo part -- subtract in loop*/

        xor shiftlen _=-1 -> &shiftlen2;
        split shiftlen2 -> &chk_len;

        write _=&loopvarsp -> &loopvar;

        write _=&l2c -> &addshr+2;
        write _=&addshrn -> &addshr;

        loop2:
            cmov _=&enddiv chk_len -> &loopvar;

            loopvar: inc shiftlen3 -> &rem_len;

            loopvarsp: split rem_len -> &chk_len; 
            goto &divshr;

            splitshr: split new_shifted_d -> &shifted_d;
            goto &addshr;

            divshr: shr shifted_d -> &new_shifted_d;
            goto &splitshr;

            addshr: add new_shifted_d1 neg_n_left_m1 -> &l2c;

            addshrn: split l2c -> &l2cc;

            write _=&acsubber -> &subber;
            cmov _=&loop2 l2cc -> &subber;

            goto &subber;

            acsubber: write _ -> &neg_n_left_m1;
        goto &loop2;


            subber: nop;
            goto &acsubber;


        enddiv:

        write _=0 -> &new_shifted_d1;
        
        write _=&divrem -> &addshr+2;
        write _=&divfinal -> &addshr;
        goto &addshr;

        divfinal:

        xor divrem _=-1 -> &ans;

        add ans _=-1 -> &isnotdiv;

        write _=&notprime -> &factorloopend;
        cmov _=&factorloop isnotdiv -> &factorloopend;

    factorloopend: nop;


    prime:
    
    write currdisp=0 -> &pdisp;
    split nextdisp -> &nextdisp2;
    write nextdisp2 -> &currdisp;
    xor _ pdisp -> &disp;
    display disp;
    goto &notprime;

