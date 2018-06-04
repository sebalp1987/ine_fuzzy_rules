import os

os.chdir('Z:\ADVANCED ANALYTICS\ZFINDER\AA\z_finder_1.0.1\doc_output\\file_preprocessed\\batch_files')

input_file = open('before_pca.csv', 'r', newline='')
i=0
for lines in input_file:
    print(lines)
    line = input_file.readline()
    i+=1
    if i < 5:
        print(line)
    else:
        break
