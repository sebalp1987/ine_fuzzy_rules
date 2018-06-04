import STRING
import preprocess.preprocess_hogar as prep
import pandas as pd
import utils.map_hogar as mapping
import time
import preprocess.join_ine_zurich as ine_zurich
import utils.heatmap as hmap
from model import kmeans
from model import stepwise
from sklearn.preprocessing import scale
'''
# Load File
hogar = pd.read_csv(STRING.PATH_source + 'zurich.csv', sep=';', encoding='utf-8')

# Clean data hogar
hogar = prep.hogar_clean(hogar)

# Map values
t_0 = time.time()
hogar_cleaned, hogar_cp = mapping.hogar_mapping(hogar, range_acceptance=75, separate_odd=True, separate_number=True,
                                                cp=False)
t_1 = time.time()
print("This took %.2f seconds" % (t_1 - t_0))

# Remain go through CP
t_0 = time.time()
hogar_cleaned, _ = mapping.hogar_mapping(hogar_cp, range_acceptance=75, separate_odd=False, separate_number=False,
                                         cp=True)
t_1 = time.time()
print("This took %.2f seconds" % (t_1 - t_0))

hogar_cp = pd.read_csv(STRING.PATH_source + 'final_file_cp.csv', sep=';', encoding='utf-8')
hogar_cp = hogar_cp[hogar_cp['total_code'] != 'N/A']

hogar = pd.read_csv(STRING.PATH_source + 'final_file.csv', sep=';', encoding='utf-8')
hogar = hogar[hogar['total_code'] != 'N/A']

# HOGAR FILE ZURICH
hogar = pd.concat([hogar, hogar_cp], axis=0)

# INE FILE
ine = pd.read_csv(STRING.PATH_source + 'test.csv', sep=';', encoding='latin1')

# JOIN
merge = ine_zurich.join_files(hogar, ine)

merge = pd.read_csv(STRING.PATH_source + 'final_file_merge.csv', encoding='latin1', sep=';')


# CORRELATION
#hmap.correlation_get_all(merge.drop(['total_code', 'hogar_codigo_unico'], axis=1), get_all=True, output_file=True, show_plot=True)
# hmap.correlation_get_all(merge.drop(['total_code', 'hogar_codigo_unico'], axis=1), False, get_specific='hogar_prima_poliza', show_plot=True)


# MODELS
merge = merge.dropna()

# COLINEALIDAD
from statsmodels.stats.outliers_influence import variance_inflation_factor

def OLS(Y, x, vif=True):
    if vif:
        vif = pd.DataFrame()
        vif['vif'] = [variance_inflation_factor(x.values, i) for i in range(x.shape[1])]
        vif['features'] = x.columns
        print(vif)

y = merge[['hogar_prima_poliza']]
x = merge.drop(['total_code', 'hogar_codigo_unico'],axis=1).copy()
del x['hogar_prima_poliza']
remove_vif = ['No UE', 'Personas analfabetas', '<30m2', 'ranking_edad_16_seccion', 'ranking_income_size_property', 'income_by_size_property',
              'edad_16_64', 'español', 'soltero', 'estudios de segundo grado', 'Viviendas Principales', 'ranking_extranjeros_riesgo', 'ranking_analfabetismo',
              'Latino', 'Vivienda_pc', 'Población total', 'sexo_porcent', 'casado', 'Personas sin estudios', 'ranking_densidad', 'vv_compra_parcial'
            ]
for i in remove_vif:
    del x[i]


x = x[['estudios de primer grado', 'vv_donacion', 'edad_16', '30-45 m2', 'Asia', 'divorciado','Total Viviendas', '91-105 m2', 'analfabetismo','vv_cedida', 'América del Norte','46-60 m2'
]]
# stepwise.setpwise_reg(x_df=x, y_df=y, names=x.columns.values.tolist())
'''
X = pd.read_csv(STRING.PATH_source + 'ine_data.csv', delimiter=';', encoding='latin1')
for i in ['cpro', 'dist']:
    X[i] = X[i].map(str)
    X[i] = X[i].str.zfill(2)
for i in ['cmun', 'secc']:
    X[i] = X[i].map(str)
    X[i] = X[i].str.zfill(3)

X['total_code'] = X['cpro'] + '-' + X['cmun'] + '-' + X['dist'] + '-' + X['secc']
X['total_code'] = X['total_code'].map(str)
X = X[['total_code', 'analfabetismo', 'No UE', 'edad_16',  'vv_cedida', 'Vivienda_pc', 'Viviendas Principales']]
X = X.dropna(axis=0)
X = X.drop_duplicates(subset=['total_code'])
X_name = X.columns.values.tolist()

# X = scale(X)
# x_df = pd.DataFrame(X, columns=X_name)

for i in X.drop(['total_code'], axis=1).columns.values.tolist():
    X[i] = X[i]*100
    X[i] = X[i].round()
    X[i] = X[i].map(int)

X = X.reset_index(drop=True)

# HAY CLUSTER?
# kmeans.expl_hopkins(X.drop(['total_code'],axis=1), num_iters=20)

# VALIDACION INTERNA
# kmeans.cluster_internal_validation(X.drop(['total_code'],axis=1), n_clusters=10)

# NUMERO CLUSTERS CORRECTA
# kmeans.silhouette_coef(X.drop(['total_code'], axis=1).values, range_n_clusters=range(3, 4, 1))
kmeans.kmeans_plus_plus(X, k=4, n_init=42, max_iter=200, drop='total_code')
