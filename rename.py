import re
import os
import os.path as osp
import argparse
from copy import deepcopy
from pprint import pprint


def analyze_patterns(fd):
    """analyze all patterns (discard extension) of the given directory, and returns them (as string for re.compile -> number of matches)
    """
    fns = os.listdir(fd)  # list of original file names

    fns = [fn.rsplit('.', 1)[0] for fn in fns if '.' in fn]  # list of file names without extention
    fns = {idx: fn for idx, fn in enumerate(fns)}  # easy to delete

    ret_pats = {}
    while fns:  # while there is file name remaining
        # loop for one template
        _, fn_pat = fns.popitem()  # pop one fn
        fn_pat = split_fn_by_number(fn_pat)
        # discard invalid pat
        if len(fn_pat) == 1:  # all digits (already cleaned), all alphas (not video name)
            continue

        # preprocess other file names, split by number
        matched_fns = {key: split_fn_by_number(fn) for key, fn in fns.items()}
        # fn_key (key in fns) -> [diff1_idx, diff2_idx, ...] idx is the one in fn_pat
        fn_key2diffs = dict() 
        # filter the ones that not match in the number of parts
        matched_fns = {key: val for key, val in matched_fns.items() if len(val) == len(fn_pat)}
        # filter part by part
        for key, participant_fn in deepcopy(matched_fns).items():
            for part_idx, (pat_part, participant_part) in enumerate(zip(fn_pat, participant_fn)):  # match for each part

                def _fill_diff():  # fill the idx to fn_key2diffs
                    if key not in fn_key2diffs:
                        fn_key2diffs[key] = []
                    fn_key2diffs[key].append(part_idx)
                
                if pat_part.isdigit():  # number part, match any number
                    if not participant_part.isdigit():
                        del matched_fns[key]
                        break
                    else:  # both are digits, record the not match idx
                        if participant_part != pat_part:
                            _fill_diff()
                else:  # non-number part, match exactly
                    if participant_part != pat_part:
                        del matched_fns[key]
                        break
        
        # since we have filtered length one pats, all pats have digits, and keys in fn_key2diffs matches those in matched_fns
        fn_key2diffs = {key: val for key, val in fn_key2diffs.items() if len(val) == 1}  # remove matches that has more than one diff in digits
        diff_idxs = dict()  # idx in fn_pat -> number of matches
        for key, diff_idx in fn_key2diffs.items():
            del fns[key]  # remove matched file names
            diff_idxs[diff_idx[0]] = diff_idxs.get(diff_idx[0], 1) + 1  # count files, count the pat file in
        
        # create pat for each diff
        def _replace(pat, symbols):
            for symbol in symbols:
                pat = pat.replace(symbol, '\\' + symbol)
            return pat

        if fn_key2diffs:  # has other files matching the current file
            # in-place replace re template special chars from fn_pat
            for idx, part in enumerate(fn_pat):
                if not part.isdigit():  
                    part = _replace(part, ['(', ')', '{', '}', '[', ']', '.', '*', '^', '$', '&', '?'])
                    fn_pat[idx] = part
            for diff_idx, count in diff_idxs.items():
                target_pat = deepcopy(fn_pat)
                target_pat[diff_idx] = r'(\d+)'
                target_pat.append('$')  # to match all
                pat = ''.join(target_pat)
                ret_pats[pat] = count
    return ret_pats
                    

def split_fn_by_number(fn):
    """split file name by numbers

    '[KTXP][Vivy-Fluorite_Eye's_Song-][03][GB_CN][1080p][HEVC_opus]'
    ->
    [
        '[KTXP][Vivy-Fluorite_Eye's_Song-][',
        '03',
        '][GB_CN][',
        '1080',
        'p][HEVC_opus]'
    ]
    """
    builder = []  # temporate string builder
    ret = []  # hold the built strings

    def _build_string():  # build string from builder and fill into ret
        if builder:  # at the beginning, builder is empty, or at endding, may be empty
            ret.append(''.join(builder))
            builder.clear()

    reading_digit = False  # is last char a digit
    for char in fn:
        is_digit = char.isdigit()

        if is_digit != reading_digit:  # switch state, build string from builder
            _build_string()

        builder.append(char)

        reading_digit = is_digit
    
    _build_string()
    
    return ret


def rename(fd, template):
    for fn in os.listdir(fd):
        
        try:
            fn_content, fn_ext = fn.rsplit('.', 1)
        except ValueError as e:
            continue

        match = re.match(template, fn_content)

        if match:
            num = match.group(1)
            out_fn = f'{num}.{fn_ext}'
            out_fp = osp.join(fd, out_fn)
            in_fp = osp.join(fd, fn)
            os.rename(in_fp, out_fp)


if __name__ == '__main__':
    target_fd = '.'

    patterns = analyze_patterns(target_fd)
    print('analyze files, found the following patterns')
    for pattern, count in patterns.items():
        print(pattern)
        print('  count: {}'.format(count))
    
    num_files = len(os.listdir(target_fd))
    num_matches = sum(patterns.values())
    print('total number of files: {}, number of matches files: {}'.format(num_files, num_matches))

    print()
    response = input('type "yes" to continue: ')
    if response.lower() != 'yes':
        exit(1)
    
    for pattern in patterns:
        rename(target_fd, re.compile(pattern))
