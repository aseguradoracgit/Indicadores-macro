import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from datetime import date
import datetime
import plotly.io as pio
from pandas.tseries.offsets import MonthEnd
import base64
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
from scipy.stats import linregress
import numpy as np
#import locale

#locale.setlocale(locale.LC_ALL, 'es_ES')

tasa = pd.read_excel('Datos macro.xlsx', sheet_name="Q")
tasa=tasa.iloc[:, :6]
tasa = tasa.rename(columns={'Activa1': 'Activa', 'Pasiva1': 'Pasiva', "Spread1":"Spread"})
tasa=pd.melt(tasa, id_vars=['Mes', "Año", "Fecha"], var_name="Tipo", value_name="Tasa")
tasa["Moneda"]="Quetzales"
tasad = pd.read_excel('Datos macro.xlsx', sheet_name="$")
tasad=tasad.iloc[:, :6]
tasad = tasad.rename(columns={'Activa1': 'Activa', 'Pasiva1': 'Pasiva', "Spread1":"Spread"})
tasad=pd.melt(tasad, id_vars=['Mes', "Año", "Fecha"], var_name="Tipo", value_name="Tasa")
tasad["Moneda"]="Dólares"
tasa_final=pd.concat([tasa, tasad])
tasa_final=tasa_final.dropna()

inflacion = pd.read_excel('Datos macro.xlsx', sheet_name="Inflación")
inflacion['Año'] = inflacion['Fecha'].dt.year
inflacion['Mes'] = inflacion['Fecha'].dt.strftime('%b')
inflacion = inflacion[inflacion['Inflación'].notna()]


imae = pd.read_excel('Datos macro.xlsx', sheet_name="IMAE")
imae = imae.rename(columns={'Período': 'Fecha', 'Var. % interanual': 'IMAE'})
imae["IMAE"]=imae["IMAE"]/100
imae['Año'] = imae['Fecha'].dt.year
imae['Mes'] = imae['Fecha'].dt.month

imae_sectores=pd.read_excel('Datos macro.xlsx', sheet_name="IMAE sectores")
imae_sectores=pd.concat([imae_sectores.iloc[:,:1], imae_sectores.iloc[:,1:]/100], axis=1)
imae=imae.merge(imae_sectores, on='Fecha', how='left')

tc = pd.read_excel('Datos macro.xlsx', sheet_name="TC")
tc = tc.rename(columns={'TCR 1/': 'Tipo de cambio'})
tc["Fecha2"]=tc["Fecha"]+ MonthEnd(0)
tcm=tc.groupby(["Fecha2"]).mean().reset_index()

remesas = pd.read_excel('Datos macro.xlsx', sheet_name="Remesas")
remesas=remesas.iloc[:12,:]
remesas=pd.melt(remesas, id_vars=['Mes'], var_name="Año", value_name="Remesas")
remesas["Fecha"]=pd.to_datetime(dict(year=remesas["Año"], month=remesas.Mes, day=1))
remesas=remesas.dropna()
remesas["Remesas"]=remesas["Remesas"]*1000000


#construir dashboard
app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
server=app.server


image_filename = 'logo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

