import pandas as pd
import statsmodels.api as sm

def run_ols_regression(df, y_var="tip"):
    X = df[["total_bill", "size"]]
    X = sm.add_constant(X)
    y = df[y_var]
    model = sm.OLS(y, X).fit()
    return model

