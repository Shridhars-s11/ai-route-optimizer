# got some error with functions because encoding gives many columns and while predicting we are giving only some of the columns
# import joblib
# import pandas as pd

# def load_model(model_path='models/eta_model.pkl'):
#     return joblib.load(model_path)

# def predict_stop_eta(model,feature_row):
#     df = pd.DataFrame([feature_row])

#     df = pd.get_dummies(df)

#     predictions = model.predict(df)[0]

#     return round(predictions,2)

import joblib
import pandas as pd


def load_model():
    model = joblib.load("models/eta_model.pkl")
    feature_columns = joblib.load("models/feature_columns.pkl")
    return model, feature_columns


def predict_stop_eta(model, feature_columns, feature_row):

    df = pd.DataFrame([feature_row])

    df = pd.get_dummies(df)

    # align with training features
    df = df.reindex(columns=feature_columns, fill_value=0)

    prediction = model.predict(df)[0]

    return round(prediction, 2)