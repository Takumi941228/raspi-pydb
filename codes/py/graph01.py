#coding: utf-8

#グラフに関連するモジュール
import matplotlib.pyplot as plt

#配列を取り扱うモジュール
import numpy as np

#配列にプロットするデータを与える
y = np.array([50,60,100,80,75])
x = np.array(["H","E","L1","L2","O"])

#グラフにデータを与える
plt.plot(x,y)

#グラフを表示する
plt.show()