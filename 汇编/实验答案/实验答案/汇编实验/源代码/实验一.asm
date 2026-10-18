DATAS SEGMENT
    DATA1 DB 05H, 06H, 07H, 08H, 00H  ; 被加数（以ASCII码形式存储，低位在前）
    DATA2 DB 03H, 04H, 05H, 09H, 00H  ; 加数（以ASCII码形式存储，低位在前）
DATAS ENDS

STACKS SEGMENT
    ; 此处输入堆栈段代码
STACKS ENDS

CODES SEGMENT
    ASSUME CS:CODES, DS:DATAS, SS:STACKS

START:
    MOV AX, DATAS           ; 初始化数据段
    MOV DS, AX

    MOV SI, OFFSET DATA1    ; SI 指向 DATA1（被加数）
    MOV DI, OFFSET DATA2    ; DI 指向 DATA2（加数）
    XOR BX, BX              ; BX 用作进位，初始化为 0
    MOV CX, 4               ; 计算 4 位数

ADD_LOOP:
    ; 读取 DATA1 和 DATA2 中的当前数字字符（ASCII）
    MOV AL, [SI]            ; AL = DATA1 当前位
    MOV DL, [DI]            ; DL = DATA2 当前位

    ; 将字符转换为数字
    SUB AL, '0'             ; 将 AL 从 ASCII 转换为数字
    SUB DL, '0'             ; 将 DL 从 ASCII 转换为数字

    ; 执行加法操作并加上进位
    ADD AL, DL              ; AL = AL + DL (两个数字相加)
    ADD AL, BL              ; AL = AL + 进位

    ; 处理进位
    JC  CARRY_SET           ; 如果有进位，跳转到 CARRY_SET

    ; 没有进位，更新进位为 0
    MOV BL, 0               ; 清除进位

    ; 将结果保存回 DATA1
    ADD AL, '0'             ; 将数字转换回 ASCII
    MOV [SI], AL            ; 将结果存储回 DATA1

    ; 更新指针，处理下一位
    INC SI
    INC DI
    LOOP ADD_LOOP

CARRY_SET:
    MOV BL, 1               ; 设置进位为 1

    ; 处理进位
    ADD AL, '0'             ; 将数字转换回 ASCII
    MOV [SI], AL            ; 将结果存储回 DATA1

    INC SI
    INC DI
    LOOP ADD_LOOP

END_PROGRAM:
    MOV AH, 4Ch             ; 结束程序
    INT 21H

CODES ENDS
    END START

