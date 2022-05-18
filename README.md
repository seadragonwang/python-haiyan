# python-haiyan
All kinds of python utility functions needed by haiyan

# Intersect 2 files using one column in each file, the first file will be a small file
python data_analyzer --action intersect --source_file file_name --source_file_2 file_name_2 --head 0/2 --columns 0/0 --output_file result.txt

# Extract columns from a file
### Usages:
python data_analyzer --action extract --source_file file_name -column column_index/column_separator/field_indices/column_names --output_file output_file_name

###For example:
python data_analyzer --action extract --source_file test.avinput.txt --column "17/:/1-2/AD,RD" --head False --output_file test_avinput_output.csv

# Split columns from a file
### Usages:
python data_analyzer --action split --source_file file_name -column column_index/column_separator/field_indices/column_names --output_file output_file_name

###For example:
python data_analyzer --action split --source_file test_avinput_output.csv --column "0/,/0-1/AD,RD" --head True --output_file test_avinput_split_output.csv

# Insert a new column with ratio of 2 columns from a file
### Usages:
python data_analyzer --action divide --source_file file_name -columns column_1_index/column_2_index/column_name,column_1_index/column_2_index/column_name --head True --output_file output_file_name

###For example:
python data_analyzer --action divide --source_file test_avinput_split_output.csv --columns "0/2/Freq" --head True --output_file test_avinput_split_ratio_output.csv

# Insert a new column with sum of 2 columns from a file
### Usages:
python data_analyzer --action add --source_file file_name -columns column_1_index/column_2_index/column_name,column_1_index/column_2_index/column_name --head True --output_file output_file_name

###For example:
python data_analyzer --action add --source_file test_avinput_split_output.csv --columns "0/2/Freq" --head True --output_file test_avinput_split_ratio_output.csv

# Merge files
### Usages:
python data_analyzer --action merge --source_file file_name_1:True,file_name_2:False --output_file output_file_name
 
### For example:
python data_analyzer --action merge --source_file test.amino.txt:True,test_avinput_split_ratio_output.csv:True --output_file merged_output_file.csv

# Search by gene name
### Usages:
python data_analyzer --action search_by_gene_name --source_file file_name_1 --column_index 15 --gene_name nf1 --column_delimiter tab --gene_delimiter ; --head True --output_file output_file_name

### For example:
python data_analyzer --action search_by_gene_name --source_file search-by-gene-name.txt --columns 8 --column_delimiter tab --gene_delimiter ; --head True --gene_name WASH7P --output_file search_by_gene_name_output.txt

# Get gene name by gene feature
### Usages
python data_analyzer --action get_gene_name --source_file file_name --columns 2 --head True --column_delimiter , --output_file results.csv

### For example
python data_analyzer --action get_gene_name --source_file annoted_myDiff50p.csv --columns 2 --head True --column_delimiter , --output_file results.csv

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

# Strip a field from a column
python3 data_analyzer --action strip --source_file test.csv --column_index 0 --head False --column_delimiter , --field_index 2 --field_delimiter _ --output_file results.csv

# Prefix a string to  a column
python3 data_analyzer --action prefix --source_file test.csv --column_index 0 --head False --prefix chr1: --column_delimiter , --output_file results.csv