import os
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
import sqlite3
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.dates as mdates
from datetime import date

def get_hist_and_pred_data(username, startdate, enddate):
    """
    Melatih model OLS dan mengembalikan data historis serta data prediksi
    dalam bentuk DataFrame. Tidak menampilkan grafik.
    """
    
    # -----------------------------------------
    # Config / file names
    # -----------------------------------------
    DB_FILE = "transactions.db"
    INDEX_MAP_FILE = "index_map.json"
    
    # Konversi input tanggal ke format yang benar
    startdate = pd.to_datetime(startdate)
    enddate = pd.to_datetime(enddate)

    # -----------------------------------------
    # 1) Baca data transaksi dari DB
    # -----------------------------------------
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT username, type, amount, date FROM transactions", conn)
    conn.close()

    # Filter & Agregasi
    df = df[(df["username"] == username) & (df["type"].str.lower() == "expense")]
    df["date"] = pd.to_datetime(df["date"])
    df = df.groupby("date", as_index=False)["amount"].sum().sort_values("date")
    df["amount"] = df["amount"].abs()

    if df.empty or len(df) < 2:
        print("Tidak cukup data historis untuk prediksi.")
        return pd.DataFrame(), pd.DataFrame()

    # -----------------------------------------
    # 2) Persiapan Index Mapping yang Persist
    # -----------------------------------------
    if os.path.exists(INDEX_MAP_FILE):
        with open(INDEX_MAP_FILE, "r") as f:
            idx_store = json.load(f)
        date_to_index = {pd.to_datetime(k): v for k, v in idx_store.get("date_to_index", {}).items()}
        last_index = int(idx_store.get("last_index", -1))
    else:
        date_to_index = {}
        last_index = -1

    dates_in_db_min = df["date"].min()
    existing_map_min = min(date_to_index.keys()) if date_to_index else None
    
    global_min = dates_in_db_min if dates_in_db_min is not None else existing_map_min
    if global_min is None:
        global_min = startdate
    else:
        global_min = min(global_min, startdate)

    global_max = max(df["date"].max(), enddate)
    global_dates = pd.date_range(start=global_min, end=global_max, freq="D")

    for d in global_dates:
        if d not in date_to_index:
            last_index += 1
            date_to_index[d] = last_index

    to_save = {
        "last_index": last_index,
        "date_to_index": {d.strftime("%Y-%m-%d"): idx for d, idx in date_to_index.items()}
    }
    with open(INDEX_MAP_FILE, "w") as f:
        json.dump(to_save, f)

    # -----------------------------------------
    # 3) Siapkan data historis untuk model
    # -----------------------------------------
    hist_df = df.copy().sort_values("date").reset_index(drop=True)
    hist_df["t_index"] = hist_df["date"].map(lambda d: date_to_index[pd.to_datetime(d)])

    # -----------------------------------------
    # 4) Fitur regresi
    # -----------------------------------------
    def make_features_from_indices(t_indices):
        features = []
        for t in t_indices:
            features.append([1, t, np.sin(2 * np.pi * t / 7), np.cos(2 * np.pi * t / 7)])
        return np.array(features)

    X_features_all = make_features_from_indices(hist_df["t_index"].values)
    y_all = hist_df["amount"].values
    
    # Latih model pada SELURUH data historis
    model = sm.OLS(y_all, X_features_all)
    results = model.fit()

    # -----------------------------------------
    # 5) Aturan rekomendasi panjang prediksi
    # -----------------------------------------
    n_learn_days = len(hist_df)
    if n_learn_days < 14: max_pred = 0
    elif n_learn_days < 21: max_pred = 3
    elif n_learn_days < 35: max_pred = 7
    elif n_learn_days < 49: max_pred = 14
    elif n_learn_days < 63: max_pred = 21
    else: max_pred = 30

    print(f"\nJumlah hari yang dipelajari: {n_learn_days}. Max prediksi direkomendasikan: {max_pred} hari.")

    # -----------------------------------------
    # 6) Siapkan daftar tanggal prediksi
    # -----------------------------------------
    # Prediksi selalu dimulai sehari setelah data historis terakhir
    last_hist_date = hist_df["date"].max()
    future_startdate = last_hist_date + pd.Timedelta(days=1)
    
    requested_pred_dates = pd.date_range(start=future_startdate, end=enddate, freq="D")
    
    n_requested = len(requested_pred_dates)
    n_pred = min(n_requested, max_pred, 30)
    
    pred_df = pd.DataFrame(columns=["date", "predicted_expense"])
    
    if n_pred > 0:
        pred_dates = requested_pred_dates[:n_pred]
        
        future_indices = [date_to_index[pd.to_datetime(d)] for d in pred_dates]
        future_features = make_features_from_indices(future_indices)
        
        y_future_pred = results.predict(future_features)
        
        pred_df = pd.DataFrame({
            "date": pred_dates,
            "predicted_expense": y_future_pred
        })

    # -----------------------------------------
    # 7) Filter dan Kembalikan data
    # -----------------------------------------
    hist_in_range = hist_df[(hist_df["date"] >= startdate) & (hist_df["date"] <= enddate)]
    pred_in_range = pred_df[(pred_df["date"] >= startdate) & (pred_df["date"] <= enddate)]
    
    return hist_in_range, pred_in_range