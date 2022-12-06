import base64
import datetime
import io
import parsedf
import serial
import time
import json

import dash
from dash.dependencies import Input, Output, State
from dash_extensions.enrich import Output, DashProxy, Input, MultiplexerTransform

from dash import dcc, html, State
import dash_daq as daq
import pandas as pd

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = dash.Dash(__name__)
app = DashProxy(transforms=[MultiplexerTransform()])

try:
    arduino = serial.Serial(port='/dev/cu.usbmodem101', baudrate=9600, timeout=.1)
except:
    pass

app.layout = html.Div(id='app', children=[
    dcc.Store(id='session', storage_type='session'),
    html.H1(children='Adaptive Mechanics: COMSOL Simulation Visualizer and Converter', style={'text-align': 'center'}),
    
    html.Div(id='content-wrapper', children=[
        html.Div(id='mid-wrapper', children=[
            dcc.Graph(id='output-data-upload', style={'width': '550px', 'height': '500px'}),
            html.Div(id='controls-wrapper', children=[
                html.Div(style={'display': 'flex', 'flex-direction': 'row'}, children=[html.P(children='Model Name: '), html.P(id='filename-output')]),
                html.Div(style={'display': 'flex', 'flex-direction': 'row'}, children=[html.P(children='Z-layer: '), html.P(id='z-output')]),
                html.Div(style={'display': 'flex', 'flex-direction': 'row'}, children=[html.P(children='Temp Range: '), html.P(id='t-output')]),
                dcc.Dropdown(['50bar 500ms', '75bar 75ms', '75bar 500ms', 'TE + Hydrogen', 'Water Baseline'], 'Water Baseline', id='df_dropdown', clearable=False),
                # html.Div(className='selector-wrapper', children=[html.P(children='Number of Columns'),
                #     daq.NumericInput(id='num_x_input', value=5, min=1, max=10)]),
                # html.Div(className='selector-wrapper', children=[html.P(children='Number of Rows'),
                #     daq.NumericInput(id='num_y_input', value=12, min=1, max=12)]),
                dcc.Dropdown(['Thermal Electric Top', 'Thermal Electric Bottom', 'Pipes', 'Only Pipes'], id='layer_dropdown', clearable=False),
                
                html.Div(id='arduino-controls', children=[html.P(children='Arduino Control'),
                    html.Button('Resend RGB String', id='button-arduino-string'),
                    html.Button('Reset LEDs', id='button-arduino-reset'),
                    # html.Button('Send Command', id='button-arduino'),
                    # html.Div(className='selector-wrapper', children=[html.P(children='Send to Layer'),
                    # daq.NumericInput(id='layer_selector', value=1, min=1, max=3)]),
                    # dcc.Input(id='arduino-input', type='text', placeholder='command',
                    #     style={'width': '96%', 'height': '30px', 'margin-top': '10px', 'padding-left': '8px', 'overflow': 'auto', 'border-radius': '5px', 'box-shadow': 'inset 1px 1px 2px 2px #e6e6e6', 'border': '0'},
                    #     debounce=True),
                    html.P(id='arduino-output', style={'font-weight':'lighter', 'text-align': 'center', 'margin-top': '20px'})]),
                    dcc.Loading(
                        id="loading-1",
                        type="default",
                        children=html.Div(id="loading-output-1"),
                        style={'margin-top':'70px'}
                    )
                # dcc.Upload(
                #     id='upload-data',
                #     children=html.Div(['Drag and Drop or Select File'])
                # )
                ])
        ]),
        html.Div(id='textarea-output'),
        html.Div(id='hidden-div', style={'display':'none'})
    ],
),
    
])

# def parse_contents(contents, filename, num_x, num_y, z):
#     content_type, content_string = contents.split(',')
#     # print(content_string)
#     decoded = base64.b64decode(content_string)
#     # print(decoded)
#     try:
#         if 'csv' in filename:
#             # Assume that the user uploaded a CSV file
#             df = pd.read_csv(
#                 io.StringIO(decoded.decode('utf-8')), skiprows=8)
#             # print(df)
#         # elif 'xls' in filename:
#         #     # Assume that the user uploaded an excel file
#         #     df = pd.read_excel(io.BytesIO(decoded))
#     except Exception as e:
#         print(e)
#         return html.Div([
#             'There was an error processing this file.'
#         ])

