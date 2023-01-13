import os
import re


def CFG_Node_brkdwn(line: str) -> tuple:
    CFG_pattern = re.compile(r"\s*(.+)\s*::\s*(.+)\s*::\s*(.+)\s*::\s*(.+)\s*;\s*")
    # assgn_cond_pattern = re.compile(r"\s*(.+)\s*(<==|<=?|=?>|==|!=)\s*(.+)\s*")
    assgn_cond_pattern = re.compile(r"\s*(.+)\s*(<==)\s*(.+)\s*")
    line_lst: list[str] = list(re.findall(CFG_pattern, line)[0])
    branch: list[str] = [x.strip() for x in re.split(r",", line_lst[1])]
    statemnt_type: str = line_lst[3].strip()
    statemnt: str = [x.strip() for x in list(re.findall(assgn_cond_pattern, line_lst[2])[0])] if statemnt_type == "A" else [line_lst[2].strip()]

    return branch, statemnt, statemnt_type


def CFG_file_brkdown(lines: list[str]) -> list[str]:
    for iter_no, iter_line in enumerate(lines):
        iter_line = re.sub(r"\n", "", iter_line)
        brnch, sttmnt, sttmnt_type = CFG_Node_brkdwn(iter_line)
        lines[iter_no] = [brnch, sttmnt, sttmnt_type]

    return lines


# def CFG_get_upper(lines: list[str], trgt: str, out_lst = None):
#     get_node = []
#     for iter_no, iter_line in enumerate(lines):
#         if iter_line[1].strip() == trgt.strip():
#             get_node = iter_line[0] if iter_line[2] == "A" else iter_line[0][:-1]
#             out_lst.append(iter_line)
#             break
#     if get_node != []:
#         for iter_no, iter_line in enumerate(lines):
#             if iter_line[0] == get_node:
#                 out_lst = CFG_get_upper(lines, iter_line[1], out_lst)
#                 break
#         return out_lst
#     else:
#         return out_lst

def fnd_statemnt(lines: list[str], trgt_line: str):
    trgt_line_lst: list = CFG_Node_brkdwn(trgt_line)
    CFG_branch: list = []
    iter_root: int = 0
    while iter_root < len(lines):
    # for iter_line_lst in lines:
        iter_line_lst = lines[iter_root]
        if trgt_line_lst[2] == "A":
            if iter_line_lst[1][0:1] == trgt_line_lst[1][0:1]:
                CFG_branch.append(iter_line_lst)
                # print("Assignment:\t", iter_line_lst)
            print(CFG_branch)
        else:
            if iter_line_lst[1] == trgt_line_lst[1]:
                print("Condition:\t", iter_line_lst)
                i_inner: int = iter_root                # iterator for the loop
                while i_inner < len(lines):
                    iter_line_lst_2 = lines[i_inner]
                    if iter_line_lst[0] == iter_line_lst_2[0][0:len(iter_line_lst[0])]:
                        CFG_branch.append(iter_line_lst_2)
                    i_inner += 1
                print(CFG_branch)
        iter_root += 1


# def fnd_prop(lines: list[str], trgt: list[str]):
#     assgnmnt_pttrn = re.compile(r"\s*(.+)\s*<==\s*(.+)")
#     for iter_trgt_line in trgt[::-1]:
#         iter_trgt_line_lst = CFG_Node_brkdwn(iter_trgt_line)
#         if iter_trgt_line_lst[2] != "A":
#             fnd_cond



def main():
    # ==================================================================================================================
    # ================================================ Folder Location =================================================
    # ==================================================================================================================
    root_loc: str = 'C:/Users/ssm220008/OneDrive - The University of Texas at Dallas/DAC_ext'
    # root_loc: str = 'D:/DAC_ext'
    RTL_loc: str = 'SoC_1/All_RTL/'
    srch_rtl: str = os.path.join(root_loc, RTL_loc)
    CFG_fldr_loc: str = 'Extracted_CFG'
    CFG_loc: str = os.path.join(root_loc, CFG_fldr_loc)
    # ================================================ Folder Location =================================================

    tst_file: str = "memory_control.txt"
    with open(os.path.join(CFG_loc, tst_file), "r") as fl:
        lines = fl.readlines()
        fl.close()

    lines = CFG_file_brkdown(lines)
    # print(lines)

    # trget_node: str = "ccif.dwait[dsource] <== 0"
    # brkn_dwn_lines: list[str] = CFG_file_brkdown(lines)
    # outlst = CFG_get_upper(lines, trget_node)
    # outlst = outlst[::-1]
    # print(outlst)

    prprty_file: str = "Property_CFG.txt"
    with open(os.path.join(CFG_loc, prprty_file), "r") as fl:
        prprty_lines = fl.readlines()
        fl.close()

    print(prprty_lines[-4])
    fnd_statemnt(lines, prprty_lines[-0])



if __name__ == "__main__":
    main()