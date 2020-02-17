#program nextlayer2scroll
#autostart
  10 ; NextLayer2Scroll Demo - Copyright (c) 2020 @kounch
  20 ; This program is free software, you can redistribute
  30 ; it and/or modify it under the terms of the
  40 ; GNU General Public License 
  50 RUN AT 1
  60 BORDER 0:PAPER 0:INK 6:CLS
  70 PRINT AT 4,4;"Next Layer 2 Scroll Demo"
  80 PRINT AT 10,8;"NUMBER OF STEPS"
  90 INK 7:OPEN #5,"w>13,12,2,5"
 100 INPUT #5,n:CLOSE #5:INK 6
 110 CLS:PRINT AT 11,12;"LOADING..."
 120 LAYER 2,0:.bmpload saucer.bmp:LAYER AT 50,0:LAYER 2,1
 130 FOR i=n TO 1 STEP -1:LET Phi=PI/2*(4*i/n+1)
 140 LET x=50*(1+COS(Phi))
 150 LET y=30*(1-SIN(Phi))
 160 LAYER AT x,y
 170 NEXT i
 180 GO TO 130
