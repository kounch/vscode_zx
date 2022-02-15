#program nextlayer2scroll
#autostart
  10 ; NextLayer2Scroll v2 Demo - Copyright (c) 2020-2022 @kounch
  20 ; This program is free software, you can redistribute
  30 ; it and/or modify it under the terms of the
  40 ; GNU General Public License 
  50 RUN AT 1
  60 BORDER 0:PAPER 0:INK 6:CLS
  70 PRINT AT 4,2;"Next Layer 2 Scroll Demo (v2)"
  80 PRINT AT 10,5;"Enter number of steps:"
  90 INK 7:OPEN #5,"w>12,10,2,8"
 100 INPUT #5,n:CLOSE #5:INK 6
 110 CLS:PRINT AT 11,10;"PREPARING..."
 120 RUN AT 3:DIM c(2,n)
 130 FOR i=n TO 1 STEP -1:LET Phi=PI/2*(4*i/n+1)
 140 LET c(1,n+1-i)=50*(1+COS(Phi))
 150 LET c(2,n+1-i)=30*(1-SIN(Phi))
 160 NEXT i:RUN AT 1
 170 CLS:PRINT AT 11,12;"LOADING..."
 180 LAYER 2,0:.bmpload saucer.bmp:LAYER AT 50,0:LAYER 2,1
 190 FOR i=1 TO n
 200 LAYER AT c(1,i),c(2,i)
 210 NEXT i
 220 GO TO 190
