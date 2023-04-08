import os
import re
import Preprocessing


# ================================================ Get Begin/End Block =================================================
def get_begin_end_blck(lines: list[str], index: int = 0):
    shrt_lst: list[str] = lines[index:]
    blck_cnt: int = 0
    blck_end: int = 0
    blck_entry: bool = False
    for iter_val, iter_line in enumerate(shrt_lst):
        iter_line = re.sub(r'[\t\n\r]', '', iter_line)
        iter_line_lst = re.split(r'[() ]', iter_line)
        if 'begin' in iter_line_lst and 'end' not in iter_line_lst:
            blck_cnt += 1
            blck_entry = True
        elif 'end' in iter_line_lst and 'begin' not in iter_line_lst:
            blck_cnt -= 1
        if blck_cnt == 0 and blck_entry is True:
            blck_end = iter_val
            break
    blck_end += index + 1
    out_lst = [x.replace('\n', '') for x in lines[index:blck_end] if x != '']
    return out_lst, blck_end


# ================================================ Get Begin/End Block =================================================

# ================================================== Get Always Block ==================================================

def get_always_blck(lines: list[str], index: int = 0) -> list[str]:
    line = lines[index]
    line1 = re.sub(r'[\t\n\r]', '', line)
    line_lst = re.split(r'[() ]', line1)
    accptd_terms = ['always', 'always_ff', 'always_comb']
    out_lst = []
    if len([x for x in line_lst if x in accptd_terms]) > 0:
        if line1.rstrip()[-1] != ';':
            out_lst, out_index = get_begin_end_blck(lines, index)
        else:
            out_lst = [line]
    return out_lst


def get_always_sens(lines: list[str], index: int = 0) -> list[str]:
    line: str = lines[index]
    line1: str = re.sub(r'[\t\n\r]', '', line)
    line_lst: list[str] = re.split(r'[() ]', line1)

    rmv_terms_always: list[str] = ['always', 'always_ff', 'always_comb']
    rmv_terms_cmn: list[str] = ['begin', 'end', '@', '']
    out_lst: list[str] = [x for x in line_lst if x not in rmv_terms_always]
    out_lst = [x for x in out_lst if x not in rmv_terms_cmn]
    out_str = ' '.join(out_lst)
    out_lst = [x.strip() for x in out_str.split(',')]
    x_out = ''
    if rmv_terms_always[2] not in line_lst:
        for i, x in enumerate(out_lst):
            if x.split()[0] == 'posedge':
                x_out = x.split()[1] + ' == 1'
            elif x.split()[0] == 'negedge':
                x_out = x.split()[1] + ' == 0'
            out_lst[i] = x_out
    else:
        out_lst = []
    return out_lst


# ================================================== Get Always Block ==================================================


# ================================================ Get Always-Block CFG ================================================
def always_blck_CFG(lines: list[str], index, node: str, Nodeinfo: list[str]):
    case_keywrd: list[str] = ['case', 'casex', 'casez']
    ifelse_keywrd: list[str] = ['if']
    # assign_keywrd: list[str] = ['assign']
    node_root = node

    always_blck: list[str] = get_always_blck(lines, index)
    sens_lst = get_always_sens(always_blck)
    sens_cond = ', '.join(sens_lst)

    Nodeinfo_appnd = node + ' :: ' + sens_cond + ' :: Alws;' if len(sens_cond) > 0 else node + ' :: ' + 'Comb/*' + ' :: Alws;'
    Nodeinfo.append(Nodeinfo_appnd)

    skiplines = len(always_blck) - 1
    inline_cond_pattern = re.compile(
        r"([a-zA-Z0-9'{},._]+)\s?(\[[a-zA-Z0-9'{},._]+:[a-zA-Z0-9'{},._]+])?\s?(<?=)\s?((\([a-zA-Z0-9'{},._]+)\s?(\[[a-zA-Z0-9'{},._]+:[a-zA-Z0-9'{},._]+])?\s?(!=|==|>|>=|<|<=)\s?([a-zA-Z0-9'{},._]+\))|(\(?!?\s?([a-zA-Z0-9'{},._]+)([a-zA-Z0-9'{},._]+:[a-zA-Z0-9'{},._]+])?)\)?)\s?(\?)\s?([a-zA-Z0-9'{},._]+)\s?(:)\s?([a-zA-Z0-9'{},._ ]+);")
    assgnmnt_pattern = re.compile(r"([\w.\[\]: ]+)\s*(<?=)\s*([\w.\[\]: ]+)\s*;")

    iter_no: int = 0
    skiplines_1: int = 0
    while iter_no < len(always_blck):
        iter_line = always_blck[iter_no]
        iter_line = re.sub(r'[\t\n]', '', iter_line)
        iter_line_lst = re.split(r"[() ]", iter_line)

        if any(x in iter_line_lst for x in case_keywrd):
            node, Nodeinfo, skiplines_1 = nestedcasestatement(always_blck, iter_no, node_root, Nodeinfo)
        elif any(x in iter_line_lst for x in ifelse_keywrd):
            node, Nodeinfo, skiplines_1 = ifelse_CFG(always_blck, iter_no, node_root, Nodeinfo)
        elif re.search(inline_cond_pattern, iter_line) is not None:
            node, Nodeinfo = inline_cond_assgnmnt(iter_line, node_root, Nodeinfo)
        elif re.search(assgnmnt_pattern, iter_line):
            node, Nodeinfo = get_assgnment(iter_line, node_root, Nodeinfo)

        iter_no += skiplines_1 + 1
        skiplines_1 = 0

    return node, Nodeinfo, skiplines


