#ini modul buat bikin prediksi dalam rentang maksimal 30 hari ke depan kalo pengguna baru masukin sedikit data
#basicnya adalah numerical method, yaotu Ordinary Leas Square (OLS)
#Rencananya, bakal pake polinomial regression yang digabung sama fourier regression

import numpy as np
import pandas as pd
import statsmodels.api as sm
import sklearn

startdate="2024-01-01" #ganti ke pembaca di kalendar widget (..w..)
enddate="2024-03-31" #ganti ke pembaca kalendar widget (..W..)
dates = pd.date_range(start=startdate, end=enddate, freq="D")

#kita pake 2 variabel, yaitu t dan t_learn. t akan jadi index buat ols
# nilainya akan reset setiap ganti bulan atau ganti range
# tapi t_learn akan jadi index yang tetap walau range berubah, fungsinya cuma buat bikin learningnya makin smooth

X = np.arange(len(dates))
#dummy y
np.random.seed(42)  # biar hasil random konsisten
n = len(dates)

# tren linear sederhana
trend = 200 * np.arange(n)

# pola musiman bulanan (gelombang sinus 30-harian)
seasonal = 5000 * np.sin(2 * np.pi * np.arange(n) / 30)

# random noise
noise = np.random.normal(0, 2000, n)

# gabungan jadi dummy pengeluaran (selalu positif)
y = 20000 + trend + seasonal + noise
y = np.maximum(y, 1000)  # jaga jangan sampai negatif

t_learn=0


#lanjut di collab dulu, nanti benerin download pyhon dulu

#Masuk fitur musiman
X_features = []
for t in X.flatten():
  X_features.append([
      1,
      t,
      np.sin(2*np.pi*t/30),
      np.cos(2*np.pi*t/30)
  ])

X_features = np.array(X_features)

#latih model OLS

model = sm.OLS(y, X_features)
results = model.fit()

print(results.summary())

future_days = np.arange(max(X)+1, max(X)+31)
future_features = []

for t in future_days:
  future_features.append([
      1,
      t,
      np.sin(2*np.pi*t/30),
      np.cos(2*np.pi*t/30)
  ])
future_features = np.array(future_features)

y_pred = results.predict(future_features)
print(y_pred)

n=len(X)

#titik pemisah train/test
split = int(n*0.8)

X_train, X_test = X_features[:split], X_features[split:]
y_train, y_test = y[:split], y[split:]

#buat ngelatih model pake data training
model = sm.OLS(y_train, X_train)
results = model.fit()

#prediksi data test
y_test_pred = results.predict(X_test)

#hitung error
from sklearn.metrics import mean_squared_error, mean_absolute_error

mse=mean_squared_error(y_test, y_test_pred)
mae=mean_absolute_error(y_test, y_test_pred)

print(f"MSE: {mse:.2f}")
print(f"MAE: {mae:.2f}")

#ini buat visualisasi hasil

import matplotlib.pyplot as plt

plt.figure(figsize=(12,5))
plt.plot(dates[:split], y_train, label="Train (Actual)")
plt.plot(dates[:split], results.predict(X_train), "--", label="Train (Predicted)")
plt.plot(dates[split:], y_test, "o", label="Test (Actual)")
plt.plot(dates[split:], y_test_pred, "x--", label="Test (Predicted)")
plt.legend()
plt.show()

#BIKIN PREDIKSI 30 HARI KE DEPAN===
future_dates = pd.date_range(start=dates[-1] + pd.Timedelta(days=1), periods=30, freq="D")

#bagian ini untuk prediksi 30 hari ke depan
future_days = np.arange(max(X)+1, max(X)+31)
future_features = []

for t in future_days:
  future_features.append([
      1,
      t,
      np.sin(2*np.pi*t/30),
      np.cos(2*np.pi*t/30)
  ])

future_features = np.array(future_features)
y_future_pred = results.predict(future_features)


plt.figure(figsize=(12,5))
plt.plot(dates, y, label="Data Actual", marker="o")
plt.plot(future_dates, y_future_pred, "--", label="Prediksi 30 Hari ke Depan", marker="x")
plt.legend()
plt.title("Prediksi Pengeluaran 30 Hari ke Depan (OLS + Fourier)")
plt.show()

pred_df = pd.DataFrame({
    "date": future_dates,
    "predicted_expense": y_future_pred
})
pred_df.to_csv("prediksi_30hari.csv", index=False)


# Prediksi untuk semua data (train+test)
y_all_pred = results.predict(X_features)

total_actual_all = np.sum(y)
total_pred_all = np.sum(y_all_pred)

print("\n=== Perbandingan Total (Keseluruhan Data) ===")
print(f"Total Aktual    : {total_actual_all:,.2f}")
print(f"Total Prediksi  : {total_pred_all:,.2f}")
print(f"Selisih         : {total_pred_all - total_actual_all:,.2f}")
print(f"Persentase Error: {100 * (total_pred_all - total_actual_all) / total_actual_all:.2f}%")

