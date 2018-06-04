import fuzzywuzzy.utils as utils
from fuzzywuzzy import fuzz
import re


def WRatio(s1, s2, force_ascii=True):
    """
    Return a measure of the sequences' similarity between 0 and 100, using different algorithms.

    **Steps in the order they occur**

    #. Run full_process from utils on both strings
    #. Short circuit if this makes either string empty
    #. Take the ratio of the two processed strings (fuzz.ratio)
    #. Run checks to compare the length of the strings
        * If one of the strings is more than 1.5 times as long as the other
          use partial_ratio comparisons - scale partial results by 0.9
          (this makes sure only full results can return 100)
        * If one of the strings is over 8 times as long as the other
          instead scale by 0.6

    #. Run the other ratio functions
        * if using partial ratio functions call partial_ratio,
          partial_token_sort_ratio and partial_token_set_ratio
          scale all of these by the ratio based on length
        * otherwise call token_sort_ratio and token_set_ratio
        * all token based comparisons are scaled by 0.95
          (on top of any partial scalars)

    #. Take the highest value from these results
       round it and return it as an integer.

    :param s1:
    :param s2:
    :param force_ascii: Allow only ascii characters
    :type force_ascii: bool
    :return:
    """

    p1 = utils.full_process(s1, force_ascii=force_ascii)
    p2 = utils.full_process(s2, force_ascii=force_ascii)

    if not utils.validate_string(p1):
        return 0
    if not utils.validate_string(p2):
        return 0

    # should we look at partials?
    try_partial = True

    unbase_scale = .60
    partial_scale = .90

    base = fuzz.ratio(p1, p2)
    len_ratio = float(max(len(p1), len(p2))) / min(len(p1), len(p2))

    # if strings are similar length, don't use partials
    if abs(len(p2) - len(p1)) <= 1:
        try_partial = True
        partial_scale = 0.95
        unbase_scale = 0.65

    if abs(len(p2) - len(p1)) <= 2 and max(len(p2), len(p1)) > 6:
        try_partial = False

    if abs(len(p2) - len(p1)) >=3 and max(len(p2),len(p1)) > 6 :
        try_partial = True
        partial_scale = 0.85

    if len_ratio > 2:
        try_partial = True
        partial_scale = 0.65

    # if one string is much much shorter than the other
    if len_ratio > 8:
        partial_scale = .60

    if try_partial:
        partial = fuzz.partial_ratio(p1, p2) * partial_scale
        ptsor = fuzz.partial_token_sort_ratio(p1, p2, full_process=False) \
            * unbase_scale * partial_scale
        ptser = fuzz.partial_token_set_ratio(p1, p2, full_process=False) \
            * unbase_scale * partial_scale

        return utils.intr(max(base, partial, ptsor, ptser))
    else:
        tsor = fuzz.token_sort_ratio(p1, p2, full_process=False) * unbase_scale
        tser = fuzz.token_set_ratio(p1, p2, full_process=False) * unbase_scale

        return utils.intr(max(base, tsor, tser))


def repeated_same(string):
    for i in range(ord('A'),ord('Z')+1):
        string1 = re.sub(chr(i)+chr(i)+chr(i)+'+', chr(i), string)

        return string1


def count_letters(word):
    non_count =[' ','-','0','1','2','3','4','5','6','7','8','9']
    return len([letter for letter in word if letter not in non_count])


def normalize_aditional_info(string):

    string_list = re.findall('\d+|\D+', string) #Separate numbers from letters
    string_list = [str(i).split() for i in string_list]
    string_list = sum(string_list, [])

    string_return = ''

    for i in string_list:
        string = i.upper()
        string = re.sub('[ºª]', '-', string)
        string = re.sub('[.,]','', string)
        string = string.replace(' ','')
        count = count_letters(string)
        if count >=2:
            string = ''

        string_return += string + '-'

    string_return = re.sub('-+', '-', string_return)

    length = len(string_return)

    string_return2 =''
    for i, char in enumerate(string_return):
        if i == 0 or i==length-1 and char =='-':
            char = char.replace('-','')

        string_return2 += char
    string_return = string_return2
    return string_return


def init_finish_bad_typo(string, bad_char='-'):

    length = len(string)
    string_return = ''

    for i, char in enumerate(string):
        if i == 0 or i ==length-1 and char == bad_char:
            char = char.replace(bad_char,'')

        string_return += char

    return string_return