# ================================================ Get Always-Block CFG ================================================

# =============================================== Get If/Else Condition ================================================
def and_or_frmtng(cond2frmt: str) -> list[str]:
    """
    Converts '||' and '&&' to 'or' 'and' respectively
    :param cond2frmt: Takes the Condition to format
    :return: returns CFG formatted Condition line
    """
    flatten_list = lambda irregular_list: [element for item in irregular_list for element in
                                           flatten_list(item)] if type(irregular_list) is list else [irregular_list]
    in_cond_lst_raw = [x.strip() for x in re.split(r'\|\|', cond2frmt)]
    in_cond_lst_or = []
    for iter_num, iter_val in enumerate(in_cond_lst_raw):
        if iter_num < len(in_cond_lst_raw) - 1:
            in_cond_lst_or.append(iter_val)
            in_cond_lst_or.append(' or ')
        else:
            in_cond_lst_or.append(iter_val)
    for iter_num, iter_val in enumerate(in_cond_lst_or[:]):
        if '&&' in iter_val:
            and_sep = re.split(r'&&', iter_val)
            in_cond_lst_and = []
            for iter_num1, iter_val1 in enumerate(and_sep):
                if iter_num1 < len(and_sep) - 1:
                    in_cond_lst_and.append(iter_val1)
                    in_cond_lst_and.append(' and ')
                else:
                    in_cond_lst_and.append(iter_val1)
            in_cond_lst_or[iter_num] = in_cond_lst_and
    in_cond_lst = flatten_list(in_cond_lst_or)
    return in_cond_lst


