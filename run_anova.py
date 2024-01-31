import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import ttest_ind, f_oneway
from parameters import *


df0_5 = pd.read_csv("data/foodperstep=0.5.csv", index_col=False, header=None)
df1_5 = pd.read_csv("data/foodperstep=1.5.csv", index_col=False, header=None)
df3 = pd.read_csv("data/foodperstep=3.csv", index_col=False, header=None)
df6 = pd.read_csv("data/foodperstep=6.csv", index_col=False, header=None)



for i in range(19):
    data1 = df0_5[i]
    data2 = df1_5[i]
    data3 = df3[i]
    data4 = df6[i]
    f_statistic, p_value = f_oneway(data1, data2, data3, data4)
    print(p_value)

p_values = {i: f_oneway(df0_5[i], df1_5[i], df3[i], df6[i])[1] for i in range(19)}

fig, ax = plt.subplots()
ax.plot(np.arange(19), list(p_values.values()))
ax.axhline(y=0.05, color='r', linestyle='--', label='Significance Level (α=0.05)')

ax.set_xlabel('Index')
ax.set_ylabel('p-value')
ax.legend()
plt.xticks(np.arange(19))
plt.title('ANOVA p-values for foodperstep')
plt.savefig(f"ANOVA_food_per_step.svg",
        transparent=True, format="svg", bbox_inches="tight")
df2 = pd.read_csv("data/fishvision=2.csv", index_col=False, header=None)
df4 = pd.read_csv("data/fishvision=4.csv", index_col=False, header=None)
df6 = pd.read_csv("data/fishvision=6.csv", index_col=False, header=None)

p_values = {i: f_oneway(df2[i], df4[i], df6[i])[1] for i in range(19)}

fig, ax = plt.subplots()
ax.plot(np.arange(19), list(p_values.values()))
ax.axhline(y=0.05, color='r', linestyle='--', label='Significance Level (α=0.05)')

ax.set_xlabel('Index')
ax.set_ylabel('p-value')
ax.legend()
plt.xticks(np.arange(19))
plt.title('ANOVA p-values for fishvision')
plt.savefig(f"ANOVA_vision.svg",
        transparent=True, format="svg", bbox_inches="tight")
