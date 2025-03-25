import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import statsmodels.api as sm
from analysis.clean_data import load_and_clean_data
from analysis.summary_stats import run_ols_regression

# Load the data
df = load_and_clean_data()

# Initialize the app
app = dash.Dash(__name__)
app.title = "Tipping Trends"

# Layout
app.layout = html.Div([
    html.H1("Tipping Trends Dashboard", style={"textAlign": "center"}),

    html.Div([
        html.Label("Filter by Day"),
        dcc.Dropdown(
            id="day-filter",
            options=[{"label": day, "value": day} for day in df["day"].unique()],
            value=None,
            placeholder="Select a day",
            multi=False
        ),

        html.Label("Filter by Gender"),
        dcc.Dropdown(
            id="gender-filter",
            options=[{"label": gender, "value": gender} for gender in df["gender"].unique()],
            value=None,
            placeholder="Select gender",
            multi=False
        ),

        html.Label("Filter by Smoker"),
        dcc.Dropdown(
            id="smoker-filter",
            options=[{"label": status, "value": status} for status in df["smoker"].unique()],
            value=None,
            placeholder="Smoker or not?",
            multi=False
        ),
    ], style={"width": "30%", "float": "left", "padding": "20px"}),

        html.Label("Show Regression Line"),
        dcc.Checklist(
            id="show-regression",
            options=[{"label": "Enable", "value": "on"}],
            value=[],  # default is ON
            style={"marginBottom": "20px"}
        ),

        html.Label("Y-Axis:"),
        dcc.RadioItems(
            id="y-axis-toggle",
            options=[
            {"label": "Tip Amount ($)", "value": "tip"},
            {"label": "Tip Percentage (%)", "value": "tip_percent"}
        ],
        value="tip",  # Default to raw tip amount
        labelStyle={"display": "block"},
        style={"marginBottom": "20px"}
    ),


    html.Div([
        dcc.Graph(id="tip-scatter"),

        html.Div(id="regression-output", style={
            "marginTop": "40px",
            "padding": "15px",
            "borderTop": "1px solid #ccc"
        })
    ], style={"width": "70%", "float": "right", "padding": "20px"})
])


# Callback for interactivity
@app.callback(
    [Output("tip-scatter", "figure"),
     Output("regression-output", "children")],
    [Input("day-filter", "value"),
     Input("gender-filter", "value"),
     Input("smoker-filter", "value"),
     Input("show-regression", "value"),
     Input("y-axis-toggle", "value")]
)
def update_graph(day, gender, smoker, show_regression, y_axis):
    filtered_df = df.copy()

    if day:
        filtered_df = filtered_df[filtered_df["day"] == day]
    if gender:
        filtered_df = filtered_df[filtered_df["gender"] == gender]
    if smoker:
        filtered_df = filtered_df[filtered_df["smoker"] == smoker]

    # Run OLS regression
    model = run_ols_regression(filtered_df, y_var=y_axis)
    params = model.params.round(2)
    r2 = round(model.rsquared, 3)

    regression_output = html.Div([
        html.H4(f"OLS Regression Summary: {y_axis} ~ Total Bill + Party Size"),
        html.P(f"Intercept: {params['const']}"),
        html.P(f"Total Bill Coefficient: {params['total_bill']}"),
        html.P(f"Party Size Coefficient: {params['size']}"),
        html.P(f"R-squared: {r2}")
    ])

    # Scatter plot
    y_label = "Tip (%)" if y_axis == "tip_percent" else "Tip ($)"
    fig = px.scatter(
        filtered_df,
        x="total_bill",
        y=y_axis,
        color="time",
        title=f"{y_label} vs. Total Bill"
    )

    # Regression Line (if enabled)
    if "on" in show_regression:
        sorted_df = filtered_df.sort_values(by="total_bill")
        X_pred = sm.add_constant(sorted_df[["total_bill", "size"]])
        y_pred = model.predict(X_pred)

        fig.add_scatter(
            x=sorted_df["total_bill"],
            y=y_pred,
            mode="lines",
            name="Regression Line",
            line=dict(color="black", dash="dash")
        )

    return fig, regression_output




if __name__ == "__main__":
    app.run_server(debug=True)