def bracket_brkdwn(bracketed_cond: str, cond: str) -> str:
    """
    This will break down a bracketed condition into CFG format
    :param bracketed_cond: the bracketed condition that is to be broken down
    :param cond: Whole condition
    :return: CFG format condition
    """
    comparison_symb_lst = ['>=', '<=', '==', '!=', '>', '<', ' or ', ' and ']

    in_cond_lst = and_or_frmtng(bracketed_cond)

    skip_lst = [' or ', ' and ']
    for iter_num, in_cond_lst_item in enumerate(in_cond_lst):
        tst_s = re.sub(r'[\s(]', '', cond)
        if tst_s[tst_s.index(re.sub(r'[\s(]', '', bracketed_cond)) - 1] != '!':
            if any(substrng in in_cond_lst_item for substrng in comparison_symb_lst):
                # if any(substrng in in_cond_lst_item for substrng in comparison_symb_lst):
                if '==' in in_cond_lst_item:
                    in_cond_lst[iter_num] = ' == '.join([x.strip() for x in in_cond_lst_item.split('==')])
                elif '!=' in in_cond_lst_item and len(re.findall(r'!=\s*[1|0]', in_cond_lst_item)) > 0:
                    # print(in_cond_lst_item)
                    if re.search(r'!=\s*1', in_cond_lst_item) != None:
                        in_cond_lst_item = re.sub(r'!=\s*1', '==_0', in_cond_lst_item)
                    elif re.search(r'!=\s*0', in_cond_lst_item) != None:
                        # print(in_cond_lst_item)
                        in_cond_lst_item = re.sub(r'!=\s*0', '==_1', in_cond_lst_item)
                    in_cond_lst_item = re.sub(r'==_0', '== 0', in_cond_lst_item)
                    in_cond_lst_item = re.sub(r'==_1', '== 1', in_cond_lst_item)
                    in_cond_lst[iter_num] = in_cond_lst_item
                elif '!=' in in_cond_lst_item and len(re.findall(r'!=\s*[1|0]', in_cond_lst_item)) == 0:
                    in_cond_lst[iter_num] = ' != '.join([x.strip() for x in in_cond_lst_item.split('!=')])
                elif '>=' in in_cond_lst_item:
                    in_cond_lst[iter_num] = ' >= '.join([x.strip() for x in in_cond_lst_item.split('>=')])
                elif '<=' in in_cond_lst_item:
                    in_cond_lst[iter_num] = ' <= '.join([x.strip() for x in in_cond_lst_item.split('<=')])
                elif '>' in in_cond_lst_item:
                    in_cond_lst[iter_num] = ' > '.join([x.strip() for x in in_cond_lst_item.split('>')])
                elif '<' in in_cond_lst_item:
                    in_cond_lst[iter_num] = ' < '.join([x.strip() for x in in_cond_lst_item.split('<')])
            else:
                in_cond_lst[iter_num] = in_cond_lst_item.replace('!', '').strip() + ' == 0' if \
                    in_cond_lst_item.strip()[0] == '!' else in_cond_lst_item.strip() + ' == 1'
        else:

            if any(substrng in in_cond_lst_item for substrng in comparison_symb_lst):
                if '==' in in_cond_lst_item and len(re.findall(r'==\s*[1|0]', in_cond_lst_item)) > 0:
                    # if len(re.findall(r'==\s?[1|0]', in_cond_lst_item)) > 0:
                    if re.search(r'==\s?1', in_cond_lst_item) != None:
                        in_cond_lst_item = re.sub(r'==\s*1', '==_0', in_cond_lst_item)
                    elif re.search(r'==\s?0', in_cond_lst_item) != None:
                        in_cond_lst_item = re.sub(r'==\s*0', '==_1', in_cond_lst_item)
                    in_cond_lst_item = re.sub(r'==_0', '== 0', in_cond_lst_item)
                    in_cond_lst_item = re.sub(r'==_1', '== 1', in_cond_lst_item)
                    in_cond_lst_item = re.sub(r'or', 'AND', in_cond_lst_item)
                    in_cond_lst_item = re.sub(r'and', 'OR', in_cond_lst_item)
                    in_cond_lst_item = re.sub(r'AND', 'and', in_cond_lst_item)
                    in_cond_lst_item = re.sub(r'OR', 'or', in_cond_lst_item)
                    in_cond_lst[iter_num] = ' == '.join([x.strip() for x in in_cond_lst_item.split('==')])
                elif '==' in in_cond_lst_item and len(re.findall(r'==\s*[1|0]', in_cond_lst_item)) == 0:
                    in_cond_lst[iter_num] = ' != '.join([x.strip() for x in in_cond_lst_item.split('==')])
                elif '!=' in in_cond_lst_item and len(re.findall(r'!=\s*[1|0]', in_cond_lst_item)) > 0:
                    # if len(re.findall(r'!=\s?[1|0]', in_cond_lst_item)) > 0:
                    if re.search(r'!=\s*1', in_cond_lst_item) != None:
                        in_cond_lst_item = re.sub(r'!=\s*1', '==_1', in_cond_lst_item)
                    elif re.search(r'!=\s*0', in_cond_lst_item) != None:
                        in_cond_lst_item = re.sub(r'!=\s?0', '==_0', in_cond_lst_item)
                    in_cond_lst_item = re.sub(r'==_0', '== 0', in_cond_lst_item)
                    in_cond_lst_item = re.sub(r'==_1', '== 1', in_cond_lst_item)
                    in_cond_lst_item = re.sub(r'or', 'AND', in_cond_lst_item)
                    in_cond_lst_item = re.sub(r'and', 'OR', in_cond_lst_item)
                    in_cond_lst_item = re.sub(r'AND', 'and', in_cond_lst_item)
                    in_cond_lst_item = re.sub(r'OR', 'or', in_cond_lst_item)
                    in_cond_lst[iter_num] = ' == '.join([x.strip() for x in in_cond_lst_item.split('==')])
                elif '!=' in in_cond_lst_item and len(re.findall(r'!=\s?[1|0]', in_cond_lst_item)) == 0:
                    in_cond_lst[iter_num] = ' == '.join([x.strip() for x in in_cond_lst_item.split('!=')])
                elif '>=' in in_cond_lst_item:
                    in_cond_lst[iter_num] = ' < '.join([x.strip() for x in in_cond_lst_item.split('>=')])
                elif '<=' in in_cond_lst_item:
                    in_cond_lst[iter_num] = ' > '.join([x.strip() for x in in_cond_lst_item.split('<=')])
                elif '>' in in_cond_lst_item:
                    in_cond_lst[iter_num] = ' <= '.join([x.strip() for x in in_cond_lst_item.split('>')])
                elif '<' in in_cond_lst_item:
                    in_cond_lst[iter_num] = ' >= '.join([x.strip() for x in in_cond_lst_item.split('<')])
                elif ' or ' in in_cond_lst_item:
                    in_cond_lst[iter_num] = ' and '
                elif ' and ' in in_cond_lst_item:
                    in_cond_lst[iter_num] = ' or '
            else:
                in_cond_lst[iter_num] = in_cond_lst_item.replace('!', '').strip() + ' == 1' if \
                    in_cond_lst_item.strip()[0] == '!' else in_cond_lst_item.strip() + ' == 0'
    in_cond_statemnt = ''.join(in_cond_lst)
    return in_cond_statemnt