#layout del app
app.layout =  html.Div([
    html.Br(),
    dbc.Container(children=[
    dbc.Row([
        dbc.Col(html.H1(children=['Dashboard Macroeconómico']), width=8),
        dbc.Col(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), height=60), width=4)
    ], justify='start')
]),
    
    
    #primer drop down para elegir las empresas
    html.Br(),
    html.H2("Tasa de interés"),
    
    html.P("Moneda:"),
   
    html.Div(dcc.RadioItems(
    id="moneda",value="Quetzales",
    options=["Quetzales", "Dólares"]
    )),
    html.Br(),
  html.P("Rango de fechas:"),
     html.Div(  dcc.Dropdown(
        id = 'timeframe_dropdown', 
        options = [
            {'label': 'Últimos 3 años', 'value': 'Últimos 3 años'},
            {'label': 'Últimos 5 años', 'value': 'Últimos 5 años'},
            {'label': 'Últimos 10 años', 'value': 'Últimos 10 años'}
        ], 
        value='Últimos 5 años',
        clearable=False,
    ), style={"width": "30%"}),
     html.Div( dcc.DatePickerRange(
        id='fechas', display_format='DD/MM/YYYY',
        min_date_allowed=tasa_final["Fecha"].min().strftime('%Y-%m-%d'),
        max_date_allowed=tasa_final["Fecha"].max().strftime('%Y-%m-%d'),
        initial_visible_month=tasa_final["Fecha"].max().strftime('%Y-%m-%d'),
        start_date=date(2018, 1, 1),
        end_date=tasa_final["Fecha"].max().strftime('%Y-%m-%d'),)),
    #graficas
    html.Div(dcc.Graph(id="grafica_interes")
            ),
    html.Div(className='row', children=[html.H3("Tendencia mensual de la tasa activa en los últimos:"),
 html.Div(children=[dcc.Graph(id="tendencia_interes", style={'display': 'inline-block'}),
                    dcc.Graph(id="tendencia_interes2", style={'display': 'inline-block'}),
                   dcc.Graph(id="tendencia_interes3", style={'display': 'inline-block'}),
                   dcc.Graph(id="tendencia_interes4", style={'display': 'inline-block'})]
            
            )]),
    html.Br(), 
    html.H2("Inflación"),
    html.P("Gráfica:"),
   
    html.Div(dcc.RadioItems(
    id="inflacion_opcion",value="Serie original",
    options=["Serie original", "Comparación anual"]
    )),
    
    html.Br(),
    html.P("Rango de fechas:"), html.Div(  dcc.Dropdown(
        id = 'timeframe_dropdown2', 
        options = [
            {'label': 'Últimos 3 años', 'value': 'Últimos 3 años'},
            {'label': 'Últimos 5 años', 'value': 'Últimos 5 años'},
            {'label': 'Últimos 10 años', 'value': 'Últimos 10 años'}
        ], 
        value='Últimos 5 años',
        clearable=False,
    ), style={"width": "30%"}),
     html.Div( dcc.DatePickerRange(
        id='fechas2',display_format='DD/MM/YYYY',
        min_date_allowed=inflacion["Fecha"].min().strftime('%Y-%m-%d'),
        max_date_allowed=inflacion["Fecha"].max().strftime('%Y-%m-%d'),
        initial_visible_month=inflacion["Fecha"].max().strftime('%Y-%m-%d'),
        start_date=date(2018, 1, 1),
        end_date=inflacion["Fecha"].max().strftime('%Y-%m-%d'),)),
    
     html.Div(dcc.Graph(id="grafica_inflacion")
            ),
    
     html.Br(),
    html.H2("IMAE"),
    html.P("Serie:"),
    html.Div(dcc.Dropdown(id="serie_imae", options=[ 'IMAE',
         'Agricultura, ganadería, silvicultura y pesca',
         'Explotación de minas y canteras',
         'Industrias manufactureras',
         'Suministro de electricidad, agua y saneamiento',
         'Construcción',
         'Comercio y reparación de vehículos',
         'Transporte y almacenamiento',
         'Actividades de alojamiento y de servicio de comidas',
         'Información y comunicaciones',
         'Actividades financieras y de seguros',
         'Actividades inmobiliarias',
         'Actividades profesionales científicas y técnicas',
         'Actividades de servicios administrativos y de apoyo',
         'Administración pública y defensa',
         'Enseñanza',
         'Salud',
         'Otras actividades de servicios'], value="IMAE")),
    html.P("Rango de fechas:"), html.Div(  dcc.Dropdown(
        id = 'timeframe_dropdown3', 
        options = [
            {'label': 'Últimos 3 años', 'value': 'Últimos 3 años'},
            {'label': 'Últimos 5 años', 'value': 'Últimos 5 años'},
            {'label': 'Últimos 10 años', 'value': 'Últimos 10 años'}
        ], 
        value='Últimos 5 años',
        clearable=False,
    ), style={"width": "30%"}),
     html.Div( dcc.DatePickerRange(
        id='fechas3', display_format='DD/MM/YYYY',
        min_date_allowed=imae["Fecha"].min().strftime('%Y-%m-%d'),
        max_date_allowed=imae["Fecha"].max().strftime('%Y-%m-%d'),
        initial_visible_month=imae["Fecha"].max().strftime('%Y-%m-%d'),
        start_date=date(2018, 1, 1),
        end_date=imae["Fecha"].max().strftime('%Y-%m-%d'),)),
    
     html.Div(dcc.Graph(id="grafica_imae")
            ),
    html.Div(dcc.Graph(id="grafica_sectores")
            ),
    html.Br(),
    html.H2("Tipo de cambio"),
    html.P("Rango de fechas:"), html.Div(  dcc.Dropdown(
        id = 'timeframe_dropdown4', 
        options = [
            {'label': 'Últimos 3 años', 'value': 'Últimos 3 años'},
            {'label': 'Últimos 5 años', 'value': 'Últimos 5 años'},
            {'label': 'Últimos 10 años', 'value': 'Últimos 10 años'}
        ], 
        value='Últimos 5 años',
        clearable=False,
    ), style={"width": "30%"}),
     html.Div( dcc.DatePickerRange(
        id='fechas4',display_format='DD/MM/YYYY',
        min_date_allowed=tcm["Fecha2"].min().strftime('%Y-%m-%d'),
        max_date_allowed=tcm["Fecha2"].max().strftime('%Y-%m-%d'),
        initial_visible_month=tcm["Fecha2"].max().strftime('%Y-%m-%d'),
        start_date=date(2018, 1, 1),
        end_date=tcm["Fecha2"].max().strftime('%Y-%m-%d'),)),
    
     html.Div(dcc.Graph(id="grafica_tc")
            ),
    
    html.Br(),
    html.H2("Remesas"),
    html.P("Rango de fechas:"), html.Div(  dcc.Dropdown(
        id = 'timeframe_dropdown5', 
        options = [
            {'label': 'Últimos 3 años', 'value': 'Últimos 3 años'},
            {'label': 'Últimos 5 años', 'value': 'Últimos 5 años'},
            {'label': 'Últimos 10 años', 'value': 'Últimos 10 años'}
        ], 
        value='Últimos 5 años',
        clearable=False,
    ), style={"width": "30%"}),
     html.Div( dcc.DatePickerRange(
        id='fechas5',display_format='DD/MM/YYYY',
        min_date_allowed=remesas["Fecha"].min().strftime('%Y-%m-%d'),
        max_date_allowed=remesas["Fecha"].max().strftime('%Y-%m-%d'),
        initial_visible_month=remesas["Fecha"].max().strftime('%Y-%m-%d'),
        start_date=date(2018, 1, 1),
        end_date=remesas["Fecha"].max().strftime('%Y-%m-%d'),)),
    
     html.Div(dcc.Graph(id="grafica_remesas")
            ),
])


