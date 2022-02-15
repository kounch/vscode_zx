#program nextsprite
#autostart
  10 ; NextSprite Demo V2 - Copyright (c) 2020-2022 @kounch
  20 ; This program is free software, you can redistribute
  30 ; it and/or modify it under the terms of the
  40 ; GNU General Public License 
  50 RUN AT 2
  60 PAPER 0:BORDER 0:INK 7:CLS
  70 PRINT AT 6,8;"Next Sprite Demo"
  80 PRINT AT 10,10;"LOADING..."
  90 LAYER 2,0:.bmpload Stars.bmp:REM Background image
 100 SPRITE CLEAR:LOAD"Saucer.spr" BANK 12:SPRITE BANK 12:SPRITE BORDER 0:SPRITE PRINT 0
 110 RESTORE 500:READ s:REM Read Pattern
 120 SPRITE 0,0,0,s,0:PROC CreateRelSprites(1)
 130 SPRITE BORDER 0:SPRITE PRINT 1:LAYER 2,1
 135 REM FOR i=0 TO 28:LET x=7*i:LET y=50+i:SPRITE 0,x,y,s,1:NEXT i
 140 REM FOR i=28 TO 0 STEP -1:LET x=i*7:LET y=50+i:SPRITE 0,x,y,s,1:NEXT i
 145 LET n=40:FOR %i=1 TO n:LET j=%i:LET Phi=PI/2*(4*(n-j)/n+1)
 150 LET x=100+50*(1+COS(Phi)):LET y=60+30*(1-SIN(Phi)):SPRITE 0,x,y,s,1:NEXT %i
 160 GO TO 135
 199
 300 DEFPROC CreateRelSprites(i)
 310 FOR %j=i TO i+19
 320 READ p:REM Read Pattern
 330 LET k=%j:LET m=%j MOD 7:PROC RelSprite(k,m*16,INT(k/7)*16,p)
 340 NEXT %j
 350 ENDPROC
 399 
 400 DEFPROC RelSprite(i,x,y,p)
 410 REG 52,i:REM Relative Sprite number
 420 REG 53,x:REM x relative coord
 430 REG 54,y:REM y relative coord
 440 REG 55,0:REM No rotations...
 450 REG 56,p+64+128:REM Pattern, Visible, Extra attr
 460 REG 57,64:REM Relative sprite, pattern<64
 470 ENDPROC
 499 
 500 DATA 0,0,2,3,4,0,0
 510 DATA 7,8,9,10,11,12,13
 520 DATA 14,15,16,17,18,19,20