def cond_breakdown(cond: list[str]) -> str:
    '''
    from the condition in if Cond bracket returns the condition in CFG format
    :param cond: everything within the bracket if_condition
    :return: cond in CFG format
    '''
    cond = ''.join(cond)
    pattern2 = re.compile(r"\(([^()]+)\)")
    comparison_lst = ['>=', '<=', '==', '!=', '>', '<']
    and_or_lst = ['or', 'and']
    innermost_bracket_lst = re.findall(pattern2, cond)
    broken_dwn_cond_lst = []
    while len(innermost_bracket_lst) > 0:
        for each_in_cond in innermost_bracket_lst:
            in_cond_statemnt = bracket_brkdwn(each_in_cond, cond)
            cond = cond.replace(each_in_cond, '')
            cond = re.sub(r'!?\(\)', in_cond_statemnt, cond)
        innermost_bracket_lst = re.findall(pattern2, cond)


    # Format the condition out of any nested brackets
    broken_dwn_cond_lst = and_or_frmtng(cond)
    for iter_num, iter_val in enumerate(broken_dwn_cond_lst):
        if not any(substring in iter_val for substring in comparison_lst) and not any(
                substring in iter_val for substring in and_or_lst):
            iter_val = iter_val.strip()
            iter_val = iter_val.replace('!', '') + ' == 0' if iter_val[
                                                                  0] == '!' else iter_val + ' == 1'  # Single word condition to CFG formatted condition
            broken_dwn_cond_lst[iter_num] = iter_val
    cond = ''.join(broken_dwn_cond_lst)

    return cond


def get_ifelse_cond(if_line: str):
    '''
    if_else condition from if line
    :param if_line: the line where "if" is mentioned
    :return:
    '''
    pattern1 = re.compile(r'\((.+)\)')  # pattern that marks everythin within a bracket
    if 'if' in re.split(r'[() ]', if_line):

        cond: list[str] = re.findall(pattern1, if_line)         # get the whole condition in if line
        cond[0] = "(" + cond[0] + ")"
        cond_CFG_format: str = cond_breakdown(cond)             # get condition in CFG Format
        return cond_CFG_format


# =============================================== Get If/Else Condition ================================================

# ================================================= Get If-Else Block ==================================================

def get_ifelse_blck(lines: list[str], index: int = 0) -> list[str]:
    line = lines[index]
    shrt_lst = lines[index:]
    line1 = re.sub(r'[\t\n\r]', '', line)
    line_lst = re.split(r'[() ]', line1)
    if 'if' in line_lst:
        if line1.rstrip()[-1] != ';':
            if_blck, if_blck_end = get_begin_end_blck(shrt_lst)
            if_else_end_flag: bool = False
            else_blck_end = if_blck_end
        else:
            if_blck = [line1]
            if_blck_end = 0
            if_else_end_flag = False
            else_blck_end = if_blck_end
        # print('Next Line:\t', shrt_lst[if_blck_end])
        while if_else_end_flag is False:
            nextline = shrt_lst[else_blck_end]
            if 'else' in re.split(r'[() ]', re.sub(r'[\t\n\r]', '', nextline)):
                shrt_lst = shrt_lst[else_blck_end:]
                if nextline.rstrip()[-1] != ';':
                    else_blck, else_blck_end = get_begin_end_blck(shrt_lst)
                else:
                    else_blck, else_blck_end = (shrt_lst[else_blck_end], else_blck_end + 1)
                # print('else Block:\t', else_blck)
            else:
                else_blck = []
                if_else_end_flag = True
            for x in else_blck:
                if_blck.append(x)
        return if_blck
    else:
        print('No If Condition Found')


