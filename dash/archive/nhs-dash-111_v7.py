# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go

import pandas as pd
import numpy as np

# test imports
import json


''' Start : NHS cancer survival Data prep '''
url = 'cancersurvivalbystage.xls'
df_cancer = pd.read_excel(url, sheet_name='Table 1. Full Results',skiprows=5)

# clean the data
df_cancer = df_cancer[df_cancer['Sex']!='Persons']
df_cancer = df_cancer[df_cancer['Stage']!='All stages combined']
df_cancer['Number of Survivors']=df_cancer['Number of tumours']*df_cancer['Net Survival %']/100

cancer_years = df_cancer['Cohort'].unique()
cancer_site = df_cancer['Cancer site'].unique()

''' End : NHS cancer survivalData prep '''

''' Start : NHS 111 Data prep '''

# Data manipulation
url = 'https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2017/12/NHS-111-MDS-time-series-to-2017-November-v2.xlsx'
df = pd.read_excel(url, sheet_name='Raw', skiprows=5, header=0, )#, sheet_name='All Attendances - Male', skiprows=3, header=0)
df.rename(columns={'Unnamed: 0':'Concat', 'Unnamed: 1':'Region', 'Unnamed: 2':'Provider Code', 'Unnamed: 3':'Date', 'Unnamed: 4':'Code', 'Unnamed: 5':'Area'}, inplace=True)

metric_options = ['Population', 'Total calls offered', 'No calls answered', 'Calls answered within 60 secs','Ambulance dispatches']
dimension_options = ['Area','Region','Provider Code']
# Future development: Could allow users to select metrics
metric_options_selected = metric_options

# Interactive variables
dimension_picker = dimension_options[0]
dimension_element_picker = df[dimension_picker][0]


# Data transformation
df_filtered = df[df[dimension_picker] == dimension_element_picker]
# df_filtered = df
df_grouped = df_filtered.groupby(by=[dimension_picker,'Date'], as_index=False).sum()

df_table_111 = df.loc[0:20]

''' End : NHS 111 Data prep '''

''' Start : NHS Hospital Outpatient Activity data prep '''

url = 'https://digital.nhs.uk/media/34230/Hospital-Outpatient-Activity-2016-17-All-attendances/default/hosp-epis-stat-outp-all-atte-2016-17-tab.xls'
df_male = pd.read_excel(url, sheet_name='All Attendances - Male', skiprows=3, header=0)#names=("code", "provider_desc", "male", "female", "unkown", "total"))
df_female = pd.read_excel(url, sheet_name='All Attendances - Female', skiprows=3, header=0)#names=("code", "provider_desc", "male", "female", "unkown", "total"))

# Append the two data frames to one and other
df_male["Gender"] = "Male"
df_female["Gender"] = "Female"
df_out_act= pd.concat([df_male, df_female])

# unpivot the age columns
df_out_act= df_out_act.melt(id_vars=["Main Specialty Code", "Main Specialty Code Description","Gender"])
df_out_act.rename(columns={'variable':'Age Group'},inplace=True)
df_out_act['Age Group'] = df_out_act['Age Group'].astype('str')

# remove total columns
df_out_act= df_out_act[df_out_act["Main Specialty Code Description"] != "Total"]
df_out_act= df_out_act[df_out_act["Age Group"] != "Total"]
df_out_act.head(3)

# Define the sorter
sorter = ['0', '1-4', '5-9', '5-9 ', '10-14', '15', '16', '17', '18', '19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80-84', '85-89', '90-120', 'Unknown']

# Create the dictionary that defines the order for sorting
sorterIndex = dict(zip(sorter,range(len(sorter))))

# Generate a rank column that will be used to sort
# the dataframe numerically
df_out_act['Age Group Rank'] = df_out_act['Age Group'].map(sorterIndex)

df_out_act.sort_values('Age Group Rank', inplace = True)
# df_out_act.drop('Age Group Rank', inplace = True)

# Clean up the data types
df_out_act["Age Group"] = df_out_act["Age Group"].astype("category")
df_out_act["Gender"] = df_out_act["Gender"].astype("category")

