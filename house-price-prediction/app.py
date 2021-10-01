import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import pycountry
import pycountry_convert as pc
import plotly_express as px

gapminder = px.data.gapminder()

df  = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')
dfm = df.set_index(['Country Name','Indicator Name','Year']).sort_index() # multi index df
#df=df.dropna()
available_indicators = df['Indicator Name'].unique()

df['code'] = [i if pycountry.countries.get(name=i)==None else pycountry.countries.get(name=i).alpha_3 for i in df['Country Name']]  

continent = []
for i in df['Country Name']: 
    try: 
        continent.append(pc.convert_continent_code_to_continent_name(pc.country_alpha2_to_continent_code(pc.country_name_to_country_alpha2(i))))
    except:
        continent.append('')

df['continent'] = continent  


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

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
])

def generate_line(dataframe):
    return html.Div(
        dcc.Graph(
            id='line-graph'),
            
        ),

    
def generate_graph(dataframe):
    return html.Div([
        dcc.Graph(id='graph-with-slider'),
        html.Label(['Indicators (x-axis, y-axis, size)',dcc.Dropdown(
            id='multy-selection-column',
            options=[{'label': i, 'value': i, 'disabled': False, 'title': 'todo: # instances'} for i in available_indicators],
            value=['Fertility rate, total (births per woman)', 
                   'Life expectancy at birth, total (years)'
                   ],
            multi=True,
            placeholder="Select indicators",
            ),]
        ),
        
], className="six columns")

def generate_map(dataframe):
    return html.Div([
        dcc.Graph(id='map-with-slider'),
        html.Label(['Indicator (z-axis)',dcc.Dropdown(
            id='zaxis-column',
            options=[{'label': i, 'value': i} for i in available_indicators],
            value='Fertility rate, total (births per woman)'
            ),]
        ),
        
], className="six columns")

app.layout = html.Div([
    html.Div([
        #generate_table(df[(df['Indicator Name']=='GDP growth (annual %)')&(df['Year']==1992)&(df['Country Name']=='Iraq')]),
        generate_graph(df),
        generate_map(df),
    ], className="row"),
    html.Div([
        dcc.Slider(
            id='year-slider',
            min=df['Year'].min(),
            max=df['Year'].max(),
            value=df['Year'].min(),
            marks={str(year): str(year) for year in df['Year'].unique()},
            step=None
        ),
        dcc.Graph(figure=px.scatter(gapminder, x="gdpPercap", y="lifeExp", animation_frame="year", animation_group="country",
                   size="pop", color="continent", hover_name="country", facet_col="continent",
                   log_x=True, size_max=45, range_x=[100,100000], range_y=[25,90])),
    ], className="row")
    
])

# it just searches in options.label
@app.callback(
    Output("multy-selection-column", "options"),
    [Input("multy-selection-column", "search_value")],
    [State("multy-selection-column", "value")],
)
def update_multi_options(search_value, value):
    if not search_value:
        raise PreventUpdate
    # Make sure that the set values are in the option list, else they will disappear
    # from the shown select list, but still part of the `value`.
    options = [{'label': i, 
                'value': i, 
                'disabled': False, 
                'title': 'todo: # instances'} for i in available_indicators]
    return [
        o for o in options if search_value in o["label"] or o["value"] in (value or [])
    ]

@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('multy-selection-column', 'value'),
     #Input('xaxis-column', 'value'),
     #Input('yaxis-column', 'value'),
     Input('year-slider', 'value')])
def update_figure(selected_multi_column,
                  #selected_xaxis_column,
                  #selected_yaxis_column,
                  selected_year):
    selected_multi_column=selected_multi_column[:3] # ignore > 3
    is_size = len (selected_multi_column) == 3
    if len (selected_multi_column) < 2: return {'data': [],'layout': dict()}
    pivot=df[df['Indicator Name'].isin(selected_multi_column)].pivot_table(values='Value',index=['Year','continent','Country Name'],columns=['Indicator Name']) 
    min=pivot.min()
    max=pivot.max()
    pivot=pivot.loc[selected_year]
    
    groups = df.continent.unique()
    traces = []
    for group in groups:
        traces.append(dict(
            x=pivot.loc[group][selected_multi_column[0]],
            y=pivot.loc[group][selected_multi_column[1]],
            text=pivot.loc[group][selected_multi_column[2]].astype(str)+pivot.loc[group].index if is_size else pivot.loc[group].index,
            mode='markers',
            opacity=0.7,
            marker={
                'size': pivot.loc[group][selected_multi_column[2]].astype(str) if is_size else 15,
                'sizemode': 'area',
                'sizeref': 2.*max[2]/(40.**2) if is_size else 1,
                'sizemin': 4,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=group
        ))

    return {
        'data': traces,
        'layout': dict(
            title={
                    'text': '{} vs. {} <br> for {} (size) in {}'.format(selected_multi_column[0],selected_multi_column[1],selected_multi_column[2],selected_year) if is_size else '{} vs. {} in {}'.format(selected_multi_column[0],selected_multi_column[1],selected_year),
                    'y':0.9,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
            xaxis={'title': selected_multi_column[0],
                   'range': [min[0],max[0]],
                   'layer': 'above traces',  
                  },
            yaxis={'title': selected_multi_column[1],
                   'range': [min[1],max[1]],
                  },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 1, 'y': 0},
            hovermode='closest',
            transition = {'duration': 500},
            cliponaxis = False,
            #margin={"r":0,"t":0,"l":0,"b":0},
        )
    }

@app.callback(
    Output('map-with-slider', 'figure'),
    [Input('zaxis-column', 'value'),
     Input('year-slider', 'value')])
def update_figure(selected_zaxis_column,
                  selected_year):
    filtered_df = df[(df.Year == selected_year)&(df['Indicator Name']==selected_zaxis_column)]
    return {
        'data': [ dict(
                type = 'choropleth',
                locations = filtered_df['code'],
                z = filtered_df.Value,
                text = filtered_df['Country Name'],
                zmax=df[df['Indicator Name']==selected_zaxis_column].Value.max(),
                zmid=df[df['Indicator Name']==selected_zaxis_column].Value.mean(),
                zmin=df[df['Indicator Name']==selected_zaxis_column].Value.min()
                 )
        ],
        'layout': dict(
                title = '{} in {}'.format(selected_zaxis_column,selected_year),
                colorbar = True,
                geo = dict(
                    scope='world',
                    projection=dict( type='natural earth' ),
                    showframe = False,
                margin={"r":0,"t":0,"l":0,"b":0},
                ),
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)