import utils.algorithm_rules as algorithm_rules
import pandas as pd
import STRING
from fuzzywuzzy import process
import tqdm
default_scorer = algorithm_rules.WRatio


def hogar_mapping(hogar_df: pd.DataFrame,  range_acceptance=90, scorer=default_scorer, separate_odd=True,
                  separate_number=True, cp=False):
    """
    :param hogar_df: Dataframe hogar
    :param range_acceptance: Thresold to accept an address to be replaced
    :param scorer: Scorer used to calculate the similarity between two strings
    :param separate_odd: If you want to separate between odd-even numbers
    :param separate_number: If you want to reduce CP to house numbers
    :param cp: It is a file control
    """

    list_coincidences = []

    try:
        censo = pd.read_csv(STRING.PATH_censo_processed, sep=';', encoding='utf-8')

    except FileNotFoundError:
        import preprocess.preprocess_censo
        preprocess.preprocess_censo.censo_clean(STRING.PATH_censo)
        censo = pd.read_csv(STRING.PATH_censo_processed, sep=';', encoding='utf-8')

    censo = censo[['impar', 'inferior', 'superior', 'cp', 'nombre', 'total_code']]
    censo['cp'] = censo['cp'].map(int)
    censo['impar'] = censo['impar'].map(int)
    censo['inferior'] = censo['inferior'].map(int)
    censo['superior'] = censo['superior'].map(int)

    censo_par = censo[censo['impar'] == 2]
    censo_impar = censo[censo['impar'] == 1]

    for index, row in tqdm.tqdm(hogar_df.iterrows(), total=hogar_df.shape[0]):

        total_code = ''
        hogar_codigo_unico = row['cod_global_unico']
        hogar_poliza = float(row['total_poliza_prima_recibo'])
        hogar_nombre_via = row['hogar_nombre_via']
        hogar_numero_via = int(row['hogar_numero_via'])
        hogar_cp = int(row['hogar_cp'])
        hogar_impar = int(row['number_odd'])

        if separate_odd == False:
            censo_i = censo
        else:
            # Filtering by cp and number
            if hogar_impar == 1:
                censo_i = censo_impar

            else:
                censo_i = censo_par

        censo_i = censo_i[censo_i['cp'] == hogar_cp]

        if separate_number == True:
            censo_i = censo_i[(censo_i['inferior'] <= hogar_numero_via) & (hogar_numero_via <= censo_i['superior'])]

        # We convert to a dict
        censo_list_names = censo_i['nombre'].values.tolist()
        censo_i = censo_i.set_index('nombre', drop=True)['total_code'].to_dict()

        try:
            coincidence_name, score = process.extractOne(hogar_nombre_via, censo_list_names, scorer=scorer)
        except TypeError:
            coincidence_name = 'N/A'
            score = 0
            total_code = 'N/A'

        if separate_odd == False:
            if score < range_acceptance:
                coincidence_name = 'N/A'
                total_code = 'N/A'
            else:
                total_code = censo_i[coincidence_name]
        else:
            # If score is not expected or was an empty list we check in the other par-impar streets
            if score < range_acceptance or total_code == 'N/A':
                if hogar_impar == 1:
                    censo_i = censo_par

                else:
                    censo_i = censo_impar

                censo_i = censo_i[censo_i['cp'] == hogar_cp]
                censo_i = censo_i[(censo_i['inferior'] <= hogar_numero_via) & (hogar_numero_via <= censo_i['superior'])]

                censo_list_names = censo_i['nombre'].values.tolist()
                censo_i = censo_i.set_index('nombre', drop=True)['total_code'].to_dict()

                try:
                    coincidence_name, score = process.extractOne(hogar_nombre_via, censo_list_names, scorer=scorer)
                except TypeError:
                    coincidence_name = 'N/A'
                    score = 0
                    total_code = 'N/A'

                if score < range_acceptance:
                    coincidence_name = 'N/A'
                    total_code = 'N/A'

                else:
                    total_code = censo_i[coincidence_name]

            else:
                total_code = censo_i[coincidence_name]

        list_coincidences.append([hogar_codigo_unico, hogar_poliza, hogar_nombre_via, hogar_numero_via, hogar_cp, coincidence_name, score,
                                  total_code])

    cleaned_df = pd.DataFrame(list_coincidences, columns=['hogar_codigo_unico', 'hogar_prima_poliza', 'hogar_nombre_via', 'hogar_numero_via',
                                                          'hogar_cp', 'coincidence_name', 'score', 'total_code'])

    if cp == True:
        cleaned_df.to_csv(STRING.PATH_by_cp, sep=';', index=False, encoding='utf-8')
    else:
        cleaned_df.to_csv(STRING.PATH_final_output, sep=';', index=False, encoding='utf-8')

    # We generate an extra file for remaining cases
    total_processed = len(hogar_df.index)
    cleaned_df = cleaned_df[cleaned_df['coincidence_name'] == 'N/A']
    not_processed = len(cleaned_df.index)
    print("Processed : ", total_processed)
    print("Not processed : ", not_processed)
    print("Percentage mapped %.2f " % (1 - (not_processed / total_processed)))
    hogar_df = hogar_df.loc[cleaned_df.index]
    # hogar_df.to_csv(STRING.PATH_by_cp, sep=';', index=False, encoding='utf-8')
    return cleaned_df, hogar_df

if __name__ == '__main__':
    import preprocess.preprocess_hogar
    hogar = pd.read_csv(STRING.PATH_source + 'hogares.csv', sep=';', encoding='utf-8')
    hogar = preprocess.preprocess_hogar.hogar_clean(hogar)
    hogar_mapping(hogar)