# Set up summarised code for Body Systems
divisions = pd.read_excel('divisions of clinical work.xlsx')
divisions.rename(columns={'Code': 'Main Specialty Code', 'Main Specialty Title': 'Main Specialty Code Description'}, inplace=True)
divisions.drop(columns='Main Specialty Code Description', inplace=True)
df_out_act= df_out_act.merge(divisions, how='left', on='Main Specialty Code')

# Set up group by
dimension = {'Divisions of clinical work': df_out_act["Divisions of clinical work"].unique(),'Gender': df_out_act['Gender'].unique()}
dimension_out_act_options = ['Gender', 'Divisions of clinical work']
dimension_out_act_picker = dimension_out_act_options[0]
df_out_act_grouped = df_out_act.groupby(by=[dimension_out_act_picker,'Age Group','Age Group Rank'], as_index=False).sum()
df_out_act_grouped.dropna(inplace=True)

''' Emd : NHS Hospital Outpatient Activity data prep '''

app = dash.Dash()
app.config['suppress_callback_exceptions']=True # used when assigning callbacks to components that are generated by other callbacks (and therefore not in the initial layout), then you can suppress this exception by setting

# Choose the CSS styly you like
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})


tabs = {1:'Outpatient Activity 2016-17', 2:'111 Program', 3: 'Cancer Survival'}

app.layout = html.Div(children=[
    html.Div([
        html.H1(children='NHS analysis', style = {'display': 'inline-block'}),
        html.Img(src='http://survation.com/wp-content/uploads/2014/12/NHS-logo.jpg', style = {'position' : 'absolute', 'right':'0px', 'height':'5.5%', 'width':'5.5%', 'padding' : '10px'})
        ],
        style = {'display': 'inline-block'}
    ),
    
    #### TRYING OUT DASH EXAMPLE
    # html.Div([  # subpage 1
    # 
    #         # Row 1 (Header)
    # 
    #         html.Div([
    # 
    #             html.Div([
    #                 html.H5(
    #                     'Goldman Sachs Strategic Absolute Return Bond II Portfolio'),
    #                 html.H6('A sub-fund of Goldman Sachs Funds, SICAV',
    #                         style={'color': '#7F90AC'}),
    #             ], className="nine columns padded"),
    # 
    #             html.Div([
    #                 html.H1(
    #                     [html.Span('03', style={'opacity': '0.5'}), html.Span('17')]),
    #                 html.H6('Monthly Fund Update')
    #             ], className="three columns gs-header gs-accent-header padded", style={'float': 'right'}),
    # 
    #         ], className="row gs-header gs-text-header"),
    # ])
    # html.Br([]),

    # tabs to navigate between analysis
    dcc.Tabs(
        tabs=[
            {'label': '{}'.format(v), 'value': k} for k, v in tabs.items()
        ],
        value=1,
        id='tabs'
    ),
    # call backs will modify this tab-output depending on which tab is selected
    html.Div(id='tab-output'),


    # # navigation buttons
    # html.Div(
    #     [
    #         html.Button('Back', id='back', style={
    #                     'display': 'inline-block'}),
    #         html.Button('Next', id='next', style={
    #                     'display': 'inline-block'})
    #     ],
    #     className='two columns offset-by-two'
    # )





])

"""
START : Tab tab-output
"""

