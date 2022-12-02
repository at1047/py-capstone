
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import colorsys

def parse(filename):
    df_raw = pd.read_csv(filename, skiprows=8)
    df = df_raw.copy()
    df = df.rename(columns={'% x': 'x', 'T (K)': 't'})

    for i in range(10):
        z_min = i
        z_max = i+1
        df_xy = df.copy()
        df_xy = df.loc[(df['z'] > z_min) & (df['z'] < z_max)]
        df_xy = df_xy[['x', 'y', 't']]

    df_xy = df.copy()
    df_xy = df_xy.loc[df['z'] == 0]
    df_xy = df_xy.loc[(df['x'] < 150) & (df['x'] >= 0)]
    df_xy = df_xy.loc[(df['y'] < 150) & (df['y'] >= 0)]
    df_xy = df_xy[['x', 'y', 't']]
    num_x = 5
    num_y = 10
    x_interval = np.floor((df_xy['x'].max() - df_xy['x'].min())/(num_x-1))
    y_interval = np.floor((df_xy['y'].max() - df_xy['y'].min())/(num_y-1))
    df_xy['x_round'] = df_xy[['x']]//x_interval
    df_xy['y_round'] = df_xy[['y']]//y_interval
    df_xy = df_xy.groupby(['x_round', 'y_round']).max().reset_index()
    df_xy = df_xy[['x_round', 'y_round', 't']]
    df_xy = df_xy.rename(columns={'x_round': 'x', 'y_round': 'y'})
    t_min = df_xy['t'].min()
    t_max = df_xy['t'].max()
    t_range = t_max - t_min
    df_xy['t_normalized'] = (df_xy['t']-t_min)/t_range
    # df_xy['r'] = (1-df_xy['t_normalized'])*255
    # df_xy['g'] = abs(0.5-df_xy['t_normalized'])*255*2
    # df_xy['b'] = df_xy['t_normalized']*255
    df_xy['rgb'] = df_xy.apply(lambda x: colorsys.hsv_to_rgb((x['t_normalized']/360*240), 1, 1), axis=1)
    c = pd.DataFrame(df_xy['rgb'].tolist())
    plt.scatter(df_xy['x'], df_xy['y'], c=c.to_numpy())
    plt.savefig("fig.png")