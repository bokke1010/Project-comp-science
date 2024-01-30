import main
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import ttest_ind
from parameters import *

def food_comp():
    df0_5 = pd.read_csv("data/foodperstep=0.5.csv", index_col=False, header=None)
    df1_5 = pd.read_csv("data/foodperstep=1.5.csv", index_col=False, header=None)
    df3 = pd.read_csv("data/foodperstep=3.csv", index_col=False, header=None)
    df6 = pd.read_csv("data/foodperstep=6.csv", index_col=False, header=None)

    alpha = 0.05


    def preform_t_test(df1, df2, column):
        data1 = df1[column]
        data2 = df2[column]
        
        t_statistic, p_value = ttest_ind(data1, data2)
        return p_value

    dfs = [df0_5, df1_5, df3, df6]
    dataset = [[preform_t_test(dfs[j], dfs[j+1], i) for i in range(19)] for j in range(3)]
    plt.plot(dataset[0])
    plt.plot(dataset[1])
    plt.plot(dataset[2])
    plt.show()

    dataset = [[preform_t_test(dfs[j], dfs[j+1], i) for i in [6]] for j in range(3)]
    print(dataset)

def vision():
    df2 = pd.read_csv("data/fishvision=2.csv", index_col=False, header=None)
    df4 = pd.read_csv("data/fishvision=4.csv", index_col=False, header=None)
    df6 = pd.read_csv("data/fishvision=6.csv", index_col=False, header=None)

    alpha = 0.05


    def preform_t_test(df1, df2, column):
        data1 = df1[column]
        data2 = df2[column]
        
        t_statistic, p_value = ttest_ind(data1, data2)
        return p_value

    dfs = [df2, df4, df6]
    dataset = [[preform_t_test(dfs[j], dfs[j+1], i) for i in range(19)] for j in range(2)]
    plt.plot(dataset[0])
    plt.plot(dataset[1])
    plt.show()

    dataset = [[preform_t_test(dfs[j], dfs[j+1], i) for i in [6]] for j in range(2)]
    print(dataset)

vision()
food_comp()