@app.callback(
    Output(component_id='tab-output',  component_property='children'),
    [Input(component_id='tabs', component_property='value')]
)
def set_tab_to_display(tab):
    if tab == 2:
        tab_display = html.Div(children=[
            html.H1(children=tabs[2]),
            dcc.Markdown(children='''The data is taken from the [NHS 111 Minimum Data Set 2017-18](https://www.england.nhs.uk/statistics/statistical-work-areas/nhs-111-minimum-data-set/nhs-111-minimum-data-set-2017-18/). NHS 111 is available 24 hours a day, 7 days a week, 365 days a year to respond to people’s health care needs when:  
            1. it’s not a life threatening situation, and therefore is less urgent than a 999 call  
            2. the GP isn’t an option, for instance when the caller is away from home  
            3. the caller feels they cannot wait and is simply unsure of which service they require  
            4. the caller requires reassurance about what to do next 
            '''),

            
            
            html.Div(children=[
            

                dcc.Graph(id='nhs-111-graph-3d', style={'display': 'inline-block', 'width':'40%'}),

                
                html.Div(children=[
                
                    html.Div(children=[
        
                        # dropdown to select the dimension
                        html.Div(dcc.Dropdown(
                            id = 'dimension_dropdown',
                            options=[
                                dict(label = dimension_options[i],value = dimension_options[i]) for i in range (0, len(dimension_options))
                            ],
                            value = dimension_options[0],
                        ), style={ 'display': 'inline-block', 'width':'20%'}),
        
                        # dropdown of chilren of the selected dimension
                        html.Div(dcc.Dropdown(
                            id = 'dimension_element_dropdown',
                            ), style={'display': 'inline-block', 'width':'40%'})
        
                    ],
                    #style={'padding': '10px'}
                    ),
                    
                    
                    dcc.Graph(id='nhs-111-graph-bar', style={'display': 'inline-block', 'width':'300%'}),
            
                ],
                style={'display': 'inline-block'}
                )
            
            ])



        ])
    elif tab == 1:
        tab_display = html.Div(children=[
            html.H1(children=tabs[1]),
            dcc.Markdown(children='''The data is taken from the [Hospital Episodes Statistics (HES)](https://digital.nhs.uk/catalogue/PUB30154) data warehouse. HES contains records of all admissions, appointments and attendances for patients admitted to NHS hospitals in England.'''),

            html.Div(children=[
                dcc.Dropdown(
                    id = 'dimension_dropdown_out_act',
                    options=[
                        dict(label = dimension_out_act_options[i],value = dimension_out_act_options[i]) for i in range (0, len(dimension_out_act_options))
                    ],
                    value = dimension_out_act_options[0],
                    #style={'width': '48%'}
                )],
                style={'width': '15%', 'display': 'inline-block'}
            ),

            dcc.Graph(id='nhs-out-act-graph-bar'),
            dcc.Graph(id='nhs-out-act-graph-donought')

            ])
            
    elif tab == 3:
        tab_display = html.Div(children=[
            html.H1(children=tabs[3]),
            dcc.Markdown(children='''The data is taken from the [Hospital Episodes Statistics (HES)](https://digital.nhs.uk/catalogue/PUB30154) data warehouse. HES contains records of all admissions, appointments and attendances for patients admitted to NHS hospitals in England.'''),
            
            ## slider component not fully visable issue with dash core coponents version
            # html.Div(children=[
            #     dcc.Slider(
            #         id = 'cancer_year_slider',
            #         min=df_cancer['Cohort'].min(),
            #         max=df_cancer['Cohort'].max(),
            #         step=None,
            #         marks={str(year): str(year) for year in df_cancer['Cohort'].unique()},
            #         value = df_cancer['Cohort'].min(),
            #         ),
            #     ],
            #     style={'hieght': '5000px'}
            # ),
            html.Div(children=[    
                 dcc.Dropdown(
                    id = 'cancer_year_slider',
                    options=[
                        dict(label = cancer_years[i],value = cancer_years[i]) for i in range (0, len(cancer_years))
                    ],
                    value = cancer_years[0],
                    ),
                ],
                style={'width': '25%'}
            ),
            

            dcc.Graph(id='nhs-cancer-graph-bar',
                style={'height': '310px'},
                hoverData={'points': [{'x': cancer_site[0]}]} # inital hover state
            ),
            
            # dcc.Markdown(children=''' **Hover Data**
            # Hover over a cancer site to change graphs below'''),
            dcc.Markdown(''' **Hover over** a cancer site above to change the graphs below'''),

            html.Div(children=[
                dcc.Graph(id='nhs-cancer-graph-line', style={'display': 'inline-block', 'width': '70%'}),
                dcc.Graph(id='nhs-cancer-graph-donought', style={'display': 'inline-block', 'width': '25%'})
            ],
            style={'display': 'inline-block','width': '100%'}
            ),
            ])


    else:
        tab_display = html.Div(children=[
            html.H1(children='in progress'),
            ])
    return tab_display

