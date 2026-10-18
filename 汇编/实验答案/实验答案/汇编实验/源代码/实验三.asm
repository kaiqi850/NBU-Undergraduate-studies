DATAS SEGMENT
    BUFFER1 DB 20
    	   DB 0
    	   DB 20 DUP(0)
    BUFFER2 DB 20
    	   DB 0
    	   DB 20 DUP(0)
    STR1 DB 'MATCH$'
DATAS ENDS

STACKS SEGMENT
    ;此处输入堆栈段代码
STACKS ENDS

CODES SEGMENT
    ASSUME CS:CODES,DS:DATAS,SS:STACKS
START:
    MOV AX,DATAS
    MOV DS,AX
    
    MOV AH,09H
    LEA DX,STR1
    INT 21H
    
    MOV AH,0AH
    LEA DX,BUFFER1
    INT 21H
	MOV SI DX
	
    MOV AH,09H
    LEA DX,STR1
    INT 21H

    MOV AH,0AH
    LEA DX,BUFFER1
    INT 21H
	MOV SI DX
    
    
    MOV AH,4CH
    INT 21H
    
CODES ENDS
    END START