#callback de la funcion
@app.callback(
    [Output('fechas', 'start_date'), # This updates the field start_date in the DatePicker
    Output('fechas', 'end_date')], # This updates the field end_date in the DatePicker
    [Input('timeframe_dropdown', 'value')],
)

def updateDataPicker(dropdown_value):
    if dropdown_value == 'Últimos 3 años':
        return (tasa_final["Fecha"].max()-relativedelta(years=3)).strftime('%Y-%m-%d'), tasa_final["Fecha"].max().strftime('%Y-%m-%d')
    elif dropdown_value == 'Últimos 5 años':
        return (tasa_final["Fecha"].max()-relativedelta(years=5)).strftime('%Y-%m-%d'), tasa_final["Fecha"].max().strftime('%Y-%m-%d')
    else:
        return (tasa_final["Fecha"].max()-relativedelta(years=10)).strftime('%Y-%m-%d'), tasa_final["Fecha"].max().strftime('%Y-%m-%d')


@app.callback(
    [Output("grafica_interes","figure"), Output("tendencia_interes","figure"), Output("tendencia_interes2","figure"),
    Output("tendencia_interes3","figure"), Output("tendencia_interes4","figure")], 
    [Input("moneda","value"), 
    Input("fechas","start_date"),
    Input("fechas","end_date")]
)

#definicion de la funcion

