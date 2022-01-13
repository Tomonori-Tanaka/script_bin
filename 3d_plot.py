import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

# CSVからデータを読み込む
data = pd.read_csv('./bccFe/Tc_a5.41_z.csv',skiprows=1, header=0, index_col=0)

print(data)
# 3Dグラフの初期化
fig = plt.figure()
ax = fig.gca(projection='3d')

# データの準備
Xgrid = data.columns.values.astype(np.float32)
Ygrid = data.index.values.astype(np.float32)
X, Y = np.meshgrid(Xgrid, Ygrid)
Z = data.values

# プロット
surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm)
ax.set_zlim(0, 2200)
fig.colorbar(surf, shrink=0.5, aspect=5)
# 必要な場合はここでその他の設定をします。
ax.scatter(X, Y, Z, c="black")

# 表示
plt.show()