def ifelse_CFG(lines: list[str], index: int, node: str, Nodeinfo: list[str]):
    '''
    Get the CFG from a If-Else Block
    :param lines: list of line from which the block is to be extracted
    :param index: index of the value where the if statement is found
    :param node: Node value before the Function is run
    :param Nodeinfo: CFG before the Function is run
    :return: Node, CFG after the Function is run (return tyoe Tuple)
    '''
    case_trig: list[str] = ['case', 'casex', 'casez']
    ifelse_trig: list[str] = ['if']
    ifelse_trig_act: list[str] = [x for x in ifelse_trig if x in re.split(r'[() ]', lines[index])]
    line = re.sub(r'[\t\n]', '', lines[index])
    line_lst: list[str] = re.split(r'[() ]', line)
    skip_lines: int = 0
    if any(x in ifelse_trig for x in line_lst):
        ifelse_blck = get_ifelse_blck(lines, index)
        skip_lines = len(ifelse_blck) - 1
        curr_node: int = 0
        node1 = node
        node_discard = ""           # To keep the discarded nodes in Nested Block
        iter_no = 0
        skip_lines_1 = 0
        iter_line = ifelse_blck[iter_no]
        iter_line = re.sub(r'[\t\n]', '', iter_line)
        iter_line_lst = re.split(r'[() ]', iter_line)

        assgmnt_pttrn = re.compile(r"\s*(assign)?\s*(.+)\s*(<?=)\s*(.+)\s*;")
        inline_cond_pattern = re.compile(r"\s*(assign)?\s*(.+)\s*(<?=)\s*\(?(.+)\)?\s*(\?)\s*(.+)\s*(:)\s*(.+)\s*;\s*")

        if any(x in ifelse_trig for x in iter_line_lst):
            if_else_cond = get_ifelse_cond(iter_line)
            node = node1 + ', ' + str(curr_node)
            curr_node += 1
            Nodeinfo_appnd = node + ' :: ' + if_else_cond + ' :: C;'
            Nodeinfo.append(Nodeinfo_appnd)
            iter_no += 1

        while iter_no < len(ifelse_blck):
            iter_line = ifelse_blck[iter_no]
            iter_line = re.sub(r'[\t\n]', '', iter_line)
            iter_line_lst = re.split(r'[() ]', iter_line)

            if 'else' in iter_line_lst and 'if' in iter_line_lst:
                if_else_cond = get_ifelse_cond(iter_line)
                node = node1 + ', ' + str(curr_node)
                curr_node += 1
                Nodeinfo_appnd = node + ' :: ' + if_else_cond + ' :: C;'
                Nodeinfo.append(Nodeinfo_appnd)

            elif 'else' in iter_line_lst and 'if' not in iter_line_lst:
                if_else_cond = '++++ELSE++++'
                node = node1 + ', ' + str(curr_node)
                Nodeinfo_appnd = node + ' :: ' + if_else_cond + ' :: C;'
                Nodeinfo.append(Nodeinfo_appnd)

            elif re.search(assgmnt_pttrn, iter_line) is not None:
                node, Nodeinfo = get_assgnment(iter_line, node, Nodeinfo)

            elif re.search(inline_cond_pattern, iter_line) is not None:
                node, Nodeinfo = inline_cond_assgnmnt(iter_line, node, Nodeinfo)

            elif any(x in case_trig for x in iter_line_lst):
                node_discard, Nodeinfo, skip_lines_1 = nestedcasestatement(ifelse_blck, iter_no, node, Nodeinfo)
            elif 'if' in iter_line_lst and 'else' not in iter_line_lst:
                node_discard, Nodeinfo, skip_lines_1 = ifelse_CFG(ifelse_blck, iter_no, node, Nodeinfo)

            # ============================================= Loop Increment =============================================
            iter_no += skip_lines_1
            skip_lines_1 = 0
            iter_no += 1
            # ============================================= Loop Increment =============================================

    return node, Nodeinfo, skip_lines


# ================================================= Get If-Else Block ==================================================

# ============================================ Get Case Block & Conditions =============================================

def get_case_blck(lines: list[str], index: int = 0):
    '''
    Gets the case block from the list of lines in the .v or .sv file
    :param lines: List of lines from which it extracts case block
    :param index: index of the line to look for, default val = 0
    :return: a list containing the case block
    '''
    line = lines[index]
    line1 = re.sub(r'[\t\n\r]', '', line)
    line_lst = re.split(r'[() ]', line1)
    accptd_terms = ['case', 'casez', 'casex']
    # if any of the accepted forms of case is found then the loop starts
    # Set case_count =  1 as it is already on a case block
    case_count = 1
    i = 0
    if len([x for x in line_lst if x in accptd_terms]) > 0:
        shrt_list = lines[index + 1:]
        for i, l in enumerate(shrt_list):
            l = re.sub(r'[\t\n\r]', '', l)
            lst_l = re.split(r'[() ]', l)
            if 'case' in lst_l:
                case_count += 1
            elif 'endcase' in lst_l:
                case_count -= 1
            if case_count == 0:
                break
        out_lst = [re.sub(r'[\t\n\r]', '', x) for x in lines[index:index + i + 2] if x != '']
        # print(out_lst)
        return out_lst


def get_case_assign(case_sens: str, case_val: str):
    out_str = case_sens.strip() + ' == ' + case_val.strip()
    return out_str


