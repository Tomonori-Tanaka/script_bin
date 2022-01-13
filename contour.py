import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# CSVからデータを読み込む
args = sys.argv[1]
data = pd.read_csv(args, skiprows=1, header=0, index_col=0)

print(data)

# データの準備
Xgrid = data.columns.values.astype(np.float32)
Ygrid = data.index.values.astype(np.float32)
X, Y = np.meshgrid(Xgrid, Ygrid)
Z = data.values


fig = plt.figure(figsize=(9, 7))
ax = fig.add_subplot(111)
# ax = fig.gca(projection='3d')
#ax.clabel(cntr, colors='black')
#ax.contourf(X, Y, Z, cmap="Spectral_r")
cntr = ax.contourf(X, Y, Z, 40, cmap="Spectral_r")
fig.colorbar(cntr, aspect=40, pad=0.08, orientation='vertical')
ax.scatter(X, Y, 2, c="black")
# プロット
# ax.scatter(X, Y, Z, c="black")
#plt.xticks([25, 25.2, 25.4, 25.6, 25.8, 26, 26.2, 26.4, 26.6, 26.8, 27])
# 表示
plt.show()
