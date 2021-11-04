#program nextsprite
#autostart
  10 ; NextSprite Demo - Copyright (c) 2020-2021 @kounch
  20 ; This program is free software, you can redistribute
  30 ; it and/or modify it under the terms of the
  40 ; GNU General Public License 
  50 RUN AT 2
  60 PAPER 0:BORDER 0:INK 7:CLS
  70 PRINT AT 6,8;"Next Sprite Demo"
  80 PRINT AT 10,10;"LOADING..."
  90 LAYER 2,0:.bmpload Stars.bmp:LAYER 2,1
 100 LOAD "Saucer.spr" BANK 12:SPRITE BANK 12:SPRITE BORDER 0:SPRITE PRINT 1
 110 FOR i=0 TO 14:LET x=(15*i):LET y=50+2*i:PROC Alien(x,y):NEXT i
 120 FOR i=14 TO 0 STEP -1:LET x=i*15:LET y=50+i*2:PROC Alien(x,y):NEXT i
 130 GO TO 110
 140 
 150 REM Procedures
 160 DEFPROC Alien(x,y)
 170 SPRITE 0,x+32,y,2,1
 180 SPRITE 1,x+48,y,3,1
 190 SPRITE 2,x+64,y,4,1
 200 FOR n=0 TO 6
 210 SPRITE n+3,x+n*16,y+16,n+7,1
 220 SPRITE n+10,x+n*16,y+32,n+14,1
 230 NEXT n
 240 ENDPROC
