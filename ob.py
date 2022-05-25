import io
import codecs
from PyPDF2.errors import PdfReadError
from PyPDF2.generic import *


def zRO(stream):

   return( readObject(stream, None) )
   
def zHFS(stream):

    HEXSTART = b"<"
    HEXEND = b">"
    EOF = b""

    tok = stream.read(1)
    assert tok == HEXSTART

    nibbles_start = stream.tell()
    tok = stream.read(1)
    while tok not in (HEXEND, EOF):
        if tok == "":
            break
        tok = stream.read(1)
    nibbles_end = stream.tell() - 1

    stream.seek(nibbles_start)
    tok = stream.read(nibbles_end - nibbles_start)
    return tok


def filter_string(s, remove):

    return re.sub("[0123456789abcdefABCDEF]+")


def RHFS(stream):

    import io
    import codecs

    HEX_CODEC = "HEX"
    HEXSTART = b"<"
    HEXEND = b">"
    HEXCHARS = b"0123456789ABCDEFabcdef"
    WHITESPACE = b" \00\t\n\r\f"
    EOF = b""

    tok = stream.read(1)
    assert tok == HEXSTART

    tok = stream.read(1)
    run = b""

    while tok not in (HEXEND, EOF):

        if tok in WHITESPACE:
            pass
        elif tok in HEXCHARS:
            run += tok
        else:
            raise PdfReadError("Bad character {} in hex stream".format(tok))

        tok = stream.read(1)

    if tok == EOF:  #
        raise PdfReadError("Stream has ended unexpectedly in hex string")
    if len(run) % 2 == 1:
        run += b"0"
    return ByteStringObject(codecs.decode(run, HEX_CODEC))


if __name__ == "__main__":

    t1 = b"<616263>    /abc"
    t2 = b"<61 62 63>  /embedded whitespage"
    t3 = b"<616263 >   /trailingblanks"
    t4 = t2.replace(b" ", b"\x00")  # nulls as whitespace
    t5 = b"<>  /zero-len-string"
    t6 = b"<61626> /odd length last char is 60 "
    t7 = b"<6162>\x00/null-separator-gave_error"
    t8 = b"<FFFE00610062>  /wrong bom "
    t9 = b"<FEFF00610062>  /bom "
    t10 = b"<a1A1>"
    e1 = b"<a1A1Z1a1>  /Non Hex char"
    e2 = b"<e2aaaaaaa0"  # non terminated
    e3 = b"<616263 %this is a comment \n 64 65>"
    t11 = b"<FEFFFEFF0061>  /bom bom a"
    t12 = b"<FEFFFEFFDCBF>  /bom + inval "
    all_hex_tests = (t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, e1, e2, e3, t11, t12)
    
    c1 = b'() /zero len '
    c2 = b'(abc)  /simple '
    c3 = b'(abc %this is a comment \r\n def )    /comments dont work in strings but LF for CF'
    c4 = b'(\\141\\142\\143\\377\\777abc\\400abc\0009) '
    c5 = b'(\\53a\\0530) \plus-a-plus-zero'
    c6 = b'(this is a single \\\nline) '
    c7 = b'(\\0053)   /plus3'
    c8 = b'(\\053)    /plus'
    c9 = b'(\\53)     /plus'
    c10 = b'(\\53a)   /plusa'    
    c11 = b'(())'
    c12 = b'(  \(:=   )  /smile' 
    all_string_tests = ( c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12 ) 
    
    r1 = b'[(s) (t) (u) ]'
    r2 = b'[/name\\%this is a comment \n   (some text) 123 124  true false null 10 0 R ]'
    r3 = b'[/name\\%this is a comment \n   (text(3)) 12.3 124  true false null 10 0 R ]'
    r4 = b'[/name\\ /name\x00(text) 12.3 124  true false null 10 0 R ]'
    r5 = b'[/loop [ /image1 /fred ]]'

    all_array_tests = (r1,r2,r3,r4,r5 )
    
    fctr = 0 
    
    for my_call in (zRO,):
      fctr += 1 
      with open ( f'tob{fctr}.t' , 'w' )  as o:
        
        
        print(my_call, file=o)

        for t in all_array_tests :
            stream = io.BytesIO(t)
            print("   ", t, file=o )
            try:
                result = my_call(stream)

            except Exception as e:
                print(e, file=o)
                result = "*** ERROR ***"
            print("==>", result, "<==", type(result) , file=o)
