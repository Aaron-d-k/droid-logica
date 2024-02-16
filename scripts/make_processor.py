
from copy import copy
import random
import math
from functools import lru_cache
import sys

from assembler import assembler

import lifelib

sess = lifelib.load_rules('g4b2s345')
lt = sess.lifetree()

star = lt.pattern('bo$3o$bo')
ship = lt.pattern('CBA$CBA!')

@lru_cache
def make_strip(l):
    if l < 0:
        raise ValueError
    o = lt.pattern()
    for i in range(l+1):
        o += star(0,i*3)
    return o

@lru_cache
def make_delay(d,h):
    if d < 0 or d == 1 or h <= 0:
        raise ValueError
    if d==0:
        return lt.pattern()
    
    w = d//(2+6*h)
    o = lt.pattern()
    hlongstrip = make_strip(h)
    if w > 0:
        for i in range(w-1):
            o |= (hlongstrip(i*14,0)|hlongstrip(i*14+7,-1))

        drem = d % (2+6*h)
        if drem == 1:
            o |= (make_strip(h-1)((w-1)*14,0)|make_strip(h-1)((w-1)*14+7,-1))
            o |= lt.pattern('.A$3A$.A11.A11.A$.A5.A4.3A4.A4.3A$3A3.3A4.A4.3A4.A$.A5.A11.A!')(w*14,-3)
            return o
        o |= (hlongstrip((w-1)*14,0)|hlongstrip((w-1)*14+7,-1))
        if drem == 0:
            return o
    else:
        drem = d
    lastheight = (drem-2)//6
    drem = (drem-2) % 6
            
    if drem == 0:
        rfd = lt.pattern()
    if drem == 1:
        if lastheight == 0:
            o |= lt.pattern('.A$3A$.A$.A$3A$.A!')(w*14,-3)
            return o
        lastheight -= 1;
        rfd = lt.pattern('.A$3A$.A11.A11.A$.A5.A4.3A4.A4.3A$3A3.3A4.A4.3A4.A$.A5.A11.A!')
    if drem == 2:
        rfd = lt.pattern('2$7.A$.A4.3A$3A4.A$.A!')
    if drem == 3:
        rfd = lt.pattern('.A$3A$.A$.A$3A$.A!')
    if drem == 4:
        rfd = lt.pattern('2$7.A11.A$.A4.3A4.A4.3A$3A4.A4.3A4.A$.A11.A!')
    if drem == 5:
        rfd = lt.pattern('.A$3A$.A11.A$.A5.A4.3A$3A3.3A4.A$.A5.A!')
    
    o |= (make_strip(lastheight)(w*14,0)|make_strip(lastheight)(w*14+7,-1))
    o |= rfd((w+1)*14,-3)
    return o