def nestedcasestatement(lines: list[str], index4: int, node: str, Nodeinfo: list[str]):
    '''
    This Function will return the CFG formatted Case Nodeinfo
    :param lines: list of lines that is to be scanned
    :param index4: index of the start of the case block [ i.e., case(arg) ]
    :param node: the current node from which the function will update
    :param Nodeinfo: input CFG
    :return: Nodeinfo or the CFG after this function
    '''
    case_trig: list[str] = ['case', 'casex', 'casez']
    ifelse_trig: list[str] = ['if', 'else']
    line = re.sub(r"[\n\t]", "", lines[index4])
    case_trig_act: list[str] = [x for x in case_trig if x in re.split(r'[() ]', line)]
    case_trig_act_k = ''.join(case_trig_act)
    skip_lines: int = 0
    if len(case_trig_act) > 0:
        line0 = lines[index4]
        line = re.sub(r'[\t\n]', '', line0)
        linevalue = [x for x in re.split(r'[() ]', line) if x != ""]
        case_variable = linevalue[linevalue.index(case_trig_act_k) + 1].strip()
        case_blck = get_case_blck(lines, index4)
        skip_lines = len(case_blck) - 1
        # To iterate through the case block
        case_sens_lst = []  # To get all the conditions
        iter_value = 0  # To avoid illegal reference before assignment
        nextline = ''  # To avoid illegal reference before assignment
        curr_node: int = 0
        node1 = node
        node_root = node
        skip_lines_1 = 0
        # pattern0 = re.compile(r'\[([A-Za-z0-9_:.]+)]')
        pattern0 = re.compile(r"([\w.',\[\]{} ]+)\s*(:)\s*([\w.',\[\]{} ]+)\s*(<?=)\s*([\w.',\[\]{} ]+)\s*;")
        pattern1 = re.compile(r"([\w.',{}\[\] ]+)\s?(:)")
        assgmnt_pttrn = re.compile(r"\s*(assign)?\s*(.+)\s*(<?=)\s*(.+)\s*;")
        inline_cond_pattern = re.compile(r"\s*(assign)?\s*(.+)\s*(<?=)\s*\(?(.+)\)?\s*(\?)\s*(.+)\s*(:)\s*(.+)\s*;\s*")
        case_cond: str = ''
        while iter_value < len(case_blck[1:]):  # end of the case block will be lines[index4 + iter_value + 1]
            nextline = case_blck[iter_value + 1]
            if re.search(pattern0, nextline):
                case_assgn_lst = [x for x in list(re.findall(pattern0, nextline)[0]) if x != '']
                case_val = case_assgn_lst[case_assgn_lst.index(':') - 1]
                assgnment_trgt = case_assgn_lst[case_assgn_lst.index("<=") - 1] if "<=" in case_assgn_lst else case_assgn_lst[case_assgn_lst.index("=") - 1]
                assgnment_val = case_assgn_lst[case_assgn_lst.index("<=") + 1] if "<=" in case_assgn_lst else case_assgn_lst[case_assgn_lst.index("=") + 1]
                assgnment = assgnment_trgt + " <== " + assgnment_val
                case_cond = get_case_assign(case_variable, case_val)
                node = node1 + ', ' + str(curr_node)
                node_discard = ""
                curr_node += 1
                Nodeinfo_appnd = node + ' :: ' + case_cond + ' :: C;'
                Nodeinfo.append(Nodeinfo_appnd)
                Nodeinfo_appnd = node + ", 0" + " :: " + assgnment + " :: A;"
                Nodeinfo.append(Nodeinfo_appnd)

            elif re.search(pattern1, nextline) and not re.search(pattern0, nextline):
                case_assgn_lst = [x for x in list(re.findall(pattern1, nextline)[0]) if x != '']
                case_val = case_assgn_lst[case_assgn_lst.index(':') - 1]
                case_cond = get_case_assign(case_variable, case_val)
                node = node1 + ', ' + str(curr_node)
                curr_node += 1
                Nodeinfo_appnd = node + ' :: ' + case_cond + ' :: C;'
                Nodeinfo.append(Nodeinfo_appnd)

            elif 'if' in re.split(r"[() ]", nextline):
                node_discard, Nodeinfo, skip_lines_1 = ifelse_CFG(case_blck, (iter_value + 1), node, Nodeinfo)

            elif re.search(assgmnt_pttrn, nextline) is not None:
                    node, Nodeinfo = get_assgnment(nextline, node, Nodeinfo)

            elif re.search(inline_cond_pattern, nextline) is not None:
                node, Nodeinfo = inline_cond_assgnmnt(nextline, node, Nodeinfo)

            elif len([x for x in case_trig if x in re.split(r'[() ]', nextline)]) > 0:
                node_discard, Nodeinfo, skip_lines_1 = nestedcasestatement(case_blck, (iter_value + 1), node, Nodeinfo)

            iter_value += skip_lines_1
            skip_lines_1 = 0
            iter_value += 1
    # print(lines[index4 + iter_value + 1])
    else:
        print('No Case Block Found')

    return node, Nodeinfo, skip_lines


# ============================================ Get Case Block & Conditions =============================================

# =========================================== Get Assignment in common form ============================================
def get_assgnment(line: str, node: str, Nodeinfo: list[str]):
    '''
    From Assignment it returns the assignment in the CFG format
    :param line: the line that contains the assignment
    :param node: Current Node on the CFG
    :param Nodeinfo: CFG before the function runs
    :return: Node and CFG after the assignment is done
    '''
    skip_term_lst = ['if', 'defparam', 'parameter', 'logic']
    assgmnt_pttrn_1 = re.compile(r"\s*(assign)?\s*(.+)\s*(<=)\s*(.+)\s*;\s*")
    assgmnt_pttrn_2 = re.compile(r"\s*(assign)?\s*(.+)\s*(=)\s*(.+)\s*;\s*")
    line_lst = line.split()
    if re.search(assgmnt_pttrn_1, line) is None and re.search(assgmnt_pttrn_2, line) is None:
        return node, Nodeinfo
    line_s = ""
    if not any(x for x in line_lst if x in skip_term_lst):
        if re.search(assgmnt_pttrn_1, line) is not None:
            line_lst = [x.strip() for x in list(re.findall(assgmnt_pttrn_1, line)[0]) if x != ""]
            assgn_trgt: str = line_lst[line_lst.index("<=") - 1]
            assgn_val: str = line_lst[line_lst.index("<=") + 1]
            line_s = node + " :: " + assgn_trgt.strip() + " <== " + assgn_val.strip()
        elif re.search(assgmnt_pttrn_2, line) is not None:
            line_lst = [x.strip() for x in list(re.findall(assgmnt_pttrn_2, line)[0]) if x != ""]
            assgn_trgt: str = line_lst[line_lst.index("=") - 1]
            assgn_val: str = line_lst[line_lst.index("=") + 1]
            line_s = node + " :: " + assgn_trgt.strip() + " <== " + assgn_val.strip()
        Nodeinfo_appnd = line_s + ' :: A;'
        Nodeinfo.append(Nodeinfo_appnd)

        return node, Nodeinfo