"""
START : NHS_cancer_survival
"""
@app.callback(
    Output(component_id='nhs-cancer-graph-bar', component_property='figure'),
    [Input(component_id='cancer_year_slider', component_property='value')]
)
def update_graph_cancer_survival_1(date_filter):
    df_grouped = df_cancer.groupby(by=['Cohort','Cancer site'], as_index=False).sum()
    df_grouped.dropna(inplace=True)

    data = [go.Bar(
      type = 'bar',
      x = df_grouped['Cancer site'],
      y = df_grouped[df_grouped['Cohort'] == date_filter]['Number of tumours'],
      name = date_filter,
      opacity = 0.8
    )]

    # plot titles and axis labels
    layout = go.Layout(
        barmode='stack', # switch between stack and group
        # title='<b>Outpatient-Activity-2016-17 by  </b>'+dimension_picker,
        yaxis = dict(
    #         type = 'log' # switches to a logarythmic scale
            title='<i>One–year net cancer survival</i>'
        ),
        xaxis=dict(
            title='<i>Cancer site</i>'
        ) ,
        bargap=0.1,
        bargroupgap=0.15
    )

    return go.Figure(data=data, layout=layout)

# # Testing Hover over functionality
# @app.callback(
#     Output(component_id='testhoverdata', component_property='children'),
#     [Input(component_id='nhs-cancer-graph-bar', component_property='hoverData')]
# )
# def testhoverdatafunc(hoverData):
#     # return json.dumps(hoverData, indent=2)
#     return str(type(hoverData['points'][0]['x']))
    
    
@app.callback(
    Output(component_id='nhs-cancer-graph-line', component_property='figure'),
    [Input(component_id='nhs-cancer-graph-bar', component_property='hoverData')]

)
def update_graph_cancer_survival_2(hoverData):
    cancer_site_filter = hoverData['points'][0]['x']
    df_grouped = df_cancer.groupby(by=['Cohort','Cancer site'], as_index=False).sum()
    df_grouped.dropna(inplace=True)

    data = [go.Scatter(
      mode = 'lines',
      x = df_grouped['Cohort'].unique(),
      y = df_grouped[df_grouped['Cancer site'] == cancer_site_filter]['Number of tumours'],
      name = 'Number of tumours',
      opacity = 0.8),
            
            go.Scatter(
      mode = 'lines',
      x = df_grouped['Cohort'].unique(),
      y = df_grouped[df_grouped['Cancer site'] == cancer_site_filter]['Number of Survivors'] / df_grouped[df_grouped['Cancer site'] == cancer_site_filter]['Number of tumours'] *100,
      name = 'Net Survival %s',
      yaxis='y2',
      opacity = 0.8),
           ]

    # plot titles and axis labels
    layout = go.Layout(
        barmode='stack', # switch between stack and group
        # title='<b>Outpatient-Activity-2016-17 by  </b>'+dimension_picker,
        yaxis = dict(
    #         type = 'log' # switches to a logarythmic scale
            title='<i>Number of tumours</i>'
        ),
        yaxis2=dict(
            title='<i>Net Survival %</i>',
            overlaying='y',
            side='right'
        ),
        xaxis=dict(
            title=cancer_site_filter+'<i> by year</i>'
        ) ,
        bargap=0.1,
        bargroupgap=0.15,
        showlegend=False
    )


    return go.Figure(data=data, layout=layout)



@app.callback(
    Output(component_id='nhs-cancer-graph-donought', component_property='figure'),
    [Input(component_id='nhs-cancer-graph-bar', component_property='hoverData'),
    Input(component_id='cancer_year_slider', component_property='value')])


