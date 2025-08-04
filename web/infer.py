from typing import Optional, Tuple, List

import pandas as pd
from pandas import DataFrame, Series
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from fastapi import FastAPI
from pydantic import BaseModel
import mlflow
from mlflow.tracking import MlflowClient
import uvicorn

app = FastAPI()

class Record(BaseModel):
    RowID: int | None
    Division_Name: str | None
    Location_Name: str | None
    Sublocation_Name: str | None
    Village_Name: str | None
    Wealthgroup_Name: str | None
    PMT_Score: float | None
    Resident_Provider: float | None
    Polygamous: float | None
    Kids_Under_15_In_Settlement: float | None
    Children_Under_15_outside_settlement: float | None
    Spouses_on_settlement: float | None
    Spouses_Outside_HH: float | None
    IsBeneficiaryHH: bool | None
    recipient_of_wfp: int | None
    recipient_of_hsnp: int | None
    OPCT_received: int | None
    PWSDCT_received: int | None
    Relationship_MainProvider: str | None
    Gender: str | None
    Age: int | None
    School_meal_receive: int | None
    Work_last_7days: str | None
    Main_provider_occupation: str | None
    Toilet: str | None
    Drinking_water: str | None
    Donkeys_owned: int | None
    Camels_owned: int | None
    Zebu_cattle_owned: int | None
    Shoats_owned: int | None
    Nets_owned: int | None
    Hooks_owned: int | None
    Boats_rafts_owned: int | None

@app.get("/")
def test(id: Optional[int] = None):
    return {"message": "And we are live"}

@app.post("/predict")
def infer(data: List[Record]):
    data_json = [datum.dict() for datum in data]
    dt = pd.json_normalize(data_json)

    # dt = pd.read_csv("C:\\Users\\david.njuguna\\Desktop\\Davi Pers Projects\\DE\\ASAL-Households-Classification-for-Social-Protection\\data\\output-refined-ann.csv")

    t,df = preprocess(dt)

    X, y = df, t

    # get run - load model
    MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    model_name = "asal_xgb_model_20250804_3"
    model_v = 1

    model = mlflow.xgboost.load_model(
        model_uri = f"models:/{model_name}/{model_v}"
    )

    # reformat featurename
    # https://stackoverflow.com/questions/42338972/valueerror-feature-names-mismatch-in-xgboost-in-the-predict-function
    cols_when_model_builds = model.get_booster().feature_names
    X = X[cols_when_model_builds]

    # predict
    pred = model.predict(X)

    return {
        "pred": np.array(pred).tolist(),
        "target": np.array(y).tolist()
    }

def preprocess(df) -> Tuple[Series, DataFrame]:
    t, df = transform(df)
    df = normalization(df)
    df = one_hot(df)
    df = bool_convert(df)
    df = fill_missing_cols(df)

    return t, df

def fill_missing_cols(df: DataFrame) -> DataFrame:
    MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    artifact: dict = mlflow.artifacts.load_dict("mlflow-artifacts:/254847489140008771/658e9234604c4598a529382521e8f24f/artifacts/col_set.json")
    artifact_cols = artifact.keys()
    dfCols = df.columns

    for col in artifact_cols:
        if col not in dfCols:
            df[col] = 0

    return df

def transform(df) -> Tuple[Series, DataFrame]:
    # remap labels
    df['Wealthgroup_Name'] = df['Wealthgroup_Name'].replace(['Better Off', 'Middle', 'Poor', 'Very Poor'], [0,1,2,3])

    bool_cols = [
        "recipient_of_wfp",
        "OPCT_received",
        "PWSDCT_received",
        "School_meal_receive",
    ]
    
    df[bool_cols] = df[bool_cols].applymap(lambda x: x == 1)

    # resident provider has categorical values representes as numbers
    df["Resident_Provider"] = df["Resident_Provider"].astype(str)

    # drop target label and features with non-trivial missing data
    # convert skip to NaN
    fd2 = df.replace("SKIP", np.nan).replace("", np.nan)

    fd2.dropna(inplace=True)

    target = fd2["Wealthgroup_Name"]

    drop_cols = [
        "IsBeneficiaryHH",
        "RowID",
        "Sublocation_Name",
        "Village_Name",
        "Division_Name",
        "Location_Name",
        "Wealthgroup_Name",
        "PMT_Score",
    ]

    fd2 = fd2.drop(drop_cols, axis=1,)

    return target, fd2

def normalization(df) -> DataFrame:
    scaler = MinMaxScaler()  # default=(0, 1)

    numerical = [
        "Age",
        "Polygamous",
        "Children_Under_15_outside_settlement",
        "Kids_Under_15_In_Settlement",
        "Spouses_on_settlement",
        "Spouses_Outside_HH",
        "Donkeys_owned",
        "Camels_owned",
        "Zebu_cattle_owned",
        "Shoats_owned",
        "Nets_owned",
        "Hooks_owned",
        "Boats_rafts_owned",
        # 'PMT_Score',
    ]

    features_minmax_transform = pd.DataFrame(data=df)
    # display(features_log_minmax_transform[:1])
    features_minmax_transform[numerical] = scaler.fit_transform(df[numerical])

    return features_minmax_transform

def one_hot(df) -> DataFrame:
    return pd.get_dummies(df)


def bool_convert(df) -> DataFrame:
    bool_cols = df.select_dtypes(include=['bool']).columns
    df[bool_cols] = df[bool_cols].replace([False, True], [0, 1])

    return df

if __name__ == "__main__":
    uvicorn.run("infer:app", host="0.0.0.0", port=8000)