def inline_cond_assgnmnt(line: str, node: str, Nodeinfo: list[str]):
    pattern_1 = re.compile(r"\s*(assign)?\s*(.+)\s*(<=)\s*\(?(.+)\)?\s*(\?)\s*(.+)\s*(:)\s*(.+)\s*;\s*")
    pattern_2 = re.compile(r"\s*(assign)?\s*(.+)\s*(=)\s*\(?(.+)\)?\s*(\?)\s*(.+)\s*(:)\s*(.+)\s*;\s*")
    cond_pattern_wthsgn = re.compile(r"\(?\s?([\w'{}:\[\],.]+)\s?(!=|==|>|>=|<|<=)\s?([\w'{}:\[\],.]+)\s?\)?")
    cond_pattern_wthoutsgn = re.compile(r"\(?\s?(!)?\(?([\w'{}:\[\],.]+)\s?\)?\)?")
    cond_pttrn_sngl_wrd = re.compile(r"\(?([\w'{}:\[\],.]+)\s?\)?")
    chck_groups: list = []

    if re.search(pattern_1, line) is not None:
        chck_groups = [x for x in list(re.findall(pattern_1, line)[0]) if x != '']
        sgn_flag: bool = True
    elif re.search(pattern_2, line) is not None:
        chck_groups = [x for x in list(re.findall(pattern_2, line)[0]) if x != '']
        sgn_flag: bool = False

    cond = [x for x in chck_groups if chck_groups.index(x) > chck_groups.index('=') if
            chck_groups.index(x) < chck_groups.index('?')]
    # chck = re.search(pattern0, line).group()

    flip_dict = {
        '==': '!=',
        '!=': '==',
        '>': '<=',
        '<': '>=',
        '>=': '<',
        '<=': '>'
    }

    cond_str: str = ' '.join(cond)
    cond_t = ''
    cond_f = ''
    # if re.search(pattern_1, line) is not None and re.search(pattern_2, line) is not None:
    if re.search(cond_pattern_wthsgn, cond_str):
        cond = list(re.findall(cond_pattern_wthsgn, cond_str)[0])
        cond_str = ' '.join(cond)
        cond_t = cond_str
        flip_item = cond[1]
        cond_f = cond.copy()
        cond_f[1] = flip_dict[flip_item]
        cond_f = ' '.join(cond_f)
    elif re.search(cond_pattern_wthoutsgn, cond_str):
        cond = list(re.findall(cond_pattern_wthoutsgn, cond_str)[0])
        cond_str = ''.join(list(re.findall(cond_pttrn_sngl_wrd, cond_str)[0]))
        cond_t = cond_str + ' == 1' if '!' not in cond else cond_str + ' == 0'
        cond_f = cond_str + ' == 0' if '!' not in cond else cond_str + ' == 1'

        node0 = node + ', 0'
        Nodeinfo_appnd0 = node0 + ' :: ' + cond_f + ' :: ' + 'C'
        Nodeinfo.append(Nodeinfo_appnd0)
        if sgn_flag:
            Nodeinfo_appnd0 = node0 + ' :: ' + chck_groups[chck_groups.index("<=") - 1] + ' <== ' + chck_groups[chck_groups.index(':') + 1] + ' :: ' + 'A'
        else:
            Nodeinfo_appnd0 = node0 + ' :: ' + chck_groups[chck_groups.index("=") - 1] + ' <== ' + chck_groups[chck_groups.index(':') + 1] + ' :: ' + 'A'
        Nodeinfo.append(Nodeinfo_appnd0)

        node1 = node + ', 1'
        Nodeinfo_appnd1 = node1 + ' :: ' + cond_t + ' :: ' + 'C'
        Nodeinfo.append(Nodeinfo_appnd1)
        if sgn_flag:
            Nodeinfo_appnd1 = node0 + ' :: ' + chck_groups[chck_groups.index("<=") - 1] + ' <== ' + chck_groups[chck_groups.index(':') - 1] + ' :: ' + 'A'
        else:
            Nodeinfo_appnd1 = node0 + ' :: ' + chck_groups[chck_groups.index("=") - 1] + ' <== ' + chck_groups[chck_groups.index(':') - 1] + ' :: ' + 'A'
        Nodeinfo.append(Nodeinfo_appnd1)

        return node, Nodeinfo


# =========================================== Get Assignment in common form ============================================

