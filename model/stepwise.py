import pandas as pd
import numpy
from sklearn.metrics import r2_score
import statsmodels.api as sm
import matplotlib.pyplot as plot
from sklearn import linear_model
from sklearn.preprocessing import scale

_author_ = 'Sebastian Palacio'

def setpwise_reg(x_df: pd.DataFrame, y_df:pd.DataFrame, names: list):
    #x_name = x_df.columns.values.tolist()
    y_name = y_df.columns.values.tolist()
    #x_df = scale(x_df)
    #x_df = pd.DataFrame(x_df, columns=x_name)
    y_df = scale(y_df)
    y_df = pd.DataFrame(y_df, columns=y_name)
    x_df = x_df.reset_index(drop=True)

    xList = x_df.values.tolist()
    target = y_df.values.tolist()

    def xattrSelect(x,
                    idxSet):
        xOut = []
        for row in x:
            xOut.append([row[i] for i in idxSet])
        return (xOut)

    # dividimos los atributos y el target en training y test
    indices = range(len(xList))
    xListTest = [xList[i] for i in indices if i % 3 == 0]
    xListTrain = [xList[i] for i in indices if i % 3 != 0]
    targetTest = [target[i] for i in indices if i % 3 == 0]
    targetTrain = [target[i] for i in indices if i % 3 != 0]

    # armamos columnas de atributos para ir probando que columnas quedan mejor
    attributeList = []
    index = range(len(xList[1]))
    indexSet = set(
        index)  # crea una variable ordenada en funciÃ³n de los valores que tenga la variable de la cual se origina

    oosError = []
    aasError = []
    bbs = []
    sse = []
    for i in index:
        print(i)
        attSet = set(attributeList)  # marca las columnas que se van descartando

        attTrySet = indexSet - attSet  # marca las columnas que se van utilizando (el contrario al attSet)

        attTry = [ii for ii in attTrySet]  # paso attTrySet a una lista [0.0, 1.0...31]

        errorList = []
        absError = []
        betaList = []
        seList = []
        ####
        for iTry in attTry:
            attTemp = [] + attributeList  # comienza como una columna de [1...31], luego itera nuevamente con dos columnas [31,1..31], luego con tres [31,21,1...31] siempre iterando la ultima columna (esto lo hace usando las columnas que genera attSet)
            attTemp.append(iTry)

            ####
            xTrainTemp = xattrSelect(xListTrain, attTemp)
            xTestTemp = xattrSelect(xListTest, attTemp)
            ####
            xTrain = numpy.array(xTrainTemp)
            yTrain = numpy.array(targetTrain)
            xTest = numpy.array(xTestTemp)
            yTest = numpy.array(targetTest)

            fileQModel = linear_model.LinearRegression()
            fileQModel.fit(xTrain, yTrain)
            ols = sm.OLS(yTrain, xTrain)
            result = ols.fit()

            rmsError = numpy.linalg.norm((yTest - fileQModel.predict(xTest)), 2) * numpy.linalg.norm(
                (yTest - fileQModel.predict(xTest)), 2) / len(yTest)  # este va calculando todo el tiempo el RMS
            absVal = numpy.linalg.norm((yTest - fileQModel.predict(xTest)), 1) / len(yTest)
            betas = fileQModel.coef_
            se = result.HC0_se
            errorList.append(rmsError)  # arma una columna de los RMS
            absError.append(absVal)
            betaList.append(betas)
            seList.append(se)
            attTemp = []

        iBest = numpy.argmin(errorList)  # toma el mÃ­nimo RMS
        attributeList.append(attTry[iBest])  # toma la mejor combinaciÃ³n de columnas de donde saliÃ³ el mÃ­nimo RMS
        oosError.append(errorList[iBest])  # va armando una columna de mejores RMS
        aasError.append(absError[iBest])
        bbs.append(betaList[iBest])
        sse.append(seList[iBest])

    print('Out of Sample error versus attribute set Size ', oosError)
    print('Out of Sample absolute error versus attribute set Size ', aasError)
    print('\n Best attribute indices ', attributeList)
    print('betas', bbs)
    print('se', sse)
    numpy.savetxt("oosError.csv", oosError, delimiter=",")
    numpy.savetxt("attributeList.csv", attributeList, delimiter=",")

    namesList = [names[i] for i in attributeList]
    print('\n Best Attribute Names ', namesList)

    '''
    Esto arroja no solo el nombre de los atributos, sino su orden de calidad en tÃ©rminos de predicciÃ³n. !!!!!
    '''

    # PLOT ERROR VERSUS NUMBER OF ATTRIBUTES#######################################################################
    x = range(len(oosError))

    plot.plot(x, oosError,
              'k')  # plot(x,y,keyword arguments) if i put 'k' is black color lines colors=('b', 'g', 'r', 'c', 'm', 'y', 'k', 'w')
    plot.xlabel('Attributes')
    plot.ylabel('MSE')
    plot.title('Stepwise Regression')
    plot.show()

    # PLOT HISTOGRAM OF OUT SAMPLE ERRORS FOR BEST NUMBER OF ATTRIBUTES############################################

    indexBest = oosError.index(min(oosError))
    print('index Best (min oosError = ', indexBest)
    attributesBest = attributeList[1:(indexBest + 1)]

    xTrainTemp = xattrSelect(xListTrain, attributesBest)  # Arma una matrix X con los mejores atributos (con el conjunto de 2/3)
    xTestTemp = xattrSelect(xListTest, attributesBest)  # Arma una matrix X con los mejores atributos (con el conjunto de prueba de 1/3)
    xTrain = numpy.array(xTrainTemp)
    xTest = numpy.array(xTestTemp)
    fileQModel = linear_model.LinearRegression()
    fileQModel.fit(xTrain, yTrain)
    errorVector = yTest - fileQModel.predict(xTest)  # hace un vector en funciÃ³n del yTest y de la predicciÃ³n de Y hecha con el xTest (basado en el modelo lineal con xTrain e yTrain)
    plot.hist(errorVector)
    plot.xlabel('lÃ­mite del error (bin boundaries)')
    plot.ylabel('Count')
    plot.show()

    # Scatter Plot of actual versus predicted
    r2 = r2_score(yTest, fileQModel.predict(xTest))
    print('r2 Stepwise', r2)
    plot.scatter(fileQModel.predict(xTest), yTest, s=100,
                 alpha=0.1)  # s es el intercept, alpha la pendiente de una lÃ­nea de ejemplo
    plot.xlabel('Predicted Values')
    plot.ylabel('Real Values')
    plot.title('Stepwise Regression')
    plot.show()
    print(type(x))
    x_df = x_df[namesList]
    ols = sm.OLS(y_df, x_df)
    result = ols.fit()
    print(result.summary())
