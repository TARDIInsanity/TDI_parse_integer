# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 18:11:05 2022

@author: github.com/TARDIInsanity
"""

__version__ = "2.0"

# all bases must begin with numeric sequences, and not begin with other base headers
BASES = {"0a":36, "0b":2, "0d":10, "0o":8, "0p":5, "0q":4, "0s":6, "0t":3, "0u":1, "0v":20, "0x":16}
ALNUM = "".join(chr(i+48) for i in range(10))+"".join(chr(i+97) for i in range(26))
ALDICTS = dict((base, dict((c, i) for i, c in enumerate(ALNUM[:base]))) for base in BASES.values())

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
        if self.seps:
            return self.sep_pull_int(code)
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

