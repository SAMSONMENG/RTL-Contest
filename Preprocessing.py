import os
import re


def purge_blck(txt_fl: str) -> str:

    pattern_block = re.compile(r"/\*(\*(?!/)|[^*]+)*\*/")
    txt_fl = re.sub(pattern_block, '', txt_fl)

    return txt_fl


def purge_line(txt_fl: str) -> str:

    pattern_line = re.compile(r"(//.*)")
    txt_fl = re.sub(pattern_line, '', txt_fl)

    return txt_fl


def purge_cmmnts(file_path: str):
    fl = open(file_path, 'r')
    full_text = fl.read()
    fl.close()

    purged_line_txt = purge_line(full_text)
    purged_blck_txt = purge_blck(purged_line_txt)

    fl = open(file_path, 'w+')
    fl.write(purged_blck_txt)
    fl.close()


def purge_blank(file_path: str):
    fl = open(file_path, 'r')
    fl_txt_list = fl.readlines()
    fl.close()

    fl_txt_list_purged = [x for x in fl_txt_list if re.sub(r'[\t\r\n ]', '', x) != '']

    fl = open(file_path, 'w+')
    fl.writelines(fl_txt_list_purged)
    fl.close()


def purge_indentation(file_path: str):
    fl = open(file_path, 'r')
    fl_txt_list = fl.readlines()
    fl.close()

    fl_txt_list_purged = [x.lstrip() for x in fl_txt_list if x != '']

    fl = open(file_path, 'w+')
    fl.writelines(fl_txt_list_purged)
    fl.close()


def purge_defparam(file_path: str):
    with open(file_path, 'r') as fl:
        full_txt = fl.read()
        fl.close()

    try:
        strt_defparam = full_txt.index('defparam')
        end_defparam = full_txt.index('defparam') + full_txt[full_txt.index('defparam'):].index(';')
        rmv_snippet = full_txt[strt_defparam:end_defparam + 1]
        full_txt = full_txt.replace(rmv_snippet, '')
    except:
        pass
        # print('No defparam')
    with open(file_path, 'w+') as fl:
        fl.write(full_txt)
        fl.close()


def mult2single(file_path: str):
    '''
    Converts Multiline Equations into a single function
    :param file_path: Absolute/Relative path to the file to process
    :return: formats the file
    '''
    with open(file_path, 'r') as fl:
        full_txt_lines = fl.readlines()
        fl.close()

    updated_txt_lst = []
    iter_num = 0
    while iter_num < len(full_txt_lines):
        line = full_txt_lines[iter_num]
        terms_to_ignore = ['`include', 'begin', 'end', 'case', 'casex', 'casez', 'endcase']
        terms2brk_out_of_loop = ['begin', 'end', 'endmodule', 'endcase']
        line_lst = re.split('[\s()]', line)
        if any(lst_itm in line_lst for lst_itm in terms_to_ignore):
            iter_num += 1
            continue
        # concat_till_line_no = 0
        if line.replace('\n', '').rstrip()[-1] != ';':
            iter_num0 = iter_num + 1
            if iter_num0 < len(full_txt_lines):
                while iter_num0 < len(full_txt_lines):
                    if any(item in full_txt_lines[iter_num0].split() for item in terms2brk_out_of_loop):
                        break
                    elif full_txt_lines[iter_num0].replace('\n', '').rstrip()[-1] == ';':
                        line = line.replace('\n', '').rstrip() + ' ' + full_txt_lines[iter_num0].strip() + '\n'
                        # print(full_txt_lines[iter_num0].strip())
                        full_txt_lines.pop(iter_num0)
                        break
                    else:
                        line = line.replace('\n', '').rstrip() + ' ' + full_txt_lines[iter_num0].strip()
                        full_txt_lines.pop(iter_num0)

        full_txt_lines[iter_num] = line
        iter_num += 1

        with open(file_path, 'w+') as fl:
            fl.writelines(full_txt_lines)
            fl.close()

# ========================================================================================================================================================
# ================================================================= Project Directories ==================================================================
# ========================================================================================================================================================
# root_loc: str = 'C:/Users/ssm220008/OneDrive - The University of Texas at Dallas/DAC_ext'
# root_loc: str = 'D:/DAC_ext'
# RTL_loc: str = 'SoC_1/All_RTL/'
# srch_rtl: str = os.path.join(root_loc, RTL_loc)
# ========================================================================================================================================================
# =================================================================== Preprocess Codes ===================================================================
# ========================================================================================================================================================

def preprocess(loc: str):
    accpt_frmt = ['.v', '.sv']
    lst_all = os.listdir(srch_rtl)
    lst_fl = [x for x in lst_all if os.path.isfile(os.path.join(srch_rtl, x))]
    lst_rtl = [x for x in lst_fl if os.path.splitext(x)[-1] in accpt_frmt]

    for x in lst_rtl:
        print(x)
        pth = srch_rtl + x
        purge_cmmnts(pth)
        purge_blank(pth)
        mult2single(pth)

def preprocess_single(file_loc: str):
    accpt_frmt = [".v", ".sv", ".txt"]
    if os.path.splitext(file_loc)[-1] in accpt_frmt:
        purge_cmmnts(file_loc)
        purge_blank(file_loc)
        mult2single(file_loc)
    else:
        print("File not Supported")