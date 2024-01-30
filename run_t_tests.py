import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import ttest_ind
from parameters import *

def preform_t_test(df1, df2, column):
    data1 = df1[column]
    data2 = df2[column]
    
    t_statistic, p_value = ttest_ind(data1, data2)
    return p_value


def food_comp():
    df0_5 = pd.read_csv("data/foodperstep=0.5.csv", index_col=False, header=None)
    df1_5 = pd.read_csv("data/foodperstep=1.5.csv", index_col=False, header=None)
    df3 = pd.read_csv("data/foodperstep=3.csv", index_col=False, header=None)
    df6 = pd.read_csv("data/foodperstep=6.csv", index_col=False, header=None)

    dfs = [df0_5, df1_5, df3, df6]
    dataset = [[preform_t_test(dfs[j], dfs[j+1], i) for i in range(19)] for j in range(3)]
    
    plt.plot(dataset[0], label = "comparison foodstep of 0.5 and 1.5")
    plt.plot(dataset[1], label = "comparison foodstep of 1.5 and 3")
    plt.plot(dataset[2], label = "comparison foodstep of 3 and 6")

    plt.xticks(np.arange(19))
    plt.title("T-test for different amount of neighbors among 2 indepentent groups")
    plt.xlabel("Number of neighbors")
    plt.ylabel("p-value")

    plt.axhline(y=0.05, color='r', linestyle='--', label=r'$\alpha = 0.05$')

    plt.legend()
    plt.show()

    dataset = [[preform_t_test(dfs[j], dfs[j+1], i) for i in [6]] for j in range(3)]
    print(dataset)
    
def vision():
    df2 = pd.read_csv("data/fishvision=2.csv", index_col=False, header=None)
    df4 = pd.read_csv("data/fishvision=4.csv", index_col=False, header=None)
    df6 = pd.read_csv("data/fishvision=6.csv", index_col=False, header=None)

    dfs = [df2, df4, df6]
    dataset = [[preform_t_test(dfs[j], dfs[j+1], i) for i in range(19)] for j in range(2)]

    plt.xticks(np.arange(19))

    plt.title("T-test for different amount of neighbors among 2 indepentent groups")
    plt.plot(dataset[0], label = "comparison fish vision of 2 and 4")
    plt.plot(dataset[1], label = "comparison fish vision of 4 and 6")

    plt.xlabel("Number of neighbors")
    plt.ylabel("p-value")

    plt.axhline(y=0.05, color='r', linestyle='--', label=r'$\alpha = 0.05$')

    plt.legend()
    plt.show()

    dataset = [[preform_t_test(dfs[j], dfs[j+1], i) for i in [6]] for j in range(2)]
    print(dataset)

vision()
food_comp()