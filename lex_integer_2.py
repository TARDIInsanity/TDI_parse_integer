# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 18:11:05 2022

@author: github.com/TARDIInsanity
"""

__version__ = "2.3"

# all bases must begin with numeric sequences, and not begin with other base headers
BASES = {"0a":36, "0b":2, "0d":10, "0o":8, "0p":5, "0q":4, "0s":6, "0t":3, "0u":1, "0v":20, "0x":16}
ALNUM = "".join(chr(i+48) for i in range(10))+"".join(chr(i+97) for i in range(26))
ALDICTS = dict((base, dict((c, i) for i, c in enumerate(ALNUM[:base]))) for base in BASES.values())

def pull_ide(code:str, allow_underscore:bool=True) -> (bool, str, str):
    if not any(i.isalpha() or i == "_" for i in code[:1]):
        return (False, "", code)
    for index, char in enumerate(code):
        if not (char.isalnum() or (allow_underscore and char == "_")):
            break
    else:
        index += 1
    return (index > 0, code[:index], code[index:])

def get_int(code:str) -> int:
    if not code:
        return 0
    if (key := code[:2]) in BASES:
        base = BASES[key]
        code = code[2:]
    else:
        key = ""
        base = 10
    index = 0
    clen = len(code)
    if base == 1:
        if set(code) - {"1"}: # if the set of chars in the integer that aren't '1' is non-empty...
            raise SyntaxError("Unexpected chars when processing integer in base 1: "+key+code)
        return clen
    quick = ALDICTS[base]
    result = 0
    while index < clen:
        try:
            result = result*base + quick[code[index]]
            index += 1
        except KeyError:
            raise SyntaxError(f"Unexpected chars when processing integer in base {base}"+
                              (f" (valid portion: {key}{code[:index]})" if index else "")+
                              f": {code[index:]}")
    return int(code, base=base)

class IntPuller:
    def __init__(self,
                 single_seps:set=(), multi_seps:set=(),
                 single_sep_suffix:bool=False, multi_sep_suffix:bool=False):
        self.single_seps = set(single_seps)
        self.multi_seps = set(multi_seps)
        self.seps = self.single_seps.union(self.multi_seps)
        self.single_sep_suffix = single_sep_suffix
        self.multi_sep_suffix = multi_sep_suffix
    @staticmethod
    def singlet_error(char:str, segment:str) -> SyntaxError:
        return SyntaxError(f"multiple singlet separators {repr(char)} appeared "
            "in a row while parsing an int: {repr(segment)}")
    @staticmethod
    def suffix_error(char:str, segment:str, name:str) -> SyntaxError:
        return SyntaxError(f"{name} separator {repr(char)} appeared at the end "
            "while parsing an int: {repr(segment)}")
    def pull_int(self, code:str) -> (bool, object, str):
        if self.single_seps:
            if self.multi_seps:
                return self.sep_pull_int(code)
            return self.nomul_pull_int(code)
        if self.multi_seps:
            return self.nosing_pull_int(code)
        return self.nosep_pull_int(code)
    def nosep_pull_int(self, code:str) -> (bool, object, str):
        if not code[:1].isnumeric():
            return (False, None, code)
        for index, char in enumerate(code):
            if not char.isalnum():
                break
        try:
            result = get_int(code[:index])
            return (True, result, code[index:])
        except SyntaxError as e:
            return (False, e, code)
    def nomul_pull_int(self, code:str) -> (bool, object, str):
        if not code[:1].isnumeric():
            return (False, None, code)
        single = False
        for index, char in enumerate(code):
            if char in self.single_seps:
                if single:
                    return (False, self.singlet_error(char, code[:index]), code)
                single = True
            elif char.isalnum():
                single = False
            else:
                break
        else:
            index += 1
        attempt = code[:index]
        if single and not self.single_sep_suffix:
            return (False, self.suffix_error(char, attempt, "singlet"), code)
        try:
            result = get_int("".join(i for i in attempt if i not in self.seps))
            return (True, result, code[index:])
        except SyntaxError as e:
            return (False, e, code)
    def nosing_pull_int(self, code:str) -> (bool, object, str):
        if not code[:1].isnumeric():
            return (False, None, code)
        digit = False
        for index, char in enumerate(code):
            if char.isalnum():
                digit = True
            elif char in self.multi_seps:
                digit = False
            else:
                break
        else:
            index += 1
        attempt = code[:index]
        if not (digit or self.multi_sep_suffix):
            return (False, self.suffix_error(char, attempt, "multi"), code)
        try:
            result = get_int("".join(i for i in attempt if i not in self.seps))
            return (True, result, code[index:])
        except SyntaxError as e:
            return (False, e, code)
    def sep_pull_int(self, code:str) -> (bool, object, str):
        if not code[:1].isnumeric():
            return (False, None, code)
        single = False
        digit = False
        for index, char in enumerate(code):
            if char in self.single_seps:
                if single:
                    return (False, self.singlet_error(char, code[:index]), code)
                single = True
                digit = False
            elif char.isalnum():
                single = False
                digit = True
            elif char in self.multi_seps:
                single = False
                digit = False
            else:
                break
        else:
            index += 1
        attempt = code[:index]
        if single and not self.single_sep_suffix:
            return (False, self.suffix_error(char, attempt, "singlet"), code)
        if not (single or digit) and not self.multi_sep_suffix:
            return (False, self.suffix_error(char, attempt, "multi"), code)
        try:
            result = get_int("".join(i for i in attempt if i not in self.seps))
            return (True, result, code[index:])
        except SyntaxError as e:
            return (False, e, code)

def pull_string(code:str, opener:str, closer:str, escapes:(dict, sorted)) -> (bool, str, str):
    # expects (opener) to be the detected opening sequence
    # expects (closer) to be the appropriate closing sequence
    # expects (escapes) to be a dict of first_char:sorted_dict pairs
    # sorted_dicts should contain sequence:interpretation pairs
    old = code
    code = code[len(opener):]
    clen = len(code)
    result = []
    index = 0
    success = False
    while index < clen:
        char = code[index]
        if char in escapes:
            target = escapes[char]
            segment = code[index:index+target[None][0]]
            for length in target[None]:
                segment = segment[index:index+length]
                if segment in target[length]:
                    result.append(code[:index]+target[length][segment])
                    code = code[index+length:]
                    clen -= index+length
                    index = -1
                    break
        if closer.startswith(char) and code.count(closer, index, index+len(closer)):
            result.append(code[:index])
            code = code[index+len(closer):]
            success = True
            break
        index += 1
    else:
        return (False, "", old)
    if success:
        return (success, "".join(result), code)
    return (False, "", old)

#########################
# unrelated handy utils #
#########################

def sorted_set(vals:set) -> dict:
    '''assumes an iterable input.
    returns a dict of the form {None:[...], *(key:int, val:set)},
    where [...] is a reverse-sorted list of the integer keys.
    all items in the input are assumed to have a len() property.
    all items are slotted into exactly one set.'''
    result = {}
    for i in vals:
        li = len(i)
        if li not in result:
            result[li] = set()
        result[li].add(i)
    result[None] = sorted(result, reverse=True)
    return result

def sorted_dict(vals:dict) -> dict:
    '''assumes an iterable input that defines vals[x] for x in vals.
    returns a dict of the form {None:[...], *(key:int, val:dict)},
    where [...] is a reverse-sorted list of the integer keys.
    all keys in the input are assumed to have a len() property.
    all key:val pairs are slotted into exactly one dict.'''
    result = {}
    for i in vals:
        li = len(i)
        if li not in result:
            result[li] = {}
        result[li][i] = vals[i]
    result[None] = sorted(result, reverse=True)
    return result

pyth_openclose = {
    chr(39):chr(39),
    chr(34):chr(34),
    chr(39)*3:chr(39)*3,
    chr(34)*3:chr(34)*3,
    }
pyth_escape = {
    "\\":sorted_dict({"\\\'":"\'", "\\\\":"\\", "\\n":"\n",
                      "\\r":"\r", "\\t":"\t", "\\b":"\b",
                      "\\f":"\f", "\\\n":"",
                      })
    }

def gen_tab_tree_first_pass(code:str, feed:callable=None) -> "list[(str[str.isspace], str)]":
    '''splitting code by \n, turn "    ..." into ("    ", "...")
    feed can be substituted with any function that returns an
    iterable over the lines of the code.
    '''
    if feed is None:
        feed = lambda s: s.split("\n")
    temp = []
    for line in feed(code):
        index = 0
        llen = len(line)
        while index < llen and line[index].isspace():
            index += 1
        temp.append((line[:index], line[index:]))
    return temp
def gen_tab_tree_second_pass(code:"list[(str, str)]") -> "list[(int[abs], str)]":
    '''taking output from first_pass, convert the spaces into >=0 integer depth measures.
    ("   ", "a") -> (1, "a").
    does not error for any particular space string in the (space, str) input pairs.'''
    temp = code
    index = 0
    tlen = len(temp)-1
    buffer = [(0, temp[0][1])]
    while index < tlen:
        index += 1
        a, b = temp[index-1][0], temp[index][0]
        if b.startswith(a):
            depth = buffer[-1][0] + (b != a)
            buffer.append((depth, temp[index][1]))
            continue
        j = index-1
        while j >= 0:
            if temp[j][0] == b:
                depth = buffer[j][0]
                buffer.append((depth, temp[index][1]))
                break
            j -= 1
        else:
            raise IndentationError(f"line {index} in code sample ~ {temp[index]}")
    return buffer
def gen_tab_tree_third_pass(code:"list[(int[abs], str)]") -> dict:
    '''expecting (int>=0, str) pairs, nest items.'''
    buffer = code
    nest = [{"depth":-1, "name":None, "block":[]}]
    #nest = [{None:0}]
    def pop_level():
        siblings = nest.pop(-1)
        nest[-1]["block"].append(siblings)
        # nest[-1][nest[-1][True]] = siblings
    while buffer:
        depth, name = buffer.pop(0)
        if depth > nest[-1]["depth"]:
            nest.append({"depth":depth, "name":name, "block":[]})
        # if depth > nest[-1][None]:
        #     nest.append({None:depth, True:name, name:{}})
            continue
        while nest[-1]["depth"] > depth:
            pop_level()
        # while nest[-1][None] > depth:
        #     pop_level()
        if depth == nest[-1]["depth"]:
            pop_level()
            nest.append({"depth":depth, "name":name, "block":[]})
            continue
        # if depth == nest[-1][None]:
        #     nest[-1][True] = name
        #     nest[-1][name] = {}
        #     continue
        raise IndentationError("unindent does not match any outer indentation level")
    while len(nest) > 1:
        pop_level()
    return nest[0]
def generate_tab_tree(code:str, feed=None) -> dict:
    # generate a tree according to python's indentation rules
    temp = gen_tab_tree_first_pass(code, feed)
    buffer = gen_tab_tree_second_pass(temp)
    nesting = gen_tab_tree_third_pass(buffer)
    return nesting
def gen_exception_util(nesting:dict, parent:type=BaseException):
    classes = {}
    for tree in nesting["block"]:
        if not str.isidentifier(tree['name']):
            raise ValueError(("requires an identifier", tree['name']))
        exec("\n".join((
            f"class {tree['name']}(parent):",
            "    pass",
            f"classes[tree['name']] = {tree['name']}"
            )))
        classes.update(gen_exception_util(tree, classes[tree['name']]))
    return classes
def generate_classes(base_class:type, code:str, feed=None) -> dict:
    '''expects input of the following form:
    "\n".join((
    "BaseException",
    "    KeyboardInterrupt",
    "    Exception",
    "        ArithmeticError",
    "            ZeroDivisionError",
    "        AssertionError"))'''
    nesting = generate_tab_tree(code, feed)
    exceptions = gen_exception_util(nesting, base_class)
    return exceptions

def ignore_iterator(iterator:iter):
    try:
        while True:
            next(iterator)
    except StopIteration as e:
        return e.value