def update_graph_cancer_survival_3(x, y):
    date_filter = y
    cancer_site_filter = x['points'][0]['x']
    df_filtered = df_cancer[(df_cancer['Cohort'] == date_filter) & (df_cancer['Cancer site'] == cancer_site_filter)]
    df_grouped = df_filtered.groupby(by=['Stage'], as_index=False).sum()
    df_grouped.dropna(inplace=True)
    
    #calculates the whole value of the pie chart
    centre_value_pie = df_grouped['Number of tumours'].sum()

    data = [go.Pie(
        values = df_grouped['Number of tumours'],
        # values = df_grouped[(df_grouped['Cohort'] == date_filter) ]['Number of tumours'],
        labels = 'Stage: ' + df_cancer['Stage'].astype(str).unique(), #df_grouped['Stage'].unique(),
        type = 'pie',
        hole = 0.7,
        opacity = 0.8),
    ]

    # plot titles and axis labels
    layout = go.Layout(
        annotations = [
            {
                "font": {
                    "size": 20
                },
                "showarrow": False,
                "text": str("{:,.0f}".format(centre_value_pie)) +' Tumours', # resulting from ' + cancer_site_filter + " Cancer for the year " + str(date_filter),
                "align": 'centre',
            }
        ]
    )
    return go.Figure(data=data, layout=layout)



"""
END : NHS_cancer_survival
"""

"""
START : NHS_out_act_tab-output
"""
@app.callback(
    Output(component_id='nhs-out-act-graph-bar', component_property='figure'),
    [Input(component_id='dimension_dropdown_out_act', component_property='value')]
)
def update_graph(dimension_picker):
    df_grouped = df_out_act.groupby(by=[dimension_picker,'Age Group','Age Group Rank'], as_index=False).sum()
    df_grouped.dropna(inplace=True)

    # stops traces from exceeding max trace limit
    if len(dimension[dimension_picker]) >6:
        len_dimension_picker = 6
    else:
        len_dimension_picker = len(dimension[dimension_picker])


    data = [go.Bar(
      type = 'bar',
      x = df_grouped['Age Group'],
      y = df_grouped[df_grouped[dimension_picker] == df_grouped[dimension_picker].unique()[i]]['value'], # filters out values not belonging to the ith demension element
      name = df_grouped[dimension_picker].unique()[i],
      opacity = 0.8
    ) for i in range(0, len_dimension_picker)]

    # plot titles and axis labels
    layout = go.Layout(
        barmode='stack', # switch between stack and group
        # title='<b>Outpatient-Activity-2016-17 by  </b>'+dimension_picker,
        yaxis = dict(
    #         type = 'log' # switches to a logarythmic scale
            title='<i>Outpatient volume</i>'
        ),
        xaxis=dict(
            title='<i>Age groups</i>'
        ) ,
        bargap=0.1,
        bargroupgap=0.15
    )


    return go.Figure(data=data, layout=layout)

@app.callback(
    Output(component_id='nhs-out-act-graph-donought', component_property='figure'),
    [Input(component_id='dimension_dropdown_out_act', component_property='value')]
)
def update_pie_chart_data(dimension_picker):

    values = []

    for option in df_out_act[dimension_picker].dropna().unique():
        df_grouped = df_out_act.groupby(by=[dimension_picker,'Age Group','Age Group Rank'], as_index=False).sum()
        value = df_grouped[df_grouped[dimension_picker] == option]['value'].sum()
        values.append(value)

    fig = {
      "data": [
        {
          "values": values,
          "labels": df_out_act[dimension_picker].dropna().unique(),
          # "domain": {"x": [0, .48]},
          "name": "Outpatient-Activity-2016-17",
          "hoverinfo":"label+percent+name+value",
          "hole": .7,
          "align": 'centre',
          "type": "pie"
        }],
      "layout": {
            # "title":"Outpatient-Activity-2016-17",
            "annotations": [
                {
                    "font": {
                        "size": 14
                    },
                    "showarrow": False,
                    "text": "Outpatient-Activity-2016-17",
                    "align": 'centre',
                    # "x": 0.12,
                    "y": 0.5
                },
                {
                    "font": {
                        "size": 14
                    },
                    "showarrow": False,
                    "text": "{:,.0f}".format(df_out_act['value'].sum()),
                    "align": 'centre',
                    # "x": 0.19,
                    "y": 0.4
                }

            ]
        }
    }
    return fig

