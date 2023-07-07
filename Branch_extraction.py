import os
import re


def CFG_brkdwn(line_lst: list[str]):
    """

    Parameters
    ----------
    line_lst: Textfile, containing CFG parsed as a list.

    Returns
    -------
    CFG broken down into it's core components as a list

    """
    brkn_lst = []
    for each_line in line_lst:
        each_line_lst = re.split("::", each_line)
        each_line_lst = [x.strip() for x in each_line_lst if type(x) is str]
        each_line_lst[1]: list[str] = re.split(",", each_line_lst[1])
        each_line_lst[1] = [x.strip() for x in each_line_lst[1]]
        each_line_lst[-1] = re.sub(";", "", each_line_lst[-1]).strip()
        brkn_lst.append(each_line_lst)

    return brkn_lst

def fnd_parent_brnch(brkndwn_lst, strt_branch_line):
    """

    Parameters
    ----------
    brkndwn_lst         :   line_lst - from Textfile, containing CFG parsed as a list - broken down into the parts of CFG
    strt_branch_line    :   current statement, parent/guard statement of which is to be determined

    Returns
    -------
    parent/guard statement of the strting brnch line

    """
    curr_brnch = strt_branch_line[1]
    curr_brnch_type = strt_branch_line[3]
    nxt_brnch = None

    if curr_brnch_type.strip() == "A":
        nxt_brnch = curr_brnch
    else:
        nxt_brnch = curr_brnch[:-1]

    nxt_brnch_line = [x for x in brkndwn_lst if x[1] == nxt_brnch][0]

    return nxt_brnch, nxt_brnch_line


def extract_pth(brkndwn_lst, strt_branch_line):
    """

    Parameters
    ----------
    brkndwn_lst         : line_lst - from Textfile, containing CFG parsed as a list - broken down into the parts of CFG
    strt_branch_line    : starting statement from which the complete path is to be extracted.

    Returns
    -------
    The complete path that leads to the starting statement

    """
    curr_brnch = strt_branch_line
    brnch_inf = strt_branch_line[1]
    cmplt_path = []

    loop_flg = True
    i = 0
    while(loop_flg):
        if curr_brnch[3].strip() == "Alws":
            cmplt_path.append(curr_brnch)
            loop_flg = False
            pass
        elif len(curr_brnch) <= 1:
            cmplt_path.append(curr_brnch)
            loop_flg = False
            pass
        else:
            cmplt_path.append(curr_brnch)
            brnch_inf, curr_brnch = fnd_parent_brnch(brkndwn_lst, curr_brnch)

    return cmplt_path


def main():
    # ==================================================================================================================
    # ================================================ Folder Location =================================================
    # ==================================================================================================================
    # root_loc: str = 'C:/Users/ssm220008/OneDrive - The University of Texas at Dallas/DAC_ext'
    root_loc: str = os.path.abspath('/Users/Samit/Phd Files/Research Projects/RTL_Concolic_Testing-main')
    RTL_loc: str = ''
    srch_rtl: str = os.path.join(root_loc, RTL_loc)
    CFG_loc_fldr_name: str = 'Extracted_CFG'
    CFG_loc: str = os.path.join(root_loc, CFG_loc_fldr_name)
    Property_loc: str = os.path.join(root_loc, "SoC_2", "spec.txt")
    # ================================================ Folder Location =================================================

    file_name: str = "adc_ctrl_fsm.txt"
    file_loc: str = os.path.join(CFG_loc, file_name)
    with open(file_loc, "r") as fl:
        line_lst = fl.readlines()
        fl.close()

    print(line_lst)
    CFG_brkndwn = CFG_brkdwn(line_lst)
    print(CFG_brkndwn)

    prnt_val = fnd_parent_brnch(CFG_brkndwn, CFG_brkndwn[2])
    print("nxt_brnch_line :\t", prnt_val)
    print(extract_pth(CFG_brkndwn, CFG_brkndwn[2]))

if __name__ == "__main__":
    main()