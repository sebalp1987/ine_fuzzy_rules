import pandas as pd
import STRING
import unidecode

def censo_clean(path):

    input_file = open(path, 'r', newline='')

    dataframe_list = []
    counter = 0

    try:
        for lines in input_file:

            # We get the necessary values from the Censo Callejero
            line = input_file.readline()
            cpro = line[0:2]
            cmun = line[2:5]
            dist = line[5:7]
            secc = line[7:10]
            impar = line[262]
            inferior = line[263:267]
            superior = line[268:272]
            cp = line[257:262]
            nombre = line[165:190]
            total_code = cpro + '-' + cmun + '-' + dist + '-' + secc

            dataframe_list_row = [cpro, cmun, dist, secc, impar, inferior, superior, cp, nombre, total_code]
            dataframe_list.append(dataframe_list_row)

            counter += 1

            if counter % 1000 == 0:
                print(counter)

    except IndexError:
        pass

    # We create a dataframe
    censo_df = pd.DataFrame(dataframe_list, columns=['cpro', 'cmun', 'dist', 'secc', 'impar', 'inferior', 'superior',
                                                     'cp', 'nombre', 'total_code'])

    # Clean CENSO symbols
    for i in STRING.symbols:
        censo_df['nombre'] = censo_df['nombre'].str.replace(i, '')

    # We remove useless words
    censo_df['nombre'] = censo_df['nombre'].apply(
        lambda x: ' '.join([word for word in x.split() if word not in (STRING.stop)]))

    censo_df['nombre'] = censo_df['nombre'].apply(unidecode.unidecode)
    censo_df['nombre'] = censo_df['nombre'].str.replace('\d+', '')
    censo_df['nombre'] = censo_df['nombre'].str.lstrip()
    censo_df['nombre'] = censo_df['nombre'].str.rstrip()
    censo_df = censo_df[censo_df['nombre'] != '']
    censo_df = censo_df.dropna(subset=['nombre'], axis=0)

    censo_df.to_csv(STRING.PATH_source + 'censo_processed.csv', sep=';', index=False, encoding='utf-8')


if __name__ == '__main__':
    censo_clean(STRING.PATH_censo)