def display_value(moneda, start_date, end_date):
    
    
    int2=tasa_final[(tasa_final["Moneda"]==moneda) & 
                         (tasa_final["Fecha"].dt.date>=(datetime.datetime.strptime(start_date, '%Y-%m-%d').date() )) &
                        (tasa_final["Fecha"].dt.date<=(datetime.datetime.strptime(end_date, '%Y-%m-%d').date() ))]
    
    
    fig= px.line(int2,color="Tipo",x="Fecha",y="Tasa", 
                width=1000,height=500,template="simple_white")
    fig.layout.yaxis.tickformat = ',.2%'
    
    
    int2act=int2[int2.Tipo=="Activa"]
    int2act['Counter'] = range(1, len(int2act) +1)
    
    
    fig4 = go.Figure()
    
    
    regint4=linregress(int2act.iloc[-24:].Counter,int2act.iloc[-24:].Tasa)
    
    fig4.add_trace(go.Indicator(
        value = regint4.slope,number = {'suffix': "%", 'font':{"size":40}},
        title = {"text": "24 meses", 'font':{"size":20}}, delta={'font':{"size":40}},
        domain = {'row': 0, 'column': 0}))
    fig4.layout = go.Layout(
              margin=go.layout.Margin(
                    l=0, #left margin
                    r=0, #right margin
                    b=0, #bottom margin
                    t=0, #top margin
                )
            )
    fig4.update_layout(height=150, width=230, template = {'data' : {'indicator': [{
        'mode' : "delta",
        'delta' : {'reference': 0, 'valueformat':'.3%',}}]
                         }})
    fig5 = go.Figure()
    
    
    regint5=linregress(int2act.iloc[-18:].Counter,int2act.iloc[-18:].Tasa)
    
    fig5.add_trace(go.Indicator(
        value = regint5.slope,number = {'suffix': "%", 'font':{"size":40}},
        title = {"text": "18 meses", 'font':{"size":20}},  delta={'font':{"size":40}},
        domain = {'row': 0, 'column': 0}))
    fig5.layout = go.Layout(
              margin=go.layout.Margin(
                    l=0, #left margin
                    r=0, #right margin
                    b=0, #bottom margin
                    t=0, #top margin
                )
            )
    fig5.update_layout(height=150, width=230, template = {'data' : {'indicator': [{
        'mode' : "delta",
        'delta' : {'reference': 0, 'valueformat':'.3%'}}]
                         }})
    fig2 = go.Figure()
    
    
    regint=linregress(int2act.iloc[-12:].Counter,int2act.iloc[-12:].Tasa)
    
    fig2.add_trace(go.Indicator(
        value = regint.slope,number = {'suffix': "%", 'font':{"size":40}},
        title = {"text": "12 meses", 'font':{"size":20}},  delta={'font':{"size":40}},
        domain = {'row': 0, 'column': 0}))
    fig2.layout = go.Layout(
              margin=go.layout.Margin(
                    l=0, #left margin
                    r=0, #right margin
                    b=0, #bottom margin
                    t=0, #top margin
                )
            )

    
    fig2.update_layout(height=150, width=230, template = {'data' : {'indicator': [{
        'mode' : "delta",
        'delta' : {'reference': 0, 'valueformat':'.3%'}}]
                         }})
    fig3 = go.Figure()
    
    regint2=linregress(int2act.iloc[-6:].Counter,int2act.iloc[-6:].Tasa)
    
    fig3.add_trace(go.Indicator(
        value = regint2.slope,number = {'suffix': "%", 'font':{"size":40}},
        delta={'font':{"size":40}}, title = {"text": "6 meses", 'font':{"size":20}}, 
        domain = {'row': 0, 'column': 0}))
    fig3.layout = go.Layout(
              margin=go.layout.Margin(
                    l=0, #left margin
                    r=0, #right margin
                    b=0, #bottom margin
                    t=0, #top margin
                )
            )
    
    fig3.update_layout(height=150, width=230, template = {'data' : {'indicator': [{
        'mode' : "delta",
        'delta' : {'reference': 0, 'valueformat':'.3%'}}]
                         }})
    
    #tabla
    return fig, fig4,fig5,fig2, fig3