def _make_serial_to_unsync_parallel(lngth,distbwoutp,distbwser,distbwinp,addtimesig,delayinps=0):
    splittr = lt.pattern('.A2.A15.A$6A13.3A$.A3.2A7.A5.A$.A4.2A5.3A$2A5.2A5.A$.A5.A6.A$.A5.A5.3A$9A5.A$.A2.A2.A!')
    o = lt.pattern()
    maxl = 0
    for i in range(1,lngth+1):
        o |= splittr(i*distbwoutp,0) 
        o |= splittr(i*distbwoutp-9,-distbwinp)
        delay = make_delay(distbwser*(lngth-i)+distbwoutp-distbwinp,distbwoutp//3 - 5)
        if delay.nonempty():
            maxl = max(maxl, delay.bounding_box[2])
        o |= delay('rot270')(i*distbwoutp-7,20)
    
    
    for i in range(1,lngth+1):
        o |= lt.pattern('17.A2.A2.A$16.9A$17.A2.A2.A5$16.A2.A2.A$15.9A$16.A2.A2.A5$14.A2.A$13.6A$14.A2.A4$16.A$6.A8.3A$5.3A8.A$6.A2$2.A$.3A$2.A!')(i*distbwoutp-13,maxl+20)

    d = make_delay(distbwoutp-9+delayinps, distbwinp//3 - 4)
    o |= d('flip_y')(distbwoutp-d.bounding_box[2]-10,0)
    
    if delayinps != 0:
        d = make_delay(delayinps, distbwinp//3 - 4)
        o |= d('flip_y')(distbwoutp-d.bounding_box[2]-15,-distbwinp)
    
    if addtimesig:
        o |= lt.pattern('5.A$4.3A$5.A2$.A$3A$.A!')(distbwoutp*(lngth+1)+2, -distbwinp-5)
    else:
        o |= star(distbwoutp*lngth+25, -distbwinp)

    o |= star(distbwoutp*lngth+25, 0)
    
    return (o,maxl)
    
def make_serial_to_unsync_parallel(lngth,distbwoutp,distbwser,distbwinp,addtimesig):
    return _make_serial_to_unsync_parallel(lngth,distbwoutp,distbwser,distbwinp,addtimesig)[0]

def make_timed_serial_to_parallel(lngth,distbwoutp,distbwser,distbwinp,outpdelays,addtimesig,delayinps=0):
    o, maxl = _make_serial_to_unsync_parallel(lngth,distbwoutp,distbwser,distbwinp,addtimesig,delayinps)
    if len(outpdelays) != lngth:
        raise ValueError
    if addtimesig:
        for i in range(1,lngth+1):
            o |= make_delay((11+distbwoutp-distbwser)*(lngth-i)+distbwinp-6+outpdelays[i-1], distbwoutp//3 - 5)('rot270')(i*distbwoutp+2,maxl+60)
    else:
        for i in range(1,lngth+1):
            o |= make_delay((11+distbwoutp-distbwser)*(lngth-i)+outpdelays[i-1], distbwoutp//3 - 5)('rot270')(i*distbwoutp+2,maxl+60)

    return o

def make_serial_to_parallel(lngth,distbwoutp,distbwser,distbwinp,addtimesig=True,delayinps=0): 
    return make_timed_serial_to_parallel(lngth,distbwoutp,distbwser,distbwinp,[0,]*lngth,addtimesig,delayinps=delayinps)

def make_parallel_to_serial(lngth,distbwinp,distbwser,distbwoutp,inpdelays=None,timerdelay=0,maxinpdelwidth=math.inf):
    o = lt.pattern()
    if inpdelays is None:
        indelay = [0,]*lngth
    elif len(inpdelays)==lngth:
        indelay = inpdelays
    else:
        raise ValueError
    
    inpdelwidth = min(maxinpdelwidth,distbwinp)//3 - 4
    
    mindel = distbwoutp+distbwser-14+(5+distbwinp-distbwser)*lngth+timerdelay
    for i in range(lngth):
        mindel = min(mindel,(5+distbwinp-distbwser)*i+indelay[i])
        
    for i in range(lngth):
        o += lt.pattern('8.A$7.3A5.A$.A6.A5.3A$3A12.A$.2A.A$.A.3A$.2A.A$3A$.A!')(i*distbwinp,0)
        d = make_delay((5+distbwinp-distbwser)*i+indelay[i]-mindel,inpdelwidth)
        if d.nonempty():
            o += d('rot270')(i*distbwinp-1,-5-d.bounding_box[2])
    o += lt.pattern('5.A$4.3A$5.A2$.A$3A$.A!')(lngth*distbwinp-6,2-distbwoutp)
    d = make_delay(distbwoutp+distbwser-14+(5+distbwinp-distbwser)*lngth+timerdelay-mindel,inpdelwidth)
    o += d('rot270')(lngth*distbwinp-1,-distbwoutp-5-d.bounding_box[2])
    return o

def make_rand_data(distbw,lngth,distbwserwire):
    o = lt.pattern()
    for i in range(lngth):
        if random.choice([True, ]):
            o += ship(i*distbw,0)
    o+= ship((lngth-1)*distbw,distbwserwire)
    return o
   
def make_temp_register(lngth,distbwserwire,distbwser,distbwparrwire):
    memcell = lt.pattern('''B97.B$30.A2.A15.A$29.6A13.3A$B29.A3.2A7.A5.A48.B$30.A4.2A5.3A$29.2A5.
2A5.A$30.A5.A6.A$30.A5.A5.3A$29.9A5.A$30.A2.A2.A7$56.A$36.A2.A10.A4.
3A14.A$35.6A8.3A4.A14.3A$36.A2.A10.A5.A15.A$36.A2.A10.A4.3A$35.6A8.3A
4.A11.A$36.A2.A10.A5.A10.3A$20.A5.A9.A2.A10.A4.3A4.A5.A$19.9A7.6A8.3A
4.A4.3A$20.A2.A2.A9.A2.A10.A11.A$36.A2.A$35.6A$36.A2.A$54.A$48.A4.3A$
47.3A4.A31.B2.B$48.A5.A$48.A4.3A$47.3A4.A$48.A5.A$48.A4.3A$47.3A4.A$
48.A5.A12.A7.A9.A6.A$48.A4.3A10.3A5.3A7.3A4.3A$47.3A4.A12.A7.A9.A6.A$
48.A5.A$9.A12.A25.A4.3A7.A17.A$8.3A10.3A23.3A4.A7.3A15.3A$9.A12.A8.A
16.A14.A17.A$30.3A$31.A6$63.A$53.A8.3A$10.A18.A22.3A8.A$9.3A16.3A22.A
$10.A18.A37.A$66.3A$14.A10.A41.A10.A$13.3A8.3A50.3A$14.A10.A52.A2$74.
A$73.3A$74.A$14.A$13.3A$14.A2$10.A$9.3A$10.A3$72.B2.B!''')
    o = lt.pattern()
    for i in range(lngth):
        o += memcell(i*distbwparrwire,0)
    o |= lt.pattern('5.A$4.3A$5.A2$.A$3A$.A!')(distbwparrwire*lngth+73, -4)
    ptos = make_parallel_to_serial(lngth,distbwparrwire,distbwser,distbwserwire,inpdelays=[(11+distbwparrwire)*(lngth-i) for i in range(1,lngth+1)],timerdelay=83-distbwparrwire)
    o+=ptos(74,80+ptos.bounding_box[3])
    
    s_to_p = make_serial_to_unsync_parallel(lngth,distbwparrwire,distbwser,distbwserwire, False)
    o+= s_to_p(85-distbwparrwire, 50-s_to_p.bounding_box[3])
    
    return o

#i figured out wtf extraunitdelay is
#its supposed to slow down the traversal of the demux from bottom to top of the spaceship
# so it slows down memory access

#delayoutps just delays the ouput by few steps
def make_demux(lngth_addr,demux_lngth,distbwserwire,distbwser,distbwparrwire,distbwdemuxunit,extraunitdelay=0,delayoutps=0):
    extradelay = make_delay(extraunitdelay,max(4,distbwparrwire//4-5))('rot90')(1,-40)
    det0 = lt.pattern('''.A$3A$.A4$3.A2.A$2.6A$3.A2.A5$4.A2.A10.A$3.6A8.3A$2.2A3.A10.A$.2A4.A$
2A5.2A5.A$.A5.A5.3A$.A5.A6.A$9A$.A2.A2.A4$20.A$19.3A$20.A$20.A$19.3A$
20.A$14.A$13.3A$14.A!''')|extradelay
    det1 = lt.pattern('''.A$3A$.A4$3.A2.A$2.6A$3.A2.A5$4.A2.A10.A$3.6A8.3A$2.2A3.A10.A$.2A4.A$
2A5.2A5.A$.A5.A5.3A$.A5.A6.A$9A$.A2.A2.A4$20.A$19.3A4.A$13.A6.A4.3A$
12.3A11.A$13.A!''')|extradelay
    splt = lt.pattern('''
.A$3A$.A4$3.A2.A$2.6A$3.A2.A5$4.A2.A$3.6A$2.2A3.A$.2A4.A$2A5.2A$.A5.A
$.A5.A$9A$.A2.A2.A!''')|extradelay
    o=lt.pattern()
    for i in range(demux_lngth):
        n = bin(i).zfill(lngth_addr)
        for j in range(lngth_addr):
            o+= (det1 if n[lngth_addr-j-1] == '1' else det0)(j*distbwparrwire,-i*distbwdemuxunit)
        o+= splt(-distbwparrwire,9-i*distbwdemuxunit)
        
    s_to_p = make_timed_serial_to_parallel(lngth_addr,distbwparrwire,distbwser,distbwserwire,[(lngth_addr-k)*(distbwparrwire+3)-29 for k in range(lngth_addr)],addtimesig=True,delayinps=delayoutps)
    s_to_p = s_to_p('rot180')(3+lngth_addr*distbwparrwire, s_to_p.bounding_box[3])
    o+= s_to_p
    for j in range(-1,lngth_addr):
        o += star(j*distbwparrwire,-demux_lngth*distbwdemuxunit)
    return o

def make_turn(thepath,distbwwire,numwire=2):
    refl = lt.pattern('.A$3A$.A2$5.A$4.3A$5.A!')
    reflw = lt.pattern()
    for i in range(numwire):
        if thepath[0] == 'r' :
            reflw |= refl(i*distbwwire,-i*distbwwire) 
        elif thepath[0] == 'l':
            reflw |= refl('flip_x')(i*distbwwire+11,-(numwire-1-i)*distbwwire)
        elif thepath[0] == 'm':#wierd l
            reflw |= refl('flip_x')(i*distbwwire+11,-i*distbwwire)
        elif thepath[0] == 's':#wierd r
            reflw |= refl(i*distbwwire,-(numwire-1-i)*distbwwire) 
        else:
            raise ValueError
            
    if len(thepath) > 1:
        if thepath[1:]=='s':
            reflw = reflw(2,0)
        else:
            raise ValueError

    return reflw 
    
#bugs: address 0 is write only
#pls don't try to fix
#it will most likely break something else
def make_ram(data,lngth_dataword,lngth_addr,distbwparrwire,distbwserwire,distbwser,demux_distbwparrwire,distbwramunit,write_stp_make_lower_by=0):
    ram_unit0 = lt.pattern('''87.C2.C29.C2.C6$C126.C$13.A2.A15.A$12.6A13.3A$C12.A3.2A7.A5.A94.C$13.
A4.2A5.3A$12.2A5.2A5.A10.A13.A$13.A5.A6.A9.3A5.A5.3A5.A$13.A5.A5.3A9.
A5.3A5.A5.3A$12.9A5.A10.A6.A6.A6.A$13.A2.A2.A16.3A5.A5.3A5.A$37.A5.3A
5.A5.3A$37.A6.A6.A6.A6.A$36.3A5.A5.3A5.A5.3A5.A36.A$37.A5.3A5.A5.3A5.
A5.3A34.3A$37.A6.A6.A6.A6.A6.A36.A$15.A2.A2.A14.3A5.A5.3A5.A5.3A5.A
22.A$14.9A14.A5.3A5.A5.3A5.A5.3A20.3A8.A$15.A5.A15.A6.A6.A6.A6.A6.A6.
A15.A8.3A$15.A5.A5.A8.3A5.A5.3A5.A5.3A5.A5.3A14.A9.A$14.2A5.2A3.3A8.A
5.3A5.A5.3A5.A5.3A5.A14.3A$15.2A4.A5.A9.A6.A6.A6.A6.A6.A6.A15.A25.A$
16.2A3.A5.A8.3A5.A5.3A5.A5.3A5.A5.3A39.3A$17.6A3.3A8.A5.3A5.A5.3A5.A
5.3A5.A41.A$18.A2.A5.A16.A13.A13.A2$99.A$98.3A4.A10.A2.A$17.A3.A77.A
4.3A8.6A$16.7A82.A10.A2.A$17.2A.2A$19.A59.A29.A$18.3A57.3A8.A3.A14.3A
$19.A17.A41.A8.7A14.A$36.3A50.2A.2A21.A2.A$23.A13.A37.A15.A22.6A$22.
3A26.A22.3A13.3A22.A3.2A$23.A17.A8.3A22.A15.A23.A4.2A$40.3A8.A62.2A5.
2A$41.A45.A27.A5.A$86.3A26.A5.A$87.A10.A15.9A$97.3A15.A2.A2.A$98.A2$
73.A20.A$72.3A18.3A$23.A17.A14.A16.A8.A11.A$22.3A15.3A7.A4.3A23.3A$
23.A17.A7.3A4.A25.A$50.A5.A$19.A9.A7.A12.A4.3A$18.3A7.3A5.3A10.3A4.A
37.A$19.A9.A7.A12.A5.A31.A4.3A$50.A4.3A29.3A4.A$49.3A4.A31.A$50.A5.A$
50.A4.3A$49.3A4.A$50.A5.A$50.A4.3A$49.3A4.A$50.A$65.A2.A$64.6A$65.A2.
A$42.A11.A10.A2.A9.A2.A2.A$41.3A4.A4.3A8.6A7.9A$36.A5.A4.3A4.A10.A2.A
9.A5.A$35.3A10.A5.A10.A2.A$36.A11.A4.3A8.6A$47.3A4.A10.A2.A$32.A15.A
5.A10.A2.A$31.3A14.A4.3A8.6A$32.A14.3A4.A10.A2.A$48.A11$2.C124.C$71.A
2.A2.A$57.A12.9A$2.C53.3A12.A5.A49.C$57.A13.A5.A$57.A12.2A5.2A$56.3A
12.A4.2A$57.A5.A7.A3.2A$62.3A5.6A$63.A7.A2.A6$87.C2.C29.C2.C!''')(21,19)
    ram_unit1 = lt.pattern('''87.C2.C29.C2.C6$C126.C$13.A2.A15.A$12.6A13.3A$C12.A3.2A7.A5.A94.C$13.
A4.2A5.3A$12.2A5.2A5.A10.A13.A$13.A5.A6.A9.3A5.A5.3A5.A$13.A5.A5.3A9.
A5.3A5.A5.3A$12.9A5.A10.A6.A6.A6.A$13.A2.A2.A16.3A5.A5.3A5.A$37.A5.3A
5.A5.3A$37.A6.A6.A6.A6.A$36.3A5.A5.3A5.A5.3A5.A36.A$37.A5.3A5.A5.3A5.
A5.3A34.3A$37.A6.A6.A6.A6.A6.A36.A$15.A2.A2.A14.3A5.A5.3A5.A5.3A5.A
22.A$14.9A14.A5.3A5.A5.3A5.A5.3A20.3A8.A$15.A5.A15.A6.A6.A6.A6.A6.A6.
A15.A8.3A$15.A5.A5.A8.3A5.A5.3A5.A5.3A5.A5.3A14.A9.A$14.2A5.2A3.3A8.A
5.3A5.A5.3A5.A5.3A5.A14.3A$15.2A4.A5.A9.A6.A6.A6.A6.A6.A6.A15.A25.A$
16.2A3.A5.A8.3A5.A5.3A5.A5.3A5.A5.3A39.3A$17.6A3.3A8.A5.3A5.A5.3A5.A
5.3A5.A41.A$18.A2.A5.A16.A13.A13.A2$99.A$98.3A4.A10.A2.A$17.A3.A77.A
4.3A8.6A$16.7A82.A10.A2.A$17.2A.2A$19.A59.A29.A$18.3A57.3A8.A3.A14.3A
$19.A17.A41.A8.7A14.A$36.3A50.2A.2A21.A2.A$23.A13.A37.A15.A22.6A$22.
3A26.A22.3A13.3A22.A3.2A$23.A17.A8.3A22.A15.A23.A4.2A$40.3A8.A62.2A5.
2A$41.A45.A27.A5.A$86.3A26.A5.A$87.A10.A15.9A$97.3A15.A2.A2.A$98.A2$
94.A$93.3A$23.A17.A14.A25.A11.A$22.3A15.3A7.A4.3A23.3A$23.A17.A7.3A4.
A25.A$50.A5.A$19.A9.A7.A12.A4.3A$18.3A7.3A5.3A10.3A4.A37.A$19.A9.A7.A
12.A5.A31.A4.3A$50.A4.3A29.3A4.A$49.3A4.A31.A$50.A5.A$50.A4.3A$49.3A
4.A$50.A5.A$50.A4.3A$49.3A4.A$50.A$65.A2.A$64.6A$65.A2.A$42.A11.A10.A
2.A9.A2.A2.A$41.3A4.A4.3A8.6A7.9A$36.A5.A4.3A4.A10.A2.A9.A5.A$35.3A
10.A5.A10.A2.A$36.A11.A4.3A8.6A$47.3A4.A10.A2.A$32.A15.A5.A10.A2.A$
31.3A14.A4.3A8.6A$32.A14.3A4.A10.A2.A$48.A11$2.C124.C$71.A2.A2.A$57.A
12.9A$2.C53.3A12.A5.A49.C$57.A13.A5.A$57.A12.2A5.2A$56.3A12.A4.2A$57.
A5.A7.A3.2A$62.3A5.6A$63.A7.A2.A6$87.C2.C29.C2.C!''')(21,19)
    
    orgate = lt.pattern('''3.A3.A$2.7A$3.2A.2A$5.A$4.3A$5.A2$.A$3A$.A4$2.A$.3A$2.A!''')#|make_delay(55,10)('rot270')(2,20)
    ram_lngth = len(data)
    o = lt.pattern()
    for i in range(ram_lngth):
        databin = bin(data[i])[2:].zfill(lngth_dataword)
        for j in range(lngth_dataword):
            o |= (ram_unit1 if databin[j] == '1' else ram_unit0)(j*distbwparrwire,-i*distbwramunit)
        o |= star(16+lngth_dataword*distbwparrwire,25-i*distbwramunit)
        o |= orgate(107+lngth_dataword*distbwparrwire,112-i*distbwramunit)
        
    for j in range(lngth_dataword):
        o |= star(141+j*distbwparrwire,-ram_lngth*distbwramunit)
   
    #me in 2023: wtf... is commenting properly really that hard
    #why del??? its delay. is it tat hard to tyype 2 characters??
    MAGIC = 239#if this fn breaks, change this
    #11* and 14* part added by trial and error. is patchwork
    writestpdelay = (distbwparrwire+2*demux_distbwparrwire*(lngth_addr+1)) - lngth_dataword*distbwparrwire + MAGIC + 11*(8-lngth_dataword) + 14*(lngth_addr-8)

    if ((-writestpdelay)>distbwparrwire-10):
        write_demux = make_demux(lngth_addr,ram_lngth,distbwserwire,distbwser,demux_distbwparrwire,distbwramunit,delayoutps=-writestpdelay)
        write_stp = make_timed_serial_to_parallel(lngth_dataword,distbwparrwire,distbwser,distbwserwire,outpdelays=[i*(11+distbwparrwire) for i in range(lngth_dataword)],addtimesig=False,delayinps=0)('flip_y')
        extra_input_shift_in_write_adress = -distbwserwire+4
        extra_input_shift_in_write_data = -7
    else: 
        write_demux = make_demux(lngth_addr,ram_lngth,distbwserwire,distbwser,demux_distbwparrwire,distbwramunit,delayoutps=0)
        write_stp = make_timed_serial_to_parallel(lngth_dataword,distbwparrwire,distbwser,distbwserwire,outpdelays=[i*(11+distbwparrwire) for i in range(lngth_dataword)],addtimesig=False,delayinps=writestpdelay)('flip_y')
        extra_input_shift_in_write_adress = -12
        extra_input_shift_in_write_data = -distbwserwire+4



    write_demux = write_demux(-distbwparrwire-write_demux.bounding_box[2],-1)
    o |= write_demux

    write_stp = write_stp(140-distbwparrwire,distbwserwire+2*distbwramunit+distbwparrwire)
    

    
    read_demux = make_demux(lngth_addr,ram_lngth,distbwserwire,distbwser,demux_distbwparrwire,distbwramunit)
    read_demux = read_demux(-2*distbwparrwire-write_demux.bounding_box[2]-read_demux.bounding_box[2],84)
    o |= read_demux
    
    read_pts = make_parallel_to_serial(lngth_dataword,distbwparrwire,distbwser,distbwserwire,inpdelays=[i*(11+distbwparrwire) for i in range(lngth_dataword-1,-1,-1)],timerdelay=140-distbwparrwire,maxinpdelwidth=distbwparrwire-150)
    read_pts = read_pts(110,distbwserwire+distbwramunit+read_pts.bounding_box[3])
    o |= read_pts
    
    o |= write_stp(0,write_stp_make_lower_by)

    
    
    o |= make_turn('l',distbwserwire)(read_demux.bounding_box[0]+read_demux.bounding_box[2],read_demux.bounding_box[1]+read_demux.bounding_box[3]-12)
    o |= make_turn('l',distbwserwire)(write_demux.bounding_box[0]+write_demux.bounding_box[2],write_demux.bounding_box[1]+write_demux.bounding_box[3]+extra_input_shift_in_write_adress)
    #if write address/data ships crash into wrong place and explode/fizzle out, try changing stuff in previous&next line. i fear to make it proper a bigger refactor will be needed
    o |= make_turn('r',distbwserwire)(write_stp.bounding_box[0]-distbwserwire-9,write_stp.bounding_box[1]+write_stp.bounding_box[3]+extra_input_shift_in_write_data+write_stp_make_lower_by)
    
    return o

if len(sys.argv) == 3:

    with open(sys.argv[1], 'r') as code_file:
        ram = make_ram(assembler.assemble_code(code_file.read()),32,32,256,64,64,128,128,300)

        outppatt = lt.load('ramless-cpu.mc')|ram('flip_x',-245,0)

        outppatt.save(sys.argv[2])

else:
    print('To use this, pass the program file and output file as the only arguments.')