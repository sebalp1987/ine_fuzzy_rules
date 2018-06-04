import pandas as pd
import STRING

def join_files(zurich, ine):
    for i in ['cpro','dist']:
        ine[i] = ine[i].map(str)
        ine[i] = ine[i].str.zfill(2)
    for i in ['cmun','secc']:
        ine[i] = ine[i].map(str)
        ine[i] = ine[i].str.zfill(3)

    ine['total_code'] = ine['cpro'] + '-' + ine['cmun'] + '-' +ine['dist'] + '-' + ine['secc']
    ine['total_code'] = ine['total_code'].map(str)
    print(ine['total_code'])
    zurich = zurich.dropna(subset=['total_code'])
    zurich['total_code'] = zurich['total_code'].map(str)
    df = pd.merge(zurich, ine, how='left', on='total_code')
    df = df.dropna(subset=['ranking_densidad'])
    del_var = ['hogar_nombre_via',
    'hogar_numero_via',
    'hogar_cp',
    'coincidence_name',
    'score',
    'cpro',
    'cmun',
    'dist',
    'secc']
    for i in del_var:
        del df[i]

    df.to_csv(STRING.PATH_source + 'final_file_merge.csv', sep=';', encoding='latin1', index=False)

    return df