#     return parsedf.parse(df, num_x, num_y, z)

@app.callback(Output('output-data-upload', 'figure'),
              Output('textarea-output', 'children'),
              Output('session', 'data'),
              Output('filename-output', 'children'),
              Output('z-output', 'children'),
              Output('t-output', 'children'),
              Output('layer_dropdown', 'value'),
              Output('layer_dropdown', 'options'),
            #   Output('df_dropdown', 'value'),
            #   Output('layer_dropdown', 'value'),
              Input('df_dropdown', 'value'),
            #   Input('num_y_input', 'value'),
              Input('layer_dropdown', 'value'))
def update_output(filename_selector, layer_name):
    num_x = 5
    # print(layer_name)
    z = 0
    layers = {1:0, 2:-1, 3:-1}
    # ['50bar 500ms', '75bar 75ms', '75bar 500ms', 'TE + Hydrogen', 'Water Baseline']
    if (filename_selector == 'TE + Hydrogen'):
        value = layer_name
        options = ['Thermal Electric Top', 'Thermal Electric Bottom', 'Pipes']
        filename = 'thermoelectric_h2'
        layers = {1: 2.5, 2: 0.3, 3: -2} # [-2, 0.3, 2.5]
    else:
        if (filename_selector == '50bar 500ms'):
            filename = '50bar500ms'
        elif (filename_selector == '75bar 75ms'):
            filename = '75bar75ms'
        elif (filename_selector == '75bar 500ms'):
            filename = '75bar500ms'
        elif (filename_selector == 'Water Baseline'):
            filename = 'waterbaseline'
        value = 'Only Pipes'
        options = ['Only Pipes']
        layer_name = 'Only Pipes'
        layers = {1:0, 2:-1, 3:-1}

    if (filename):
        if layer_name == 'Thermal Electric Top':
            z = -2
        elif layer_name == 'Thermal Electric Bottom':
            z = 0.3
        elif layer_name == 'Pipes':
            num_x = 6
            z = 2.5
        elif layer_name == 'Only Pipes':
            z = 0
        # print(z)
        # fig = parse_contents(content, filename, num_x, z)
        fig, t_range, strout = parsedf.parse(filename, num_x, z, layers)
        return fig, strout, strout, filename_selector, z, t_range, value, options
        # fig, str = parse_contents(content, filename, num_x, num_y, z)
        # return fig, json.dumps(str), filename
    else:
        return parsedf.blank_fig(), '', 'testing2', '', 0, '', value, options

@app.callback(Output('arduino-output', 'children'),
              Output("loading-output-1", "children"),
              Input('session', 'data'),
              Input('button-arduino-string', 'n_clicks'))
def update_arduino(cmds, n_clicks):
    # if cmd:
    for cmd in cmds:
        # print(k)
        print(f'command: {cmd}')
        arduino.write(bytes(cmd, 'utf-8'))
        time.sleep(1.5)
            
    #     # str = arduino.readline().decode("utf-8")
    #     str = 'Sent'
    # else:
    #     str = ''
    # str = cmd
    # str = arduino.readline().decode("utf-8")
    return '', ''

# @app.callback(Output('arduino-output', 'children'),
#               Output('arduino-input', 'value'),
#               Input('button-arduino', 'n_clicks'),
#               State('arduino-input', 'value'))
# def update_arduino(n_clicks, arduino_input=''):
#     if arduino_input:
#         stdin = json.loads(arduino_input)
#         # print(stdin)
#         for k, v in stdin.items():
#             # print(k)
#             payload = f'{k}:{v}'
#             print(payload)
#             arduino.write(bytes(payload, 'utf-8'))
#             time.sleep(1.5)
            
#         # str = arduino.readline().decode("utf-8")
#         str = 'Sent'
#     else:
#         str = ''
#     # str = arduino.readline().decode("utf-8")
#     return str, ''

@app.callback(Output('arduino-output', 'children'),
              Input('button-arduino-reset', 'n_clicks'))
def reset_arduino(n_clicks):
    for layer in [1,2,3]:
        cmd = f'-1:{layer}'
        arduino.write(bytes(cmd, 'utf-8'))
        time.sleep(1.5)
        # str = arduino.readline().decode("utf-8")
    return ''

if __name__ == '__main__':
    app.run_server(debug=True)