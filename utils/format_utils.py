
DEFAULT_LENGTH = 81

def print_title_boundary(title, char='*', length=DEFAULT_LENGTH):
    final_str = char * length
    if title:
        part_len = (length-len(title)-2)/2
        final_str = char * part_len + ' {} '.format(title) + char * part_len
    if len(final_str) < length:
        final_str = final_str + char
    print final_str

def print_boundary(char, length=DEFAULT_LENGTH):
    print_title_boundary(None, char=char, length=length)

