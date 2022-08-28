# TDI_parse_integer
custom integer parsing and associated constants

Supports the following bases using a generalized "0x" format:  
- 0a : 36; alphanumeric: alphabetic characters represent 9 + their 1-indexed position in the alphabet (a=10, b=11... z=35)  
- 0b : 2; binary (01)  
- 0d : 10; decimal, but explicitly so (0123456789)  
- 0o : 8; octal (01234567)  
- 0p : 5; "penta", quinary (01234)  
- 0q : 4; quaternary (0123)  
- 0s : 6; seximal (012345)  
- 0t : 3; ternary (012)  
- 0u : 1; unary (the only digit is 1, the number of ones to follow 0u is the value, which can be as few as 0 ones)  
- 0v : 20; vagesimal (012...9 abc...j)  
- 0x : 16; hexadecimal (012...9 abcdef)  
  
In order to lex integers from strings, call .pull_int(code) from an instance of the class IntPuller(single_seps, multi_seps, single_sep_suffix, multi_sep_suffix). single_seps must be an iterable containing every separator which may appear either 0 and 1 times between each digit of the number. multi_seps must be an iterable containing every separator which may appear any number of times between digits. the two arguments ending in _suffix are booleans that specify whether these separators are allowed to be suffixes. If these suffixes are found at the end of the number, or if more than one separator or more than one copy of a separator from single_seps appears between digits, the lexing fails either softly (returning False, x, code) or by raising a SyntaxError.

Additional features provided:  
pull_string(code, opener, closer, escapes) -> (success:bool, result:str, remaining_code:str)  
> pull_string ASSUMES code.startswith(opener) and does not check whether this is true at all  
> closer : the substring which is required to close the string in your code, can be any non-empty string  
> escapes : the output of the utility function sorted_dict  
sorted_set(vals:set) -> dict  
> takes every value and inserts it into a set of values with the same len(), which is stored in the result under the appropriate integer denoting that charactaristic len().  
> then, under the key "None", a reverse-sorted list of the integer keys is inserted. When lexing tokens, it is best to begin searching for tokens starting from the longest ones and working down in length until all fail. This function is provided to assist in that process, since the key None is given a list of all other defined keys in order from greatest to least.  
sorted_dict(vals:dict) -> dict  
> just like sorted_set, except it remembers all key:val relationships while sorting the keys in the same way as sorted_set would.  
pyth_openclose  
> a constant dictionary of opener:closer pairs according to python's string opener & closer rules.  
pyth_escape  
> a constant dictionary of python's escape sequences, in string form, including the use of backslash at the end of a line to discard the newline.  
generate_classes  
> a helper function that takes a string of indented identifiers and quickly builds a class hierarchy for testing and debugging. !!! USES EXEC !!!. For security reasons, it is heavily advised that you remove (gen_exception_util) from the file before publishing any variation of this file.  
generate_tab_tree  
> a utility function used by (generate_classes) that converts a string of indented substrings into the correct tree of those same substrings. Feel free to use this function and its utilities (gen_tab_tree_first_pass, gen_tab_tree_second_pass, gen_tab_tree_third_pass) to prepare code that is meant to use pythonic indentation rules.  
