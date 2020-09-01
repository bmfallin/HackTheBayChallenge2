import dash_core_components as dcc
import dash_html_components as html


layout = [

    html.Div(
        id="homepage-banner",
        className="lg-12 md-12 sm-12 xs-12",
        children=[
            html.Div(
                id="homepage-banner-box",
                children=[
                    html.Div(
                        children=[
                            html.H1("Hack The Bay Challenge 2"),
                            html.H4("PAX River Team")
                        ]
                    )
                ]
            )
        ]
    ),
    html.Div(
        className="tile lg-12 md-12 sm-12 xs-12",
        children=[
            html.H2("Description"),
            html.P("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis efficitur mi quis massa vulputate, in pretium arcu semper. Nullam aliquam ornare nisi sit amet ultricies. Vestibulum lobortis erat vel eros aliquam, nec accumsan magna dignissim. Donec vulputate augue eu massa facilisis consectetur. Vestibulum pulvinar dui purus, vel sollicitudin tellus scelerisque non. Mauris tincidunt mauris ut risus pretium, ac dignissim felis viverra. Maecenas dolor dolor, faucibus lacinia sem vitae, commodo venenatis velit. Sed id ipsum tempus, ornare nibh sit amet, elementum arcu. In consequat lectus eu mi molestie consequat. Quisque dapibus sodales sem, vel aliquet leo condimentum in. Nulla facilisi. Maecenas a est venenatis, tristique elit vitae, interdum risus. Morbi dolor turpis, dignissim a quam sit amet, faucibus fringilla leo. Nulla ultrices et urna at lobortis."),
            html.P("Sed vel tortor sem. Phasellus dictum laoreet quam in porttitor. Proin tellus dui, dapibus quis quam quis, consequat tristique nulla. Aliquam fermentum rutrum ullamcorper. Donec iaculis ante et rutrum euismod. Suspendisse bibendum ultricies pharetra. Aliquam facilisis, tortor ut lobortis vulputate, turpis urna facilisis ante, in fermentum risus nulla in mauris. Morbi gravida rhoncus pharetra. Ut blandit, purus vel posuere maximus, enim tortor porta dui, at molestie eros eros eu arcu. Vivamus ultricies felis ac ullamcorper tincidunt. Cras in velit eu tortor pellentesque convallis. Vivamus cursus felis quam. Ut nunc ex, gravida a scelerisque convallis, fermentum at nisi. Vestibulum rutrum mattis fermentum. Etiam quis leo elit. Aenean eu nunc eu sem placerat condimentum.")                    
        ]
    ),
    html.Div(
        className="container tile lg-12 md-12 sm-12 xs-12",
        children=[
            html.H2(
                className="lg-12 md-12 sm-12 xs-12",
                children="Contributors"
            ),

            html.Div(
                className="contributor lg-4 md-12 sm-12 xs-12",
                children=[
                    html.Img(src="../assets/images/brandon.png"),
                    html.H4("Brandon Fallin"),
                    html.P("Description")
                ]
            ),
            html.Div(
                className="contributor lg-4 md-12 sm-12 xs-12",
                children=[
                    html.Img(src="../assets/images/lisa.png"),
                    html.H4("Lisa Jacobson"),
                    html.P("Description")
                ]
            ),
            html.Div(
                className="contributor lg-4 md-12 sm-12 xs-12",
                children=[
                    html.Img(src="../assets/images/jon.png"),
                    html.H4("Jon Anderson"),
                    html.P("Description")
                ]
            ),
            html.A(
                className="attribution",
                href="https://www.vecteezy.com/free-vector/people-smile",
                children="Avatars images by Vecteezy"
            )
        ]
    ),
    html.Div(
        className="tile lg-6 md-12 sm-12 xs-12",
        children=[
            html.H2("Technologies"),
            html.Ul(
                children=[
                    html.Li("Python"),
                    html.Li("Numpy"),
                    html.Li("Pandas"),
                    html.Li("GeoPandas"),
                    html.Li("Plotly"),
                    html.Li("Dash")
                ]
            )
        ]
    ),
    html.Div(
        className="tile lg-6 md-12 sm-12 xs-12",
        children=[
            html.H2("Data Sources"),

            html.Div(
                className="data-source-citation",
                children=[
                    html.H4("CMC and CBP Water Sample Collections:"),
                    html.P(
                        className="inline",
                        children="HackTheBay Organizers. (2020, August)."),
                    html.P(
                        className="italic inline",
                        children="Water_Final.csv"),
                    html.Br(),
                    html.P(
                        className="inline indent",
                        children="[CMC and CBP Water Sample Collections]"),
                    html.Br(),
                    html.A(
                        className="indent",
                        href="https://drive.google.com/file/d/1M4ELFR6cS32EvxHlRjGNr9TYXN84O2ce/view",
                        children="https://drive.google.com/file/d/1M4ELFR6cS32EvxHlRjGNr9TYXN84O2ce/view"
                    )
                ]
            ),

            html.Div(
                className="data-source-citation",
                children=[
                    html.H4("CBP Benthic sample collections:"),
                    html.P(
                        className="inline",
                        children="HackTheBay Organizers. (2020, August)."),
                    html.P(
                        className="italic inline",
                        children="CBP_Benthic.csv"),
                    html.Br(),
                    html.P(
                        className="inline indent",
                        children="[CBP Benthic Samples]"),
                    html.Br(),
                    html.A(
                        className="indent",
                        href="https://drive.google.com/drive/folders/1EwdmR1KjpmlOZinTZk-vxo7KlSbB-anz",
                        children="https://drive.google.com/drive/folders/1EwdmR1KjpmlOZinTZk-vxo7KlSbB-anz"
                    )
                ]
            ),

            html.Div(
                className="data-source-citation",
                children=[
                    html.H4("CMC Benthic sample collections:"),
                    html.P(
                        className="inline",
                        children="HackTheBay Organizers. (2020, August)."),
                    html.P(
                        className="italic inline",
                        children="CMC_Benthic_Data.xlsx"),
                    html.Br(),
                    html.P(
                        className="inline indent",
                        children="[CMC Benthic Samples]"),
                    html.Br(),
                    html.A(
                        className="indent",
                        href="https://drive.google.com/drive/folders/1EwdmR1KjpmlOZinTZk-vxo7KlSbB-anz",
                        children="https://drive.google.com/drive/folders/1EwdmR1KjpmlOZinTZk-vxo7KlSbB-anz"
                    )
                ]
            ),

            html.Div(
                className="data-source-citation",
                children=[
                    html.H4("HUC12 Boundaries:"),
                    html.P(
                        className="inline",
                        children="HackTheBay Organizers. (2020, August)."),
                    html.P(
                        className="italic inline",
                        children="wbdhu12_a_us_september2019.gdb"),
                    html.Br(),
                    html.P(
                        className="inline indent",
                        children="[HUC12 Watershed Boundaries]"),
                    html.Br(),
                    html.A(
                        className="indent",
                        href="https://nrcs.app.box.com/v/huc/file/532373547877",
                        children="https://nrcs.app.box.com/v/huc/file/532373547877"
                    )
                ]
            ),

            html.Div(
                className="data-source-citation",
                children=[
                    html.H4("HUC12 Land Cover:"),
                    html.P(
                        className="inline",
                        children="Environmental Protection Agency. (2019, October)."),
                    html.P(
                        className="italic inline",
                        children="CONUS_metrics_Oct2019_FGDB.zip"),
                    html.Br(),
                    html.P(
                        className="inline indent",
                        children="[Continental United States metrics]. United States Environmental Protection Agency."),
                    html.Br(),
                    html.A(
                        className="indent",
                        href="https://edg.epa.gov/data/public/ORD/EnviroAtlas/National/ConterminousUS/",
                        children="https://edg.epa.gov/data/public/ORD/EnviroAtlas/National/ConterminousUS/"
                    )
                ]
            )
        ]
    )
]