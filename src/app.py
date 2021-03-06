import dash
import data

# Define the stylesheet
external_stylesheets = [
    "./assets/stylesheets/stylesheet.css",
    "./assets/stylesheets/buttons.css",
    "./assets/stylesheets/data-table.css",
    "./assets/stylesheets/date-range.css",
    "./assets/stylesheets/navigation.css",
    "./assets/stylesheets/select-menu.css",
    "./assets/stylesheets/sliders.css",
    "./assets/stylesheets/spinners.css"
]

# Define the dash app
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True
)

app.title="Cheapeake Bay Watershed Analysis"

# Load our dataframes
huc_gaps_df = data.load_huc_gaps()
station_gaps_df = data.load_station_gaps()
stations_df = data.load_stations()
mapbox_token = "pk.eyJ1IjoiYmZhbGxpbiIsImEiOiJjanQ2ZjU3dWUwZ2dyM3lvNjA1ZGpuYmUyIn0.Ylu23fEbZoSmCuP-ekyIAA"