"""
END : NHS_out_act_tab-output
"""

"""
START : NHS_111_tab-output
"""

# sets the children of dimension_element_dropdown
@app.callback(
    Output(component_id='dimension_element_dropdown', component_property='options'),
    [Input(component_id='dimension_dropdown', component_property='value')]
)
def set_dimension_elements(dimension_picker):
    options = df[dimension_picker].unique()
    options = [{'label': i, 'value': i} for i in options]
    options.insert(0, {'label': 'All', 'value': 'All'})
    return options

# sets the initial value in the dimension_element_dropdown when the dimension_dropdown dropdown changes i.e. chaning the dimension.
@app.callback(
    Output(component_id='dimension_element_dropdown', component_property='value'),
    [Input(component_id='dimension_element_dropdown', component_property='options')]
)
def set_display_children(available_options):
    return available_options[0]['value']


@app.callback(
    Output(component_id='nhs-111-graph-bar', component_property='figure'),
    [Input(component_id='dimension_dropdown', component_property='value'),
    Input(component_id='dimension_element_dropdown', component_property='value')]
)
def update_graph(dimension_picker, dimension_element_picker):
    # if all is selected in the dimension_element_picker then do not include a dimension in the group by clause
    if dimension_element_picker == 'All':
        df_grouped = df.groupby(by=['Date'], as_index=False).sum()
    else:
        df_filtered = df[df[dimension_picker] == dimension_element_picker]
        df_grouped = df_filtered.groupby(by=[dimension_picker,'Date'], as_index=False).sum()

    # Future development: Could allow users to select metrics
    metric_options_selected = metric_options

    # use the DataFrame columns for generating data
    data = [go.Scatter(
        x = df_grouped['Date'],
        y = df_grouped[metric_options_selected[i]],
        mode = 'lines',
        name = metric_options_selected[i],
#         text = df_grouped[metric_options_selected[i]],
        opacity = 0.8,
    ) for i in range(0, len(metric_options_selected))] # loop through traces

    # plot titles and axis labels
    layout = go.Layout(
        barmode='group',#'group', # switch between stack and group
        # title='<b>NHS 111 calls where  </b>'+ dimension_picker+' = '+dimension_element_picker,
        yaxis = dict(
            type = 'log', # switches to a logarythmic scale
            title='<i>Volume</i>'
        ),
#         xaxis=dict(
#             title='<i>Date</i>'
#         )
    )

    return go.Figure(data=data, layout=layout)


@app.callback(
    Output(component_id='nhs-111-graph-3d', component_property='figure'),
    [Input(component_id='dimension_dropdown', component_property='value')]
)
def set_display_children(dimension_picker='Area'):
    df_grouped_3d = df.groupby(by=['Date', dimension_picker], as_index=False).sum()

    data = [go.Scatter3d(
        x=df_grouped_3d['Date'],
        z=df_grouped_3d['Calls answered within 60 secs']/df_grouped_3d['Total calls offered'],
        y=df_grouped_3d['Area'],
        mode='markers',
        marker=dict(
            size=df_grouped_3d['Total calls offered']/8000, # visualises the volume of calls
            color=df_grouped_3d['Calls answered within 60 secs']/df_grouped_3d['Total calls offered'],                # set color to an array/list of desired values
            colorscale='Viridis',   # choose a colorscale
            opacity=0.8
        )
    )]


    layout = go.Layout(
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0
        )
        # ,zaxis = dict(
        #     title="% of Calls answered within 60 secs",
        # )
    )
    return go.Figure(data=data, layout=layout)


"""
END: NHS_111_tab-output
"""



if __name__ == '__main__':
    app.run_server(debug=True)
