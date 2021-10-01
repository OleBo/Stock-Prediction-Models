# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import pycountry

df1 = pd.read_csv('https://gist.githubusercontent.com/chriddyp/c78bf172206ce24f77d6363a2d754b59/raw/c353e8ef842413cae56ae3920b8fd78468aa4cb2/usa-agricultural-exports-2011.csv')
df2 = pd.read_csv('https://gist.githubusercontent.com/chriddyp/5d1ea79569ed194d432e56108a04d188/raw/a9f9e8076b837d541398e999dcbac2b2826a81f8/gdp-life-exp-2007.csv')
df3 = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2011_february_us_airport_traffic.csv')

df2['code'] = [i if pycountry.countries.get(name=i)==None else pycountry.countries.get(name=i).alpha_3 for i in df2['country']]  

df3['text'] = df3['airport'] + '' + df3['city'] + ', ' + df3['state'] + '' + 'Arrivals: ' + df3['cnt'].astype(str)

scl = [ [0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
    [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"] ]

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ], style={
        'color': colors['text']
    })

def generate_graph(dataframe):
    return dcc.Graph(
        id='life-exp-vs-gdp',
        figure={
            'data': [
                dict(
                    x=dataframe[dataframe['continent'] == i]['gdp per capita'],
                    y=dataframe[dataframe['continent'] == i]['life expectancy'],
                    text=dataframe[dataframe['continent'] == i]['country'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in dataframe.continent.unique()
            ],
            'layout': dict(
                title='Life Expectancy vs. GDP',
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
                font={
                    'color': colors['text']
                },
                xaxis={'type': 'log', 'title': 'GDP Per Capita'},
                yaxis={'title': 'Life Expectancy'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )
    
def generate_choropleth(dataframe):
    return dcc.Graph(
        id='gap-minder',
        figure={
            'data': [ dict(
                type = 'choropleth',
                locations = dataframe['code'],
                z = dataframe['gdp per capita'],
                text = dataframe['country'],
                colorbar = dict(
                    title = 'GDP in $',
                    )
                )
            ],
            'layout': dict(
                title = 'gdp per capita',
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
                font={
                    'color': colors['text']
                },
                colorbar = True,
                geo = dict(
                    scope='world',
                    projection=dict( type='natural earth' ),
                    showframe = False,
                ),
            )
        }
    )
    
def generate_geo(dataframe):
    return dcc.Graph(
        id='most-trafficked-airports',
        figure={
            'data': [ dict(
                type = 'scattergeo',
                locationmode = 'USA-states',
                lon = dataframe['long'],
                lat = dataframe['lat'],
                text = dataframe['text'],
                mode = 'markers',
                marker = dict(
                    size = 8,
                    opacity = 0.8,
                    reversescale = True,
                    autocolorscale = False,
                    symbol = 'square',
                    line = dict(
                        width=1,
                        color='rgba(102, 102, 102)'
                    ),
                    colorscale = scl,
                    cmin = 0,
                    color = dataframe['cnt'],
                    cmax = dataframe['cnt'].max(),
                    colorbar=dict(
                        title="Incoming flightsFebruary 2011"
                    )
                )
            )],
            'layout': dict(
                title = 'Most trafficked US airports<br>(Hover for airport names)',
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
                font={
                    'color': colors['text']
                },
                colorbar = True,
                geo = dict(
                    scope='usa',
                    projection=dict( type='albers usa' ),
                    showland = True,
                ),
            )
        }
    )

markdown_text = '''
### Dash and Markdown

Dash apps can be written in Markdown.
Dash uses the [CommonMark](http://commonmark.org/)
specification of Markdown.
Check out their [60 Second Markdown Tutorial](http://commonmark.org/help/)
if this is your first introduction to Markdown!

### Core Components
For reference, see:

- [dash_core_components gallery](https://dash.plotly.com/dash-core-components)
- [dash_html_components gallery](https://dash.plotly.com/dash-html-components)
'''

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(children='Hello Dash',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='''
        Dash: A web application framework for Python.
    ''', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 3, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization',
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }
            }
        }
    ),
    
    html.H4(children='US Agriculture Exports (2011)', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    
    generate_table(df1),
    generate_graph(df2),
    generate_table(df2),
    generate_choropleth(df2),
    generate_geo(df3),
    
    dcc.Markdown(children=markdown_text,
        style={
            'color': colors['text']
        }),
    html.Div([
        html.Label('Dropdown'),
        dcc.Dropdown(
            options=[
                {'label': 'New York City', 'value': 'NYC'},
                {'label': u'Montréal', 'value': 'MTL'},
                {'label': 'San Francisco', 'value': 'SF'}
            ],
            value='MTL'
        ),

        html.Label('Multi-Select Dropdown'),
        dcc.Dropdown(
            options=[
                {'label': 'New York City', 'value': 'NYC'},
                {'label': u'Montréal', 'value': 'MTL'},
                {'label': 'San Francisco', 'value': 'SF'}
            ],
            value=['MTL', 'SF'],
            multi=True
        ),

        html.Label('Radio Items'),
        dcc.RadioItems(
            options=[
                {'label': 'New York City', 'value': 'NYC'},
                {'label': u'Montréal', 'value': 'MTL'},
                {'label': 'San Francisco', 'value': 'SF'}
            ],
            value='MTL'
        ),

        html.Label('Checkboxes'),
        dcc.Checklist(
            options=[
                {'label': 'New York City', 'value': 'NYC'},
                {'label': u'Montréal', 'value': 'MTL'},
                {'label': 'San Francisco', 'value': 'SF'}
            ],
            value=['MTL', 'SF']
        ),

        html.Label('Text Input'),
        dcc.Input(value='MTL', type='text'),

        html.Label('Slider'),
        dcc.Slider(
            min=0,
            max=9,
            marks={i: 'Label {}'.format(i) if i == 1 else str(i) for i in range(1, 6)},
            value=5,
        ),
    ], style={
        'columnCount': 2,
        'color': colors['text']
    })
])

if __name__ == '__main__':
    app.run_server(debug=True)