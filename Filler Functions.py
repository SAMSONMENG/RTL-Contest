def Cmmnt_filler(cmmnt: str = '', block: bool = False, fill_len: int = 116) -> str:
    filled_cmmnt: str = ''
    if block:
        filler = ''
        for i in range(fill_len + 2):
            filler += '='
        filler = '# ' + filler
    if cmmnt == '':
        eq: int = fill_len
        for i in range(eq):
            filled_cmmnt += '='
        filled_cmmnt = '# ' + filled_cmmnt
        if block:
            filled_cmmnt = filler + '\n' + filled_cmmnt + '\n' + filler
            return filled_cmmnt
        else:
            return filled_cmmnt

    eq: int = fill_len - len(cmmnt)
    for i in range(eq // 2):
        filled_cmmnt += '='
    filled_cmmnt = '# ' + filled_cmmnt + ' ' + cmmnt + ' ' + filled_cmmnt
    if eq % 2 != 0:
        filled_cmmnt += '='
    if block:
        filled_cmmnt = filler + '\n' + filled_cmmnt + '\n' + filler
        return filled_cmmnt
    else:
        return filled_cmmnt


# def main():
# print(Cmmnt_filler("Get If/Else Condition"))
print(Cmmnt_filler("Property CFG", 0, 112))
# print(Cmmnt_filler('Main Code', 1, 150))


# if __name__ == "__main__":
#     main()
#     print('Code Ran Successfully')
