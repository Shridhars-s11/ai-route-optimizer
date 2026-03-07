import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import joblib

def train_model(data_path):
    df = pd.read_csv(data_path)
    df = df.dropna()

    y = df['Time_taken']
    X = df.drop('Time_taken',axis=1)

    X = pd.get_dummies(X)

    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=42)

    model = LinearRegression()

    model.fit(X_train,y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test,predictions)

    print(f"Model mean absolute error is : {round(mae,3)} minutes")

    joblib.dump(model,"models/eta_model.pkl")

    return model