@app.callback(
    [Output('fechas2', 'start_date'), # This updates the field start_date in the DatePicker
    Output('fechas2', 'end_date')], # This updates the field end_date in the DatePicker
    [Input('timeframe_dropdown2', 'value')],
)

def updateDataPicker(dropdown_value):
    if dropdown_value == 'Últimos 3 años':
        return (inflacion["Fecha"].max()-relativedelta(years=3)).strftime('%Y-%m-%d'), inflacion["Fecha"].max().strftime('%Y-%m-%d')
    elif dropdown_value == 'Últimos 5 años':
        return (inflacion["Fecha"].max()-relativedelta(years=5)).strftime('%Y-%m-%d'), inflacion["Fecha"].max().strftime('%Y-%m-%d')
    else:
        return (inflacion["Fecha"].max()-relativedelta(years=10)).strftime('%Y-%m-%d'), inflacion["Fecha"].max().strftime('%Y-%m-%d')



@app.callback(
    Output("grafica_inflacion","figure"),
    [Input("inflacion_opcion","value"), 
    Input("fechas2","start_date"),
    Input("fechas2","end_date")]
)

#definicion de la funcion

def display_value(opcion, start_date, end_date):
    
    
    inf2=inflacion[(inflacion["Fecha"].dt.date>=(datetime.datetime.strptime(start_date, '%Y-%m-%d').date() )) &
                        (inflacion["Fecha"].dt.date<=(datetime.datetime.strptime(end_date, '%Y-%m-%d').date() ))]
    
    
   
    
    if opcion=="Serie original":
        fig=px.line(inf2, x="Fecha", y="Inflación", 
                width=1000,height=500, template="simple_white")
        fig.add_hline(y=0.03, line_dash="dash", line_color="red",opacity=1, line_width=2)
        fig.add_hline(y=0.05, line_dash="dash", line_color="red",opacity=1, line_width=2)
        fig.layout.yaxis.tickformat = ',.2%'
    else: 
        fig=px.line(inf2, x="Mes", y="Inflación", color="Año", markers=True, 
                width=1000,height=500, template="simple_white")
        fig.add_hline(y=0.03, line_dash="dash", line_color="red",opacity=1, line_width=2)
        fig.add_hline(y=0.05, line_dash="dash", line_color="red",opacity=1, line_width=2)
        fig.layout.yaxis.tickformat = ',.2%'
        fig.update_layout(legend_title="", legend= dict(
                orientation="h", y=-.2
                ))
    #tabla
    return fig

@app.callback(
    [Output('fechas3', 'start_date'), # This updates the field start_date in the DatePicker
    Output('fechas3', 'end_date')], # This updates the field end_date in the DatePicker
    [Input('timeframe_dropdown3', 'value')],
)

def updateDataPicker(dropdown_value):
    if dropdown_value == 'Últimos 3 años':
        return (imae["Fecha"].max()-relativedelta(years=3)).strftime('%Y-%m-%d'), imae["Fecha"].max().strftime('%Y-%m-%d')
    elif dropdown_value == 'Últimos 5 años':
        return (imae["Fecha"].max()-relativedelta(years=5)).strftime('%Y-%m-%d'), imae["Fecha"].max().strftime('%Y-%m-%d')
    else:
        return (imae["Fecha"].max()-relativedelta(years=10)).strftime('%Y-%m-%d'), imae["Fecha"].max().strftime('%Y-%m-%d')




@app.callback(
    [Output("grafica_imae","figure"),Output("grafica_sectores","figure")],
    [Input("serie_imae", "value"),Input("fechas3","start_date"),
    Input("fechas3","end_date")]
)

#definicion de la funcion

