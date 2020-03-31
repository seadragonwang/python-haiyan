# python-haiyan
All kinds of python utility functions needed by haiyan

# Merge files
Usages:

Source files are tab seperated, and useful information should be in 17th and 18th columns of first source file, example as below

17th column:

GT:GQ:SDP:DP:RD:AD:FREQ:PVAL:RBQ:ABQ:RDF:RDR:ADF:ADR

18th column:

1/1:58:11:11:0:11:100%:1.4176E-6:0:45:0:0:6:5

then from 4th to 7th values will be extracted as seperate columns, 17th column is extracted only once as header.
Here is the example:

DP, RD, AD, FREQ

11, 0, 11, 100%


python3 merge_files.py --source_file_1 [1st source file] --source_file_2 [2nd source file] --output_file [output file]

# Deduplicate rows of csv file based on gene name

python3 deduplicate_gene_name.py --source_file [source file] --output_file [output file]

# Calculate the ratio of columns, source_file_2 is optional,
## if only source_file_1 exist, it will only calculate ration with this file. For example, you want to have
1st, 2nd, 5th, 6th and 2nd/6th in output file, then

python3 calculate_ratio.py --source_file_1 [1st source file] --columns 0,1,4,5,2/5 --output_file [output file]

## if there are 2 source files, and you want to have 1st, 3rd(1st source file)/3rd(2nd source file), 5th(1st source file)/5th(2nd source file)

python3 calculate_ratio.py --source_file_1 [1st source file] --source_file_2 [2nd source file] --columns 0,2/2,4/4 --output_file [output file]

# Intersect 2 files based on gene name.

python3 gene_intersect.py --source_file_1 [1st source file] --source_file_2 [2nd source file] --columns [0,7] --output_file [output file]
