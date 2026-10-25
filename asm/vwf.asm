; Dialogue VWF (phase 5). tools/build.py assembles this with asar onto the built ROM after packing the text.
; The game draws each glyph (16x11 1bpp, $84:808C + i*22) into a 2bpp tile buffer at $7F:10B8 that it DMAs to
; VRAM every frame: colour 3 for the glyph, colour 1 for a shadow 1 px right and 1 px down. The original puts
; glyphs in 12-px cells (column = low nibble of the cursor $7F:002C, wrapping after 14). This draws at a pixel pen
; instead and advances it by the glyph's width. docs/re/font.md has the buffer layout.
lorom

; scratch in bank $7F (DB = $7F inside vwf_draw); trap-tested unused (docs/re/rom.md)
!px = $FF00        ; pen x (pixels) on the current line
!adv = $FF02       ; advance of this glyph
!shift = $FF04     ; px & 7
!base = $FF06      ; buffer offset of the tile under the pen, top tile row of the text row
!stride = $FF08    ; bytes per tile row of the buffer
!prev = $FF0A      ; glyph row above, for the shadow
!hi = $FF0C        ; 32-bit shifter: hi word, lo word
!lo = $FF0E
!row = $FF10       ; glyph row 0-11 (11 = shadow only)
!tmp = $FF12
!clear = $7FFF14   ; nonzero: clear the 3 rows before the next glyph (the page wait is still running)

!buf = $10B8       ; text tile buffer $7F:10B8

org $839F01        ; glyph draw (JSR, A = glyph index 16-bit, X = text pointer); was the 12-px cell renderer
    jsl vwf_draw
    rts

; Paging. The original newline ($83:A561, code 0D) at row 3 only scrolls within 2 newlines after a {page}, else
; it waits and draws the next line over row 3; jp text never has more than 3 lines before a {page}. English
; lines are broken by the build, so: a newline past row 3 waits for a button and starts a fresh page, and {page}
; (code 01, was newline + wait + scroll counter $7F:002D) waits and starts a fresh page unless one just began.
org $83916E        ; dialogue VM ($83:9158, M = 8 bit): a glyph every 4 frames, was 8 (AND #$07); English pages
    and #$03            ; have ~3x the glyphs of the jp ones (phase 8: ~12 s a page at 8)

org $83A51A        ; {page} handler (jump table $83:A4F9)
    jmp vwf_page
vwf_scroll3:        ; JSL target for vwf_draw, in the old handler's dead bytes $83:A51D-$83:A527
    jsr $A3C9           ; scroll up one row, fill the bottom row with the box background (none for Totetsu)
    jsr $A3C9
    jsr $A3C9
    rtl
    assert pc() <= $83A528

org $83A561        ; newline handler, rewritten in place (77 bytes up to $83:A5AD)
vwf_newline:
    sep #$20
    lda $7F002C
    and #$0F
    beq .done           ; newline at column 0 does nothing (as before)
    lda $7F002C
    and #$30
    clc
    adc #$10
    sta $7F002C
    cmp #$30
    bne .done
    rep #$20
    jmp vwf_newpage
.done
    rep #$20
    rts

vwf_page:
    jsr $A561
    lda $7F002C
    and #$00FF
    beq +               ; the newline already began a page
    jmp vwf_newpage
+   rts

vwf_newpage:            ; wait for a button, cursor to the top left; vwf_draw clears the rows after the wait
    jsr $9DE7           ; starts the wait (arrow); the VM calls it every frame until a press ($7F:0028 = 0)
    sep #$20
    lda #$00
    sta $7F002C
    inc a
    sta !clear
    rep #$20
    rts
    assert pc() <= $83A5AE

org $84808C        ; font slots 0..n-1 (fonts/vwf.txt via tools/font.py)
    incbin "../build/vwf_font.bin"

org $80E580        ; free space $80:E57B-$80:FFBF (docs/re/rom.md)
vwf_draw:
    php
    phb
    rep #$30
    pha
    phx
    phy
    lda !clear          ; a new page began: clear the old one now that its wait is over (caller's DB)
    and #$00FF
    beq +
    lda #$0000
    sta !clear
    jsl vwf_scroll3     ; leaves the cursor on row 2
    sep #$20
    lda #$00
    sta $7F002C
    rep #$20
+   lda $05,s           ; the glyph index again
    pea $7F7F
    plb
    plb
    tax
    lda.l vwf_widths,x
    and #$00FF
    sta !adv
    txa                 ; X = $808C + 22 * glyph (bank $84)
    asl
    sta !tmp
    asl
    sta !row
    asl
    asl
    clc
    adc !tmp
    adc !row
    adc #$808C
    tax
    lda $002C           ; column 0 = start of a line: pen back to the left edge
    and #$000F
    bne +
    stz !px
+
    lda $003A           ; nonzero on the profile screens: 16-tile rows, up to 16 text rows
    bne .profile
    lda #$0170          ; dialogue box: 23-tile rows, text row = 2 tile rows (row * $2E0)
    sta !stride
    lda $002C
    and #$0030
    sta !tmp
    asl
    asl
    adc !tmp
    asl
    adc !tmp
    asl
    adc !tmp
    asl
    bra .rowbase
.profile
    lda #$0100
    sta !stride
    lda $002C
    and #$00F0
    asl
    asl
    asl
    asl
    asl
.rowbase
    sta !base
    lda !px
    and #$FFF8
    asl
    clc
    adc !base
    sta !base
    lda !px
    and #$0007
    sta !shift
    stz !prev
    stz !row
.loop
    lda #$0000
    ldy !row
    cpy #$000B
    bcs +
    lda.l $840000,x     ; row as stored: left byte first
    xba
    inx
    inx
+
    pha
    lda !prev
    lsr
    ora $01,s           ; plane 0: glyph | shadow
    ldy #$0000
    jsr vwf_emit
    pla
    sta !prev
    ldy #$0001          ; plane 1: glyph only
    jsr vwf_emit
    inc !row
    lda !row
    cmp #$000C
    bcc .loop
    lda !px
    clc
    adc !adv
    sta !px
    sep #$20            ; column stays 1: the game's newline still works, its 14-cell wrap never fires
    lda $002C
    and #$F0
    ora #$01
    sta $002C
    rep #$30
    ply
    plx
    pla
    plb
    plp
    rtl

; A = 16-bit row pattern (MSB = left pixel), Y = plane (0/1). ORs it, shifted right by !shift, into the three
; tiles under the pen at glyph row !row.
vwf_emit:
    sta !hi
    stz !lo
    phy
    ldy !shift
    beq +
-   lsr !hi
    ror !lo
    dey
    bne -
+
    lda !row
    asl
    cmp #$0010
    bcc +
    clc                 ; rows 8-11 are in the next tile row: + stride - 16
    adc !stride
    sec
    sbc #$0010
+
    clc
    adc !base
    adc $01,s
    tay
    pla
    sep #$20
    lda !hi+1
    ora !buf,y
    sta !buf,y
    lda !hi
    ora !buf+16,y
    sta !buf+16,y
    lda !lo+1
    ora !buf+32,y
    sta !buf+32,y
    rep #$20
    rts

vwf_widths:
    incbin "../build/vwf_widths.bin"
vwf_end:
    assert pc() <= $80FFC0