def display_value(serie, start_date, end_date):
    
    
    imae2=imae[(imae["Fecha"].dt.date>=(datetime.datetime.strptime(start_date, '%Y-%m-%d').date() )) &
                        (imae["Fecha"].dt.date<=(datetime.datetime.strptime(end_date, '%Y-%m-%d').date() ))]
    
    imae2 = imae2[imae2[serie].notna()]
    imae2['Counter'] = range(1, len(imae2) +1)
    
    regresion=linregress(imae2.Counter,imae2[serie])
    imae2["Predicted1"]=regresion.intercept+regresion.slope*imae2["Counter"]
    imae2["Residuals"]=imae2[serie]-imae2["Predicted1"]
    imae2['Estacionalidad'] = imae2.groupby('Mes')['Residuals'].transform('mean')
    imae2['Pronosticado']=imae2["Predicted1"]+imae2["Estacionalidad"]
    imae2["Error2"]=imae2[serie]-imae2["Pronosticado"]

    imae2["Rango"]=abs(imae2.Error2.diff())
    std=imae2.Rango.mean()*2.66/3
    imae2["-3 sigma"]=imae2["Pronosticado"]+std*-3
    imae2["-2 sigma"]=imae2["Pronosticado"]+std*-2
    imae2["-1 sigma"]=imae2["Pronosticado"]+std*-1
    imae2["1 sigma"]=imae2["Pronosticado"]+std*1
    imae2["2 sigma"]=imae2["Pronosticado"]+std*2
    imae2["3 sigma"]=imae2["Pronosticado"]+std*3
    fig=px.line(imae2,width=1000,height=500, template="simple_white",labels={
                     "value": serie,
                     "variable": "Serie"
                 },x="Fecha", y=[serie,"Pronosticado", "-3 sigma","-2 sigma","-1 sigma", "3 sigma","2 sigma","1 sigma"], color_discrete_map={'-3 sigma': 'red', 
                                                   '3 sigma': 'red', '-2 sigma': 'orange', '2 sigma': 'orange',
                                                    '1 sigma': 'yellow', '-1 sigma': 'yellow', serie:"blue", "Pronosticado":"purple"}).update_traces(
    selector={"name": "-3 sigma"}, 
    line={"dash": "dot"}).update_traces(
    selector={"name": "3 sigma"}, 
    line={"dash": "dot"}).update_traces(
    selector={"name": "-2 sigma"}, 
    line={"dash": "dot"}).update_traces(
    selector={"name": "2 sigma"}, 
    line={"dash": "dot"}).update_traces(
    selector={"name": "-1 sigma"}, 
    line={"dash": "dot"}).update_traces(
    selector={"name": "1 sigma"}, 
    line={"dash": "dot"})
    fig.layout.yaxis.tickformat = ',.2%'
    fig.update_layout(legend_title="", legend= dict(
    orientation="h", y=-.2
        ))
    
    sectores=imae2[["Fecha", 'Agricultura, ganadería, silvicultura y pesca',
         'Explotación de minas y canteras',
         'Industrias manufactureras',
         'Suministro de electricidad, agua y saneamiento',
         'Construcción',
         'Comercio y reparación de vehículos',
         'Transporte y almacenamiento',
         'Actividades de alojamiento y de servicio de comidas',
         'Información y comunicaciones',
         'Actividades financieras y de seguros',
         'Actividades inmobiliarias',
         'Actividades profesionales científicas y técnicas',
         'Actividades de servicios administrativos y de apoyo',
         'Administración pública y defensa',
         'Enseñanza',
         'Salud',
         'Otras actividades de servicios']]
    sectores=sectores[sectores["Agricultura, ganadería, silvicultura y pesca"].notna()]
    fecha_sectores=sectores.iloc[-1:,:]["Fecha"].item().strftime("%B %Y")
    sectores=sectores.iloc[-1:,1:]
    sectores=np.transpose(sectores)
    sectores=sectores.rename(columns={sectores.columns[0]: 'Variación interanual'})
    sectores=sectores.sort_values(by=["Variación interanual"], ascending=False)
    sectores["Color"] = np.where(sectores["Variación interanual"]<0, 'red', 'green')
    fig2=px.bar(sectores, x="Variación interanual", y=sectores.index,width=1000,height=500, template="simple_white", 
                labels={
                     "index": "Sector"},
                title=f"Variación interanual a {fecha_sectores} por sector").update_traces(marker_color=sectores["Color"])
    fig2.layout.xaxis.tickformat = ',.2%'
    return fig,fig2

@app.callback(
    [Output('fechas4', 'start_date'), # This updates the field start_date in the DatePicker
    Output('fechas4', 'end_date')], # This updates the field end_date in the DatePicker
    [Input('timeframe_dropdown4', 'value')],
)

