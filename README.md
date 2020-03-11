# python-haiyan
All kinds of python utility functions needed by haiyan


Usages:

Source files are tab seperated, and useful information should be in 17th and 18th columns of first source file, example as below

17th column:

GT:GQ:SDP:DP:RD:AD:FREQ:PVAL:RBQ:ABQ:RDF:RDR:ADF:ADR

18th column:

1/1:58:11:11:0:11:100%:1.4176E-6:0:45:0:0:6:5

then from 4th to 7th values will be extracted as seperate columns, 17th column is extracted only once as header.
Here is the example:

DP, RD, AD, FREQ\n
11, 0, 11, 100%


python3 merge_files.py --source_file_1 [1st source file] --source_file_2 [2nd source file] --output_file [output file]
