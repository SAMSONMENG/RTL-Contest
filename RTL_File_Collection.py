import os
import shutil


def get_flders(paths: str) -> list[str]:
    '''
    get a list of folders in a path
    :param paths: Root Path from where the list of folder is being generated
    :return: list of folders in the Root path
    '''
    root_path = os.path.abspath(paths)
    lst_flder = [x for x in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, x))]
    return lst_flder


def get_fls(paths: str) -> list[str]:
    '''
    Generate a list of files in a path
    :param paths: Root Path from where a list of files is being generated
    :return: list of files in the Root path
    '''
    root_path = os.path.abspath(paths)
    lst_fl = [x for x in os.listdir(root_path) if os.path.isfile(os.path.join(root_path, x))]
    return lst_fl


def get_rtl(root_path: str, dest: str, rtl_fls: list[str] = []) -> list[str]:
    '''
    Copy all RTL Files from the Project Directory to All_RTL
    :param root_path: Project Directory
    :param dest: Copy Derectory
    :param rtl_fls: rtl file list
    :return: A list of all the RTL files present in the project
    '''
    root_pth = os.path.abspath(root_path)
    # create Destination Directory
    try:
        os.mkdir(dest)
    except:
        print('Folder Already Exists')
    # get list of all files
    lst_fl = get_fls(root_pth)
    # get list of all folders
    lst_fldr = get_flders(root_pth)
    # list of extensions that are rtl files
    accptd_extnsn = ['.v', '.sv']
    # loop through the file list to get rtl files in the root directory
    for fls in lst_fl:
        if os.path.splitext(fls)[-1] in accptd_extnsn:
            rtl_fls.append(fls)
            print(os.path.join(root_path, fls))
            try:
                shutil.copyfile(os.path.join(root_path, fls), os.path.join(dest, fls))
            except:
                print('File Already Exists')
    # loop through the file list to get rtl folders in the root directory
    lst_fl.clear()
    for fldr in lst_fldr:
        if fldr != 'All_RTL':
            fldr_address = os.path.join(root_pth, fldr)
            lst_fl = get_fls(fldr_address)
            for fls in lst_fl:
                if os.path.splitext(fls)[-1] in accptd_extnsn:
                    rtl_fls.append(fls)
                    try:
                        shutil.copyfile(os.path.join(fldr_address, fls), os.path.join(dest, fls))
                    except:
                        print('File Already Exists')
            lst_fldr = get_flders(fldr_address)
            # run till there's no subfolder left
            if len(lst_fldr) > 0:
                get_rtl(fldr_address, dest, rtl_fls)
    return rtl_fls


# ========================================================================================================================================================
# ==================================================================== Main Function =====================================================================
# ========================================================================================================================================================

# =================================================== Path Directory ===================================================
root_path = os.path.abspath('C:/Users/ssm220008/OneDrive - The University of Texas at Dallas/DAC_ext')
rtl_fldr_path = os.path.join(root_path, 'SoC_1')
cpy_dest_path = os.path.join(rtl_fldr_path, 'All_RTL')
# ======================================================================================================================
get_rtl(rtl_fldr_path, cpy_dest_path)