def updateDataPicker(dropdown_value):
    if dropdown_value == 'Últimos 3 años':
        return (tcm["Fecha2"].max()-relativedelta(years=3)).strftime('%Y-%m-%d'), tcm["Fecha2"].max().strftime('%Y-%m-%d')
    elif dropdown_value == 'Últimos 5 años':
        return (tcm["Fecha2"].max()-relativedelta(years=5)).strftime('%Y-%m-%d'), tcm["Fecha2"].max().strftime('%Y-%m-%d')
    else:
        return (tcm["Fecha2"].max()-relativedelta(years=10)).strftime('%Y-%m-%d'), tcm["Fecha2"].max().strftime('%Y-%m-%d')





@app.callback(
    Output("grafica_tc","figure"),
    [Input("fechas4","start_date"),
    Input("fechas4","end_date")]
)

#definicion de la funcion

def display_value(start_date, end_date):
    
    
    tcm2=tcm[(tcm["Fecha2"].dt.date>=(datetime.datetime.strptime(start_date, '%Y-%m-%d').date() )) &
                        (tcm["Fecha2"].dt.date<=(datetime.datetime.strptime(end_date, '%Y-%m-%d').date() ))]
    
    tcm2['Counter'] = range(1, len(tcm2) +1)

    regresiontc=linregress(tcm2.Counter,tcm2["Tipo de cambio"])
    tcm2["Predicted1"]=regresiontc.intercept+regresiontc.slope*tcm2["Counter"]
    tcm2["Residuals"]=tcm2["Tipo de cambio"]-tcm2["Predicted1"]
    tcm2['Estacionalidad'] = tcm2.groupby('Mes')['Residuals'].transform('mean')
    tcm2['Pronosticado']=tcm2["Predicted1"]+tcm2["Estacionalidad"]
    tcm2["Error2"]=tcm2["Tipo de cambio"]-tcm2["Pronosticado"]

    tcm2["Rango"]=abs(tcm2.Error2.diff())
    stdtc=tcm2.Rango.mean()*2.66/3
    tcm2["-3 sigma"]=tcm2["Pronosticado"]+stdtc*-3
    tcm2["-2 sigma"]=tcm2["Pronosticado"]+stdtc*-2
    tcm2["-1 sigma"]=tcm2["Pronosticado"]+stdtc*-1
    tcm2["1 sigma"]=tcm2["Pronosticado"]+stdtc*1
    tcm2["2 sigma"]=tcm2["Pronosticado"]+stdtc*2
    tcm2["3 sigma"]=tcm2["Pronosticado"]+stdtc*3
    fig=px.line(tcm2,width=1000,height=500, template="simple_white",labels={
                     "value": "Tipo de cambio",
                     "variable": "Serie",
        "Fecha2":"Fecha"
                 },x="Fecha2", y=["Tipo de cambio","Pronosticado", "-3 sigma","-2 sigma","-1 sigma", "3 sigma","2 sigma","1 sigma"], color_discrete_map={'-3 sigma': 'red', 
                                                   '3 sigma': 'red', '-2 sigma': 'orange', '2 sigma': 'orange',
                                                    '1 sigma': 'yellow', '-1 sigma': 'yellow', "Tipo de cambio":"blue", "Pronosticado":"purple"}).update_traces(
    selector={"name": "-3 sigma"}, 
    line={"dash": "dot"}).update_traces(
    selector={"name": "3 sigma"}, 
    line={"dash": "dot"}).update_traces(
    selector={"name": "-2 sigma"}, 
    line={"dash": "dot"}).update_traces(
    selector={"name": "2 sigma"}, 
    line={"dash": "dot"}).update_traces(
    selector={"name": "-1 sigma"}, 
    line={"dash": "dot"}).update_traces(
    selector={"name": "1 sigma"}, 
    line={"dash": "dot"})
    fig.update_layout(legend_title="", legend= dict(
    orientation="h", y=-.2
        ))
    #tabla
    return fig

