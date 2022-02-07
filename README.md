# RTL-Contest

Concolic Testing on RTL for Detecting Security Vulnerabilities

Getting Started

Prerequisites:

• Icarus Verilog

• Python 3.8

Getting Started

• Create a directory \RTL\RTLVerilog and add the Verilog files to the folder RTLVerilog.

• Execute the module_track python file.

• This copies the files to a folder All_RTL in the RTL folder.

• Execute the CFG-Path Specification python file.

• This creates a list of nodes with every condition and assignment statements.

• Select a targetnode for the path specification and provide the target statement.

• This generates the path specification along with the input values required to reach the node.

• The inputvalues are stored in the file input_values.txt.

• In the concolic_testing python file, add the clock signals to the variable togglevariables at line 742 and execute the the python file.

• This creates and executes the template modlue and testbench created for concolic testing. These files will be stored in the folder C:\iverilog

• In the testcase.txt file, add testcases that have to be verified and run the testcases.py file.
