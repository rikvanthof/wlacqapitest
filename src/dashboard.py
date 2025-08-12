from dash import Dash, html, dcc
import pandas as pd
from .utils import get_db_engine
import plotly.express as px

app = Dash(__name__)
engine = get_db_engine()
df = pd.read_sql('SELECT * FROM runs', engine)
fig = px.line(df.groupby(['chain_id', 'test_id', 'merchant_description', 'card_description']).agg({'duration_ms': 'mean'}).reset_index(),
              x='chain_id', y='duration_ms', color='merchant_description', line_dash='card_description',
              title='Average Response Time per Chain, Test, Merchant, and Card')

app.layout = html.Div([
    html.H1('E2E Payment Test Dashboard'),
    html.H2('Results Table'),
    dcc.Graph(figure=fig),
    html.Table([
        html.Tr([html.Th(col) for col in df.columns])] +
        [html.Tr([html.Td(df.iloc[i][col]) for col in df.columns]) for i in range(min(10, len(df)))]
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)