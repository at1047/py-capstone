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
arduino = serial.Serial(port='/dev/cu.usbmodem101', baudrate=9600, timeout=.1)

app.layout = html.Div(id='app', children=[
    html.H1(children='Adaptive Mechanics: COMSOL Simulation Visualizer and Converter', style={'text-align': 'center'}),
    
    html.Div(id='content-wrapper', children=[
        html.Div(id='mid-wrapper', children=[
            dcc.Graph(id='output-data-upload', style={'width': '550px', 'height': '500px'}),
            html.Div(id='controls-wrapper', children=[
                html.Div(children=[html.P(children='Filename'), html.P(id='filename-output')]),
                html.Div(className='selector-wrapper', children=[html.P(children='Number of Columns'),
                    daq.NumericInput(id='num_x_input', value=5, min=1, max=10)]),
                html.Div(className='selector-wrapper', children=[html.P(children='Number of Rows'),
                    daq.NumericInput(id='num_y_input', value=12, min=1, max=12)]),
                
                html.Div(id='arduino-controls', children=[html.P(children='Arduino Control'),
                    html.Button('Send RGB String', id='button-arduino-string'),
                    html.Button('Reset LEDs', id='button-arduino-reset'),
                    html.Button('Send Command', id='button-arduino'),
                    dcc.Input(id='arduino-input', type='text', placeholder='', style={'width': '98%', 'height': '20px', 'margin-top': '10px', 'overflow': 'auto'}, debounce=True),
                    html.P(id='arduino-output', style={'font-weight':'lighter'})]),
                dcc.Upload(
                    id='upload-data',
                    children=html.Div(['Drag and Drop or Select File'])
                )])
        ]),
        html.Div(id='textarea-output'),
        html.Div(id='hidden-div', style={'display':'none'})
    ],
),
    
])

def parse_contents(contents, filename, num_x, num_y):
    content_type, content_string = contents.split(',')
    # print(content_string)
    decoded = base64.b64decode(content_string)
    # print(decoded)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), skiprows=8)
            # print(df)
        # elif 'xls' in filename:
        #     # Assume that the user uploaded an excel file
        #     df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return parsedf.parse(df, num_x, num_y)

@app.callback(Output('output-data-upload', 'figure'),
              Output('textarea-output', 'children'),
              Output('filename-output', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              Input('num_x_input', 'value'),
              Input('num_y_input', 'value'))
def update_output(content, filename, num_x, num_y):
    if (content and filename):
        fig, str = parse_contents(content, filename, num_x, num_y)
        return fig, json.dumps(str), filename
    else:
        return parsedf.blank_fig(), '', 'No file selected'

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
#     print(str)
#     return str, ''

@app.callback(Output('arduino-output', 'children'),
              Output('arduino-input', 'value'),
              Input('button-arduino', 'n_clicks'),
              State('arduino-input', 'value'))
def update_arduino(n_clicks, arduino_input=''):
    if arduino_input:
        stdin = json.loads(arduino_input)
        # print(stdin)
        for k, v in stdin.items():
            # print(k)
            payload = f'{k}:{v}'
            print(payload)
            arduino.write(bytes(payload, 'utf-8'))
            time.sleep(1.5)
            
        # str = arduino.readline().decode("utf-8")
        str = 'Sent'
    else:
        str = ''
    # str = arduino.readline().decode("utf-8")
    print(str)
    return str, ''

@app.callback(Output('arduino-output', 'children'),
              Input('button-arduino-reset', 'n_clicks'))
def reset_arduino(n_clicks):
    arduino.write(bytes('-1:1', 'utf-8'))
        # time.sleep(0.05)
        # str = arduino.readline().decode("utf-8")
    return 'Cleared'

if __name__ == '__main__':
    app.run_server(debug=True)