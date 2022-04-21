
DEFAULT_LENGTH = 100

def print_title_boundary(title, char='*', length=DEFAULT_LENGTH):
    if not title:
        print char * length
        return
    part_len = (length-len(title)-2)/2
    final_str = char * part_len + ' {} '.format(title) + char * part_len
    if len(final_str)%2 == 1:
        final_str = final_str + char
    print final_str

def print_boundary(char, length=DEFAULT_LENGTH):
    print_title_boundary(None, char=char, length=length)

