
import numpy as np
import pandas as pd
import plotly.express as px
import colorsys
import plotly.graph_objects as go

def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def parse(df, num_x, num_y):
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
    # num_x = 5
    # num_y = 10
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
    df_xy['rgb_int'] = df_xy['rgb'].apply(lambda x: (int(np.floor(x[0]*255)), int(np.floor(x[1]*255)), int(np.floor(x[2]*255))))
    df_xy['hex'] = df_xy['rgb_int'].apply(lambda x: f'#{rgb_to_hex(x)}')
    fig = px.scatter(x=df_xy['x'], y=df_xy['y'], color=df_xy['hex'], color_discrete_map="identity")
    fig.update_layout({'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)'})
    fig.update_layout(title_text='Heat Map', title_x=0.5, title_y=0.925)
    # strout = {['' for i in range(num_x)]}
    strout = {}
    for i in range(num_x):
        # print(i)
        df_rgb = c[((i+1)*num_y-num_y):((i+1)*num_y)]
        df_rgb = df_rgb*255
        # df_rgb = df_rgb.apply(np.floor)
        df_rgb = df_rgb.astype('int')
        if (i % 2) == 1:
            df_rgb = df_rgb.loc[::-1].reset_index()
        # print(df_rgb)
        str = ''
        print(df_rgb)
        for index, row in df_rgb.iterrows():
            r = row[0]
            g = row[1]
            b = row[2]
            print(f'{index} {b}')
            str = str+f',{r},{g},{b}'
        str = str[1:]
        print(str)
        strout[i] = str

    return fig, strout

def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y = [], name="Heat Map"))
    fig.update_layout(title="Heat Map")
    fig.update_layout(template = None)
    fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_layout({'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)'})
    return fig