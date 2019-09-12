import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import json
import flask
import dash_bio as dashbio

#import number of nodes per level for each root
df = pd.read_csv("withoutsum.csv")

#Rename first column to Disease Name
df = df.rename(columns = {'Unnamed: 0':"Disease Name"})

#store column names
cols = df.columns 

#import data with total nodes per root
df2 = pd.read_csv("withsum.csv")

#rename column
df2 = df2.rename(columns = {'Unnamed: 0':"Disease Name"})

cols2 = df2.columns #stores col names in variable

#Circos data
colors = ['#996600', '#666600',
 '#99991E', '#CC0000',
 '#FF0000', '#FF00CC',
 '#FFCCCC', '#FF9900',
 '#FFCC00', '#FFFF00',
 '#CCFF00', '#00FF00',
 '#358000', '#0000CC',
 '#6699FF', '#99CCFF',
 '#00FFFF', '#CCFFFF',
 '#9900CC', '#CC33FF',
 '#CC99FF', '#666666',
 '#999999', '#CCCCCC',
 '#ABE2FB', '#FF8C00']

val = 1 #value of layout
counter = 0
layout_data = []
for disease in df["Disease Name"]:
    layout_data.append({"id":val, "label":disease,"color":colors[counter],"len":df2["total_nodes"][counter]})
    val += 1
    counter += 1

#open list of number of common nodes between each root
with open('intersecting_nodes.txt', 'r') as filehandle:
    common_nodes = json.load(filehandle)

#creating circos data
circos_data = []

for root in common_nodes.keys():
    for key in common_nodes[root]:
        if common_nodes[root][key] != 0:
            circos_data.append({"color":"#ff5722","source": {"id":root, "start":0, "end":common_nodes[root][key]},"target":{"id":key,"start":0,"end":common_nodes[root][key]}})
            
app = dash.Dash(__name__)

#set up URL bar
url_bar_and_content_div = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

#Homepage layout
layout_index = html.Div([
    dcc.Link("Circos Graph", href='/page-1'), #link to page 1
    html.Br(), #inserts line break
    dcc.Link("Barplots", href='/page-2'), #link to page 2
    ])

layout_page_1 = html.Div([
    html.H2('Circos Graph'), #Header of page
    
    #specify Circos graph layout
    dashbio.Circos(id = "network-circos",
                   layout = layout_data,
                   tracks = [{'type': 'CHORDS',
            'data': circos_data,
            'config': {
                'tooltipContent': {
                    'source': 'source',
                    'sourceID': 'id',
                    'target': 'target',
                    'targetID': 'id',
                    'targetEnd': 'end'
                }
            }
        }]
                  ),
    html.Div(id='circos-output'),
    html.Br(), 
    dcc.Link('Navigate to homepage', href='/'), #back to home page
    html.Br(),
    dcc.Link("Navigate to Barplot", href='/page-2'), #to second DCC page
    ])

layout_page_2 = html.Div([
    html.H2('Barplot'),
    dcc.Dropdown(id="disease-type", #
                            options = [{"label":disease, "value":disease} for disease in df[cols[0]]],
                             value = df[cols[0]].iloc[0]
                            ),
    dcc.Graph(id="graphics"),
    html.Div(id='barplot-output'),
    html.Br(),
    dcc.Link('Navigate to homepage', href='/'),
    html.Br(),
    dcc.Link('Navigate to Circos', href='/page-1'),
    ])

def serve_layout():
    if flask.has_request_context():
        return url_bar_and_content_div
    return html.Div([
        url_bar_and_content_div,
        layout_index,
        layout_page_1,
        layout_page_2,
    ])

app.layout = serve_layout

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == "/page-1":
        return layout_page_1
    elif pathname == "/page-2":
        return layout_page_2
    else:
        return layout_index

# Barplot callbacks
@app.callback(
Output("graphics","figure"),
[Input("disease-type","value")])

def update_graph(selected_disease):
    filtered_df = df[df[cols[0]] == selected_disease]
    nodes = filtered_df.loc[:,"1":"12"].values.tolist()
    nodes = nodes[0]
    return {
        "data": [
                 {"x":list(cols)[2:14],"y":nodes,"type":"bar"},
             ],
        "layout": go.Layout(title = "Nodes Per Level",
                           xaxis = {"title":"Levels"},
                            yaxis = {"title":"Nodes"}
                           )
    }

if __name__ == '__main__':
    app.run_server()