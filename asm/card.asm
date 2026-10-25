; Chapter card (sequence 6, $82:B57E; docs/re/graphics.md §G4). The loader draws the whole dir-11 map with its
; tiles into BG3 tiles, map row r column c -> tile 16r+c+1. The original then wrote 3x4-tile cells for 第, the
; numeral, 章 and four title glyphs into the BG3 map ($7C00). tools/gfx_text.py draws "Chapter" into tiles
; $01-$08/$11-$18, the digits 1-6 into $21-$26/$31-$36 and chapter c's title (one or two lines) into the 4x15
; tiles from $41+64c, so this writes:
;   rows 15-16, columns 11-19: "Chapter" + the chapter's digit;  rows 22-25, columns 8-22: the title.
; Both are centred on x = 124, as the original text was.
pushpc
org $82B585        ; after PHK/PLB/REP #$20 in $82:B57E; was LDX #$7DCA ... (the cell writer $82:B5C4)
    jsl card_draw
    rts
pullpc

card_draw:
    rep #$30
    lda #$7C00+(15*32)+11   ; asar evaluates left to right: bracket every product
    ldx #$2001
    ldy #$2021
    jsr .header
    lda #$7C00+(16*32)+11
    ldx #$2011
    ldy #$2031
    jsr .header
    lda $00033B         ; chapter c: title tiles $41+64c..
    asl
    asl
    asl
    asl
    asl
    asl
    clc
    adc #$2041
    tax
    lda #$7C00+(22*32)+8
-   jsr .title          ; X ends on the next row's first tile
    clc
    adc.w #32           ; .w: asar sizes a small immediate as 8-bit
    cmp #$7C00+(26*32)+8
    bcc -
    rtl

.header:                ; A = map word address, X = first header tile, Y = tile of digit 1
    sta $002116
-   txa
    sta $002118
    inx
    txa
    and #$000F
    cmp #$0009
    bne -
    tya
    clc
    adc $00033B         ; chapter 0-5
    sta $002118
    rts

.title:                 ; A = map word address (kept), X = first tile of a 15-tile row
    sta $002116
    pha
-   txa
    sta $002118
    inx
    txa
    and #$000F
    bne -
    inx                 ; skip column 0 of the next tile row
    pla
    rts
