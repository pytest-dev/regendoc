

def dedent(line):
    stripped = line.lstrip(' ')
    return len(line) - len(stripped), stripped

def blocks(lines):
    result = []
    firstline = None
    last_indent = None
    items = []
    for lineno, line in enumerate(lines):

        indent, rest = dedent(line)

        if last_indent is None:
            print repr(last_indent), indent, repr(line)
            last_indent = indent

        if firstline is None:
            firstline = lineno

        if rest.isspace() or indent !=last_indent:
            if items:
                result.append((last_indent, firstline, items))
            if not rest.isspace():
                items = [rest]
                last_indent = indent
                firstline = lineno
            else:
                firstline = None
                last_indent = None
                items = []

        else:
            last_indent = indent
            items.append(rest)

    else:
        result.append((indent, firstline, items))


    return result