@app.callback(
    [Output('fechas5', 'start_date'), # This updates the field start_date in the DatePicker
    Output('fechas5', 'end_date')], # This updates the field end_date in the DatePicker
    [Input('timeframe_dropdown5', 'value')],
)

def updateDataPicker(dropdown_value):
    if dropdown_value == 'Últimos 3 años':
        return (remesas["Fecha"].max()-relativedelta(years=3)).strftime('%Y-%m-%d'), remesas["Fecha"].max().strftime('%Y-%m-%d')
    elif dropdown_value == 'Últimos 5 años':
        return (remesas["Fecha"].max()-relativedelta(years=5)).strftime('%Y-%m-%d'), remesas["Fecha"].max().strftime('%Y-%m-%d')
    else:
        return (remesas["Fecha"].max()-relativedelta(years=10)).strftime('%Y-%m-%d'), remesas["Fecha"].max().strftime('%Y-%m-%d')





@app.callback(
    Output("grafica_remesas","figure"),
    [Input("fechas5","start_date"),
    Input("fechas5","end_date")]
)

#definicion de la funcion

def display_value(start_date, end_date):
    
    
    remesas2=remesas[(remesas["Fecha"].dt.date>=(datetime.datetime.strptime(start_date, '%Y-%m-%d').date() )) &
                        (remesas["Fecha"].dt.date<=(datetime.datetime.strptime(end_date, '%Y-%m-%d').date() ))]
    
    remesas2['Counter'] = range(1, len(remesas2) +1)

    regresionrem=linregress(remesas2.Counter,remesas2.Remesas)
    remesas2["Predicted1"]=regresionrem.intercept+regresionrem.slope*remesas2["Counter"]
    remesas2["Residuals"]=remesas2["Remesas"]-remesas2["Predicted1"]
    remesas2['Estacionalidad'] = remesas2.groupby('Mes')['Residuals'].transform('mean')
    remesas2['Pronosticado']=remesas2["Predicted1"]+remesas2["Estacionalidad"]
    remesas2["Error2"]=remesas2["Remesas"]-remesas2["Pronosticado"]

    remesas2["Rango"]=abs(remesas2.Error2.diff())
    stdrem=remesas2.Rango.mean()*2.66/3
    remesas2["-3 sigma"]=remesas2["Pronosticado"]+stdrem*-3
    remesas2["-2 sigma"]=remesas2["Pronosticado"]+stdrem*-2
    remesas2["-1 sigma"]=remesas2["Pronosticado"]+stdrem*-1
    remesas2["1 sigma"]=remesas2["Pronosticado"]+stdrem*1
    remesas2["2 sigma"]=remesas2["Pronosticado"]+stdrem*2
    remesas2["3 sigma"]=remesas2["Pronosticado"]+stdrem*3
    fig=px.line(remesas2,width=1000,height=500, template="simple_white",labels={
                     "value": "Remesas",
                     "variable": "Serie"
                 },x="Fecha", y=["Remesas","Pronosticado", "-3 sigma","-2 sigma","-1 sigma", "3 sigma","2 sigma","1 sigma"], color_discrete_map={'-3 sigma': 'red', 
                                                   '3 sigma': 'red', '-2 sigma': 'orange', '2 sigma': 'orange',
                                                    '1 sigma': 'yellow', '-1 sigma': 'yellow', "Remesas":"blue", "Pronosticado":"purple"}).update_traces(
    selector={"name": "-3 sigma"}, 
    line={"dash": "dot"}).update_traces(
    selector={"name": "3 sigma"}, 
    line={"dash": "dot"}).update_traces(
    selector={"name": "-2 sigma"}, 
    line={"dash": "dot"}).update_traces(
    selector={"name": "2 sigma"}, 
    line={"dash": "dot"}).update_traces(
    selector={"name": "-1 sigma"}, 
    line={"dash": "dot"}).update_traces(
    selector={"name": "1 sigma"}, 
    line={"dash": "dot"})
    fig.update_layout(legend_title="", legend= dict(
    orientation="h", y=-.2
        ))
    #tabla
    fig.update_layout(yaxis_tickprefix = '$')
    return fig



#setear server y correr
app.run_server(debug=False,port=10000, host='0.0.0.0')
    
