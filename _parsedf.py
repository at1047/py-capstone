
import numpy as np
import pandas as pd
import plotly.express as px
import colorsys
import plotly.graph_objects as go

def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def parse(df, num_x, num_y, z):
    df = df.rename(columns={'% x': 'x', 'T (K)': 't'})
    df_zrounded = pd.DataFrame(columns = ['x', 'y', 'z_rounded', 't'])
    name_z = {'pipes': 2.5, 'te_bottom': 0.3, 'te_top': -2, 'only_pipes': 0}
    for z_val in np.round(np.linspace(-2,2.5,46),1):
        z_min = z_val - 0.5
        z_max = z_val + 0.5
        df_xy = df.copy()
        df_xy = df_xy.loc[(df['z'] > z_min) & (df['z'] < z_max)]
        df_xy['z_rounded'] = z_val
        df_xy = df_xy[['x', 'y', 'z_rounded', 't']]
        df_zrounded = df_zrounded.append(df_xy)

    df_xy = df_zrounded.copy()
    df_xy = df_xy.loc[df_xy['z_rounded'] == z]
    df_xy = df_xy.loc[(df_xy['x'] < 150) & (df_xy['x'] >= 0)]
    df_xy = df_xy.loc[(df_xy['y'] < 150) & (df_xy['y'] >= 0)]
    df_xy = df_xy[['x', 'y', 't']]
    y_interval = np.floor((df_xy['y'].max() - df_xy['y'].min())/(num_y-1))
    df_xy['y_round'] = df_xy[['y']]//y_interval
    df_xy = df_xy.groupby(['y_round']).max().reset_index()
    df_xy = df_xy[['y_round', 't']]
    df_xy = df_xy.rename(columns={'y_round': 'y'})
    df_final = pd.DataFrame(columns = ['x', 'y', 't'])
    for i in range(num_x):
        df_tmp = df_xy.copy()
        df_tmp['x'] = i
        df_final = df_final.append(df_tmp)
    t_min = df_zrounded['t'].min()
    t_max = df_zrounded['t'].max()
    t_range = t_max - t_min
    df_final['t_normalized'] = (df_final['t']-t_min)/t_range

    df_final['rgb'] = df_final.apply(lambda x: colorsys.hsv_to_rgb(((1-x['t_normalized'])/360*240), 1, 1), axis=1)
    df_final['rgb_int'] = df_final['rgb'].apply(lambda x: (int(np.floor(x[0]*255)), int(np.floor(x[1]*255)), int(np.floor(x[2]*255))))
    df_final['hex'] = df_final['rgb_int'].apply(lambda x: f'#{rgb_to_hex(x)}')
    fig = px.scatter(x=df_final['x'], y=df_final['y'], color=df_final['hex'], color_discrete_map="identity")
    fig.update_layout({'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)'})
    fig.update_layout(title_text='Heat Map', title_x=0.5, title_y=0.925)
    
    
    
    # strout = {}
    # c = pd.DataFrame(df_final['rgb'].tolist())

    # for i in range(num_x):
    #     # print(i)
    #     df_rgb = c[((i+1)*num_y-num_y):((i+1)*num_y)]
    #     df_rgb = df_rgb*255
    #     # df_rgb = df_rgb.apply(np.floor)
    #     df_rgb = df_rgb.astype('int')
    #     if (i % 2) == 1:
    #         df_rgb = df_rgb.loc[::-1].reset_index()
    #     # print(df_rgb)
    #     str = ''
    #     for index, row in df_rgb.iterrows():
    #         r = row[0]
    #         g = row[1]
    #         b = row[2]
    #         str = str+f',{r},{g},{b}'
    #     str = str[1:]
    #     strout[i] = str

    return fig #, strout

def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y = [], name="Heat Map"))
    fig.update_layout(title="Heat Map")
    fig.update_layout(template = None)
    fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_layout({'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)'})
    return fig