def get_module_name(lines: list[str], index: int = 0):
    module_name = ''
    while index < len(lines):
        line_lst = [x for x in re.split(r'[() ;]', lines[index]) if x != '']
        if 'module' in line_lst:
            module_name = line_lst[line_lst.index('module') + 1]
            break
        index += 1
    if module_name == "":
        return "Property_CFG"

    return module_name


# ======================================================================================================================
# =================================================== CFG Generation ===================================================
# ======================================================================================================================

def gen_CFG(file_loc: str):
    Preprocessing.preprocess_single(file_loc)
    with open(file_loc) as fl:
        lines = fl.readlines()
        fl.close()

    module_name = get_module_name(lines)

    case_keywrd: list[str] = ['case', 'casex', 'casez']
    ifelse_keywrd: list[str] = ['if']
    always_keywrd: list[str] = ['always', 'always_ff', 'always_comb', 'always_latch']
    assign_keywrd: list[str] = ['assign']
    skip_term_lst = ['if', 'defparam', 'parameter', 'logic']
    inline_cond_pattern = re.compile(
        r"\s*(assign)?\s*(.+)\s*(<?=)\s*\(?(.+)\)?\s*(\?)\s*(.+)\s*(:)\s*(.+)\s*;\s*")
    assgnmnt_pattern_o_alwys = re.compile(r"\s*(assign)?\s*([\w.\[\]:'()&|=<>!~ ]+)\s*(<?=)\s*([\w.\[\]:'()&|=<>!~ ]+)\s*;")
    node_root = 'Module: ' + module_name
    Nodeinfo: list[str] = []
    line_no: int = 0
    skip_lines: int = 0
    curr_node: int = 0
    while line_no < len(lines):
        line0 = lines[line_no]
        line = re.sub(r'[\t\n]', '', line0)
        line_lst = re.split(r'[() ]', line)
        # print(line.replace('\n',''), '\t', line_no)
        node = node_root + ' :: ' + str(curr_node)
        if re.search(inline_cond_pattern, line) is not None and not any(x in line_lst for x in skip_term_lst):
            node, Nodeinfo = inline_cond_assgnmnt(line, node, Nodeinfo)
            curr_node += 1
        elif re.search(assgnmnt_pattern_o_alwys, line) is not None and not any(x in line_lst for x in skip_term_lst):
            node, Nodeinfo = get_assgnment(line, node, Nodeinfo)
            curr_node += 1
        if any(x in always_keywrd for x in line_lst):
            node, Nodeinfo, skip_lines = always_blck_CFG(lines, line_no, node, Nodeinfo)
            curr_node += 1

        # =============================================== Loop Increment ===============================================
        line_no += skip_lines
        skip_lines = 0
        line_no += 1
        # =============================================== Loop Increment ===============================================

    return module_name, Nodeinfo
# =================================================== CFG Generation ===================================================


# ========================================================================================================================================================
# ====================================================================== Main Code =======================================================================
# ========================================================================================================================================================
def main():
    # ==================================================================================================================
    # ================================================ Folder Location =================================================
    # ==================================================================================================================
    root_loc: str = 'C:/Users/ssm220008/OneDrive - The University of Texas at Dallas/DAC_ext'
    # root_loc: str = 'D:/DAC_ext'
    RTL_loc: str = 'SoC_1/All_RTL/'
    srch_rtl: str = os.path.join(root_loc, RTL_loc)
    CFG_loc: str = 'Extracted_CFG'
    Dest_loc: str = os.path.join(root_loc, CFG_loc)
    Property_loc: str = os.path.join(root_loc, "spec.txt")
    # ================================================ Folder Location =================================================

    accpt_frmts = ['.v', '.sv']
    file_lst = [x for x in os.listdir(srch_rtl) if os.path.splitext(x)[-1] in accpt_frmts]
    # file_lst = ["system.sv"]

    # ================================================= CFG generation =================================================
    for iter_file in file_lst:
        iter_file_loc: str = os.path.join(srch_rtl, iter_file)
        module_name, Nodeinfo = gen_CFG(iter_file_loc)
        print(module_name)

        for iter_num, items in enumerate(Nodeinfo):
            Nodeinfo[iter_num] = items + '\n'
        try:
            os.mkdir(Dest_loc)
        except:
            pass

        with open(os.path.join(Dest_loc, module_name + '.txt'), 'w+') as fl:
            fl.writelines(Nodeinfo)
    # ================================================= CFG generation =================================================

    # ================================================== Property CFG ==================================================
    module_name, Nodeinfo = gen_CFG(Property_loc)
    print(module_name)
    
    for iter_num, items in enumerate(Nodeinfo):
        Nodeinfo[iter_num] = items + '\n'
    
    with open(os.path.join(Dest_loc, module_name + '.txt'), 'w+') as fl:
        fl.writelines(Nodeinfo)
    print("\n================+++++\tDone\t+++++================\n")
    # ================================================== Property CFG ==================================================



# ========================================================================================================================================================
# ========================================================================================================================================================
# ========================================================================================================================================================
if __name__ == "__main__":
    main()
