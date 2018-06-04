import googlemaps
import googlemaps.exceptions as gmexc
import STRING
import pandas as pd

gmaps = googlemaps.Client(key='AIzaSyDM_aED9kv2PDiVfZrbcIqAznOBaOSkqSo')
address = pd.read_csv(STRING.PATH_source + 'final_file.csv', sep=';', encoding='latin1')
address = address[['hogar_codigo_unico','hogar_nombre_via', 'hogar_numero_via', 'hogar_cp']]
address['direccion_completa'] = address['hogar_nombre_via'].map(str) + ' '+address['hogar_numero_via'].map(str)+', '+address['hogar_cp'].map(str) + ', Spain'
address['GPS'] = pd.Series('', index=address.index)
print(address)

try:
    auxiliar_file = pd.read_csv(STRING.PATH_source + 'address_gps.csv', sep=';', encoding='latin1')

except FileNotFoundError:
    auxiliar_file = pd.DataFrame(columns=['hogar_codigo_unico', 'direccion_completa', 'GPS']
                                 )

check_aux = auxiliar_file[['direccion_completa']]
check_aux['CONTROL'] = pd.Series(1, index=check_aux.index)
check_aux['direccion_completa'] = check_aux['direccion_completa'].map(str)
address['direccion_completa'] = address['direccion_completa'].map(str)
address = pd.merge(address, check_aux, how='left', on='direccion_completa')
address['CONTROL'] = address['CONTROL'].fillna(0)
address = address[address['CONTROL'] != 1]
del address['CONTROL']
address = address.reset_index(drop=True)
list_values = []

try:
    for index, row in address.iterrows():
        address_i = row['direccion_completa']
        row['GPS'] = gmaps.geocode(str(address_i))
        list_values.append([row['hogar_codigo_unico'], address_i, row['GPS']])

except gmexc.Timeout:
    pass
df = pd.DataFrame(list_values, columns=['hogar_codigo_unico', 'direccion_completa', 'GPS'])
auxiliar_file = pd.concat([auxiliar_file, df], axis=0)
auxiliar_file.to_csv(STRING.PATH_source + 'address_gps.csv', sep=';', encoding='utf-8', index=False)
