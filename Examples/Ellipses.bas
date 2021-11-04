#program ellipses
#autostart
  10 ; Ellipses - Copyright (c) 2020-2021 @kounch
  20 ; This program is free software, you can redistribute
  30 ; it and/or modify it under the terms of the
  40 ; GNU General Public License 
  50 RUN AT 3:CLS
  60 LET t=1422:LET x=-10:LET y=90
  70 LET x=x+10:LET y=y-10
  80 FOR n=0 TO PI*2 STEP .04:LET t=t-1:PRINT AT 0,0;t;"    "
  90 PLOT 128+x*SIN n,87+y*COS n
 100 NEXT n
 110 IF x=80 AND y=0 THEN PRINT AT 0,0;" ":PAUSE 0:STOP 
 120 GO TO 70
