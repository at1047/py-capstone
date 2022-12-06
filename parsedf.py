
import numpy as np
import pandas as pd
import plotly.express as px
import colorsys
import plotly.graph_objects as go

def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def parse(filename, num_x, z, layers):
    # filename = 'waterbaseline'
    df_raw = pd.read_pickle(f'static/files/{filename}.pkl')
    df_xy = df_raw.copy() # change Z depending on model
    t_min = df_raw['t'].min()
    t_max = df_raw['t'].max()
    t_range = t_max - t_min
    # print(f't_min = {t_min}, t_max = {t_max}, z = {z}')
    print(filename)
    df_xy['t_normalized'] = (df_xy['t']-t_min)/t_range
    # print(df_xy['t_normalized'])
    df_xy['rgb'] = df_xy.apply(lambda x: colorsys.hsv_to_rgb(((1-x['t_normalized'])/360*240), 1, 1), axis=1)
    df_xy['rgb_int'] = df_xy['rgb'].apply(lambda x: (int(np.floor(x[0]*255)), int(np.floor(x[1]*255)), int(np.floor(x[2]*255))))
    df_xy['rgb_str'] = df_xy.apply(lambda x: f'rgb{x["rgb_int"]}', axis=1)
    df_xy['rgb_tuple'] = df_xy.apply(lambda x: (x['t_normalized'], f'rgb{x["rgb_int"]}'), axis=1)
    # df_xy['hex'] = df_xy['rgb_int'].apply(lambda x: f'#{rgb_to_hex(x)}')
    df_final = pd.DataFrame(columns = ['x', 'y', 't'])
    for i in range(num_x):
        df_tmp = df_xy.loc[df_raw['z'] == z].copy()
        df_tmp['x'] = i
        df_final = df_final.append(df_tmp)
    
    fig = px.scatter(df_final, x='x', y='y', color='t', color_continuous_scale=df_xy.loc[df_raw['z'] == z]['rgb_str'].tolist())
    fig.update_layout({'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)'})
    fig.update_layout(title_text='Heat Map', title_x=0.5, title_y=0.925)
    
    strout = []
    for i, layer in layers.items():
        if layer == -1:
            str = f'-1:{i}'
        else:
            str = f'{i}:'
            for index, row in df_xy.loc[df_xy['z'] == layer]['rgb_int'].iteritems():
                r = row[0]
                g = row[1]
                b = row[2]
                str = str+f'{r},{g},{b},'
            str = str[0:-1]
        strout.append(str)
    # print(strout)

    return fig, f'[{t_max:.2f}, {t_min:.2f}]', strout

def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y = [], name="Heat Map"))
    fig.update_layout(title="Heat Map")
    fig.update_layout(template = None)
    fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_layout({'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)'})
    return fig