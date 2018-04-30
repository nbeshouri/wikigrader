"""
This module contains utilities used by other modules or notebooks.

Todo:
    * Rename to "scoring"?
    * Use local imports so doesn't force keras to be imported if not
        needed.

"""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error as mae
from sklearn.metrics import r2_score
from sklearn.model_selection import cross_val_score
from keras import backend as K


def rmse(y_true, y_pred):
    """Return root-mean-square error."""
    return np.sqrt((mean_squared_error(y_true, y_pred)))


def metrics(y_true, y_pred):
    """Return a `DataFrame` of regression metrics."""
    labels = ['R^2', 'RMSE', 'MAE'] 
    vals = [r2_score(y_true, y_pred), rmse(y_true, y_pred), 
            mae(y_true, y_pred)]    
    return pd.DataFrame(vals, index=labels, columns=['Score'])


def cross_val_metrics(X, y, model, cv=3):
    """Return a `DataFrame` of regression metrics."""
    scorers = ['r2', 'neg_mean_squared_error', 'neg_mean_absolute_error']
    scores = [np.mean(cross_val_score(model, X, y, scoring=scorer, cv=3)) for scorer in scorers]
    labels = ['R^2', 'RMSE', 'MAE'] 
    scores[1], scores[2] = -scores[1], -scores[2]
    df = pd.DataFrame(scores, index=labels)
    df.columns = [f'Scores ({cv} folds)'] if cv else [f'Scores']
    return df


def r2(y_true, y_pred):
    """Create tensor graph for computing R^2."""
    ss_res = K.sum(K.square(y_true - y_pred)) 
    ss_tot = K.sum(K.square(y_true - K.mean(y_true))) 
    return 1 - ss_res / (ss_tot + K.epsilon())
