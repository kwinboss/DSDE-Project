import os
import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px
import plotly.graph_objs as go

st.set_page_config(
    page_title="10 Year Academic Insights",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load external CSS
def load_css(file_path="/Users/bossbanner/Desktop/Project/given data/assets/directory/styles.css"):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load datasets function
def load_combined_dataset(base_path='.'):
    """Load and merge CSV files for multiple years."""
    pattern = 'cluster_final_prepared_{}_data.csv'
    dataframes = []

    for year in range(2013, 2024):
        filepath = os.path.join(base_path, pattern.format(year))
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath)
                df['year'] = year
                dataframes.append(df)
            except Exception as e:
                st.sidebar.warning(f"Error loading {filepath}: {e}")
    
    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
        combined_df['publication_date'] = pd.to_datetime(combined_df['publication_date'], errors='coerce')
        combined_df = combined_df.dropna(subset=['publication_date'])
        columns_to_fill = ['title', 'author_name', 'affiliation', 'city', 'country']
        for col in columns_to_fill:
            combined_df[col] = combined_df[col].fillna('Unknown')
        return combined_df
    else:
        st.error("No data files could be loaded!")
        return pd.DataFrame()

def rgba_to_plotly(rgba):
    return f'rgba({rgba[0]},{rgba[1]},{rgba[2]},{rgba[3]/255})'

# Apply the CSS
load_css()

## Main Dashboard
df = load_combined_dataset()


# Streamlit App Title
st.markdown("<h1>10 Year Academic Insights</h1>", unsafe_allow_html=True)

st.markdown("<hr style='border: 0; height: 0.5px; background: #333; margin: 2px 0; color: #7f8c8d;'>", unsafe_allow_html=True)

# Add subtle description
st.markdown("""
<div class='subtle-description'>
 Scholarly Research Dataset: A Comprehensive Overview from 2013 to 2023
</div>
""", unsafe_allow_html=True)

# Define a color mapping for each cluster (same as before)
color_map = {
    -1: [80, 80, 80, 160],  # Dark Gray for outliers
    0: [255, 0, 0, 160],  # Red
    1: [0, 128, 0, 160],  # Dark Green
    2: [0, 0, 139, 160],  # Dark Blue
    3: [221, 160, 0, 160],  # Yellow
    4: [0, 139, 139, 160],  # Dark Cyan
    5: [139, 0, 255, 160],  # Dark Magenta
    6: [105, 105, 105, 160],  # Dark Gray
    7: [139, 0, 0, 160],  # Dark Maroon
    8: [0, 100, 0, 160],  # Dark Olive Green
    9: [0, 0, 128, 160],  # Dark Navy
    10: [255, 140, 0, 160],  # Dark Orange
    11: [255, 20, 147, 160],  # Deep Pink
    12: [255, 69, 0, 160],  # Red-Orange
    13: [34, 139, 34, 160],  # Forest Green
    14: [70, 130, 180, 160],  # Steel Blue
    15: [186, 85, 211, 160],  # Medium Orchid
    16: [0, 206, 209, 160],  # Dark Turquoise
    17: [255, 69, 0, 160],  # Red-Orange
    18: [255, 228, 181, 160],  # Moccasin (lighter)
    19: [255, 222, 173, 160],  # Navajo White
    20: [240, 128, 128, 160],  # Light Coral
    21: [186, 85, 211, 160],  # Medium Orchid
    22: [218, 112, 214, 160],  # Orchid
    23: [255, 192, 203, 160],  # Pink
    24: [144, 238, 144, 160],  # Light Green
    25: [139, 69, 19, 160],  # Darker Light Green
}


# Sidebar for page selection
st.sidebar.markdown("## 🧭 Navigation")
page = st.sidebar.radio("Select Analysis View", ["Cluster Analysis", "Geographic Analysis", "Author and Affiliation Insights", "Topic/Keyword Filter"])

# Sidebar Filters for Year
st.sidebar.markdown("## 🔍 Filters")
selected_year = st.sidebar.slider("Select Year", int(df['year'].min()), int(df['year'].max()), 2017)

# Prepare the data (year)
df["year"] = pd.to_datetime(df["publication_date"]).dt.year
filtered_df = df[df["year"] == selected_year]

# Conditional (Select Country + Select City)
if page == "Geographic Analysis":
    # Country Selection
    country_options = sorted(df['country'].unique())
    selected_country = st.sidebar.selectbox("Select Country", options=["All"] + list(country_options))
    
    # City Selection
    if selected_country == "All":
        city_options = sorted(df['city'].unique())
    else:
        city_options = sorted(df[df['country'] == selected_country]['city'].unique())
    
    selected_city = st.sidebar.selectbox("Select City", options=["All"] + list(city_options))
else:
    # For other page, we don't show the country or city filters
    selected_country = "All"
    selected_city = "All"

# Map the color for each row based on its cluster
filtered_df["color"] = filtered_df["cluster"].map(color_map)



# Handle different pages in the app
if page == "Cluster Analysis":
    # Clustered Geomap
    st.markdown("## 🌍 Clustered Geomap")
    col1, col2, col3 = st.columns([0.5, 4, 0.5])  # Adjust middle column width
    with col2:
        st.pydeck_chart(pdk.Deck(
        # Your existing pydeck configuration
        map_style="mapbox://styles/mapbox/light-v9",  # Light theme
        initial_view_state=pdk.ViewState(
            latitude=filtered_df["latitude"].mean(),
            longitude=filtered_df["longitude"].mean(),
            zoom=1,
            pitch=4,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=filtered_df,
                get_position="[longitude, latitude]",
                get_fill_color="color",
                get_radius=65000,
                pickable=True,
                opacity=0.7,
            ),
        ],
    ))

    # Cluster Composition Bar Chart
    st.markdown("## 📊 Cluster Composition")

    cluster_counts = filtered_df['cluster'].value_counts().reset_index()
    cluster_counts.columns = ['Cluster', 'Number of Points']

    # Bar chart data
    fig = go.Figure(data=[
        go.Bar(
            x=cluster_counts['Cluster'],
            y=cluster_counts['Number of Points'],
            marker_color=[
                rgba_to_plotly(color_map.get(cluster, [128, 128, 128, 160])) 
                for cluster in cluster_counts['Cluster']
            ],
            hovertemplate='<b>Cluster: %{x}</b><br>Number of Points: %{y}<br><extra></extra>',
            opacity=0.85
        )
    ])

    # Layout update
    fig.update_layout(
        xaxis=dict(
            title='Cluster ID',
            titlefont=dict(size=14, color="#2c3e50"),
            tickfont=dict(size=12, color="#34495e"),
            gridcolor="rgba(200,200,200,0.2)",  # Light gridlines
            zeroline=False
        ),
        yaxis=dict(
            title='Number of Points in Cluster',
            titlefont=dict(size=14, color="#2c3e50"),
            tickfont=dict(size=12, color="#34495e"),
            gridcolor="rgba(200,200,200,0.3)",  # Slightly darker gridlines
            zeroline=False
        ),
        plot_bgcolor="#f4f4f4",  # Background color close to specified
        paper_bgcolor="#f4f4f4",  # Full chart background
        font=dict(family="Arial", size=12, color="#2c3e50"),
        margin=dict(t=20, b=40)  # Adjust top and bottom margins
    )

    # Add annotation for the maximum cluster
    max_cluster = cluster_counts.loc[cluster_counts['Number of Points'].idxmax()]
    fig.add_annotation(
        x=max_cluster['Cluster'],
        y=max_cluster['Number of Points'],
        text=f"Max: {max_cluster['Number of Points']}",
        showarrow=True,
        arrowhead=2,
        font=dict(size=12, color="#ffffff"),
        bordercolor="#3498db",
        borderwidth=2,
        borderpad=4,
        bgcolor="#3498db",  # Blue background for annotation
    )

    # Create columns for layout
    col1, col2, col3 = st.columns([0.5, 4, 0.5])  # Middle column is wider
    with col2:
        st.plotly_chart(fig, use_container_width=True)

    # Add the title below the chart
    with col2:
        st.markdown("<div class='subtle-description'>Cluster Composition Analysis</div>", unsafe_allow_html=True)



elif page == "Geographic Analysis":
    # Filtering logic for data display
    if selected_country == "All":
        city_data = df.dropna(subset=['latitude', 'longitude'])
    else:
        # Filter by country first
        country_filtered_data = df[df['country'] == selected_country]
        
        # Further filter by city if not "All"
        if selected_city == "All":
            city_data = country_filtered_data.dropna(subset=['latitude', 'longitude'])
        else:
            city_data = country_filtered_data[
                (country_filtered_data['city'] == selected_city) & 
                country_filtered_data['latitude'].notna() & 
                country_filtered_data['longitude'].notna()
            ]

    # Research Heatmap
    st.markdown("## 🗺️ Research Heatmap")
    # Layout with columns
    col1, col2, col3 = st.columns([0.5, 4, 0.5])  # Middle column is wider

    with col2:
        
        # Use the full dataset for the heatmap, not filtered by the selected year
        if selected_country == "All":
            heatmap_data = filtered_df.dropna(subset=['latitude', 'longitude'])
        else:
            # Filter by country
            country_filtered_data = filtered_df[filtered_df['country'] == selected_country]

            # Further filter by city if not "All"
            if selected_city == "All":
                heatmap_data = country_filtered_data.dropna(subset=['latitude', 'longitude'])
            else:
                heatmap_data = country_filtered_data[
                    (country_filtered_data['city'] == selected_city) & 
                    country_filtered_data['latitude'].notna() & 
                    country_filtered_data['longitude'].notna()
                ]

        # Check if there's data to plot
        if heatmap_data.empty:
            st.warning(f"No geographic data available for {selected_city} in {selected_country}")
        else:
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9", 
                initial_view_state=pdk.ViewState(
                    latitude=heatmap_data['latitude'].mean(),
                    longitude=heatmap_data['longitude'].mean(),
                    zoom=5 if selected_city != "All" else 3,
                    pitch=50,
                ),
                layers=[
                    pdk.Layer(
                        "HeatmapLayer",
                        data=heatmap_data,
                        get_position="[longitude, latitude]",
                        get_weight=1,
                        radius_pixels=30,
                        opacity=0.7,
                    ),
                ],
            ))

    # Top Research Countries (Bar Chart)
    st.markdown("## 🌐 Top Research Countries")

    # Prepare the data for the bar chart
    country_counts = filtered_df['country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'Number of Publications']

    # Create the bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=country_counts['Country'],
            y=country_counts['Number of Publications'],
            marker=dict(
                color=country_counts['Number of Publications'],  # Use 'Number of Publications' for color scale
                colorscale='Viridis',  # You can use any Plotly colorscale like 'Viridis', 'Cividis', etc.
                showscale=True  # This shows a color scale bar
            ),
            hovertemplate='<b>Country: %{x}</b><br>Number of Publications: %{y}<br><extra></extra>',
            opacity=0.85
        )
    ])

    # Layout update (similar to Cluster Composition)
    fig.update_layout(
        title={
            "text": "",
            "y": 0.95,  # Vertical alignment
            "x": 0.5,   # Horizontal alignment (centered)
            "xanchor": "center",
            "yanchor": "top",
            "font": {"size": 20, "color": "#34495e"}  # Title font color and size
        },
        xaxis=dict(
            title='Country',
            titlefont=dict(size=14, color="#2c3e50"),
            tickfont=dict(size=12, color="#34495e"),
            gridcolor="rgba(200,200,200,0.2)",  # Light gridlines
            zeroline=False
        ),
        yaxis=dict(
            title='Number of Publications',
            titlefont=dict(size=14, color="#2c3e50"),
            tickfont=dict(size=12, color="#34495e"),
            gridcolor="rgba(200,200,200,0.3)",  # Slightly darker gridlines
            zeroline=False
        ),
        plot_bgcolor="#f4f4f4",  # Background color to match app background
        paper_bgcolor="#f4f4f4",  # Full chart background color
        font=dict(family="Arial", size=12, color="#2c3e50"),
        margin=dict(t=20, b=40)  # Adjust margins
    )

    # Add annotation for the maximum country
    max_country = country_counts.loc[country_counts['Number of Publications'].idxmax()]
    fig.add_annotation(
        x=max_country['Country'],
        y=max_country['Number of Publications'],
        text=f"Max: {max_country['Number of Publications']}",
        showarrow=True,
        arrowhead=2,
        font=dict(size=12, color="#ffffff"),
        bordercolor="#3498db",  # Blue border for annotation
        borderwidth=2,
        borderpad=4,
        bgcolor="#3498db",  # Blue background for annotation
    )

    # Create columns for layout
    col1, col2, col3 = st.columns([0.5, 4, 0.5])  # Middle column is wider
    with col2:
        st.plotly_chart(fig, use_container_width=True)

    # Add the title below the chart
    with col2:
        st.markdown("<div class='subtle-description'>Top Research Countries</div>", unsafe_allow_html=True)

    # City-Level Analysis (Table)
    st.markdown("## 📍 City-Level Analysis")
    if selected_country == "All":
        st.info("Please select a specific country to view city-level details.")
    else:
        # Filter table data based on country and city selection
        if selected_city == "All":
            table_data = filtered_df[filtered_df['country'] == selected_country]
        else:
            table_data = filtered_df[(filtered_df['country'] == selected_country) & (filtered_df['city'] == selected_city)]
        
        # Reset index to remove it from display
        table_data = table_data.reset_index(drop=True)
        
        # Style the dataframe
        styled_table = table_data[['author_name', 'affiliation', 'title', 'publication_date']].style.apply(
            lambda x: ['background-color: #f0f2f6' if i % 2 == 0 else '' for i in range(len(x))],
            axis=0
        ).highlight_max(
            subset=['publication_date'], 
            color='#e6f2ff'
        ).set_properties(**{
            'font-size': '12px',
            'border': '1px solid #ddd',
            'text-align': 'left'
        })
    
        # Display the styled dataframe
        st.dataframe(
            styled_table, 
            use_container_width=True,
            hide_index=True
        )
        
        
elif page == "Author and Affiliation Insights":
    st.header("Author and Affiliation Insights")

    # --- Top Authors ---
    st.markdown("## 🏆 Top 10 Authors by Publications")

    # Calculate top authors by number of publications
    top_authors = filtered_df['author_name'].value_counts().head(10).reset_index()
    top_authors.columns = ['Author', 'Number of Publications']

    # Bar chart for top authors
    fig_authors = px.bar(
        top_authors,
        x='Author',
        y='Number of Publications',
        title="Top 10 Authors by Publications",
        color='Number of Publications',
        color_continuous_scale='Blues',
        labels={'Number of Publications': 'Publications'}
    )

    # Customize chart layout
    fig_authors.update_layout(
        title={
            "text": "",
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": {"size": 20, "color": "#34495e"}  # Title font
        },
        xaxis=dict(
            title='Author',
            titlefont=dict(size=14, color="#2c3e50"),
            tickfont=dict(size=12, color="#34495e"),
            gridcolor="rgba(200,200,200,0.2)",  # Light gridlines
            zeroline=False
        ),
        yaxis=dict(
            title='Number of Publications',
            titlefont=dict(size=14, color="#2c3e50"),
            tickfont=dict(size=12, color="#34495e"),
            gridcolor="rgba(200,200,200,0.3)",  # Slightly darker gridlines
            zeroline=False
        ),
        plot_bgcolor="#f4f4f4",  # Background color to match app background
        paper_bgcolor="#f4f4f4",  # Full chart background color
        font=dict(family="Arial", size=12, color="#2c3e50"),
        margin=dict(t=20, b=40)  # Adjust margins
    )
    st.plotly_chart(fig_authors, use_container_width=True)

    # --- Affiliation Analysis ---
    st.markdown("## 🏫 Top 10 Affiliations by Publications")

    # Calculate top affiliations by number of publications
    top_affiliations = filtered_df['affiliation'].value_counts().head(10).reset_index()
    top_affiliations.columns = ['Affiliation', 'Number of Publications']

    # Pie chart for top affiliations
    fig_affiliations = px.pie(
        top_affiliations,
        names='Affiliation',
        values='Number of Publications',
        title="Top 10 Affiliations by Publications",
        color_discrete_sequence=px.colors.sequential.RdBu
    )

    # Customize the layout for Affiliation Pie chart
    fig_affiliations.update_layout(
        title={
            "text": "",
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": {"size": 20, "color": "#34495e"}  # Title font
        },
        plot_bgcolor="#f4f4f4",  # Background color to match app background
        paper_bgcolor="#f4f4f4",  # Full chart background color
        font=dict(family="Arial", size=12, color="#2c3e50"),
        margin=dict(t=20, b=40)  # Adjust margins
    )
    st.plotly_chart(fig_affiliations, use_container_width=True)

    # --- Raw Data for Selected Year ---
    st.markdown("### Raw Data for Selected Year")
    
    # Dropdown or text input for author name filter
    author_list = filtered_df['author_name'].dropna().unique()
    selected_author = st.selectbox("Filter by Author", options=["All"] + sorted(author_list), index=0)
    
    # Filter the data based on selected author
    if selected_author == "All":
        filtered_raw_data = filtered_df
    else:
        filtered_raw_data = filtered_df[filtered_df['author_name'] == selected_author]

    # Reset index to remove it from display
    filtered_raw_data = filtered_raw_data.reset_index(drop=True)

    # Style the dataframe
    styled_table = filtered_raw_data[['author_name', 'affiliation', 'title', 'publication_date']].style.apply(
        lambda x: ['background-color: #f0f2f6' if i % 2 == 0 else '' for i in range(len(x))],
        axis=0
    ).highlight_max(
        subset=['publication_date'], 
        color='#e6f2ff'
    ).set_properties(**{
        'font-size': '12px',
        'border': '1px solid #ddd',
        'text-align': 'left'
    })

    # Display the styled dataframe
    st.dataframe(
        styled_table, 
        use_container_width=True,
        hide_index=True
    )

    

elif page == "Topic/Keyword Filter":

    def topic_keyword_filter(filtered_df, df):
        """
        Topic/Keyword Filter Page with Enhanced Styling and Consistent Design
        """
        # Header
        st.markdown("<h2 style='text-align: center; color: #34495e;'>🔍 Topic/Keyword Filter</h2>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; color: #7f8c8d;'>Explore research publications by keyword and filter options.</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Filter Section
        st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 2, 2])

        with col1:
            # Keyword Input
            keyword = st.text_input(
                "Enter research topic or keyword:",
                placeholder="e.g., Artificial Intelligence, Machine Learning",
                help="Search across titles, affiliations, and cities"
            )

        with col2:
            # Year Range Slider
            min_year = filtered_df['publication_date'].dt.year.min()
            max_year = filtered_df['publication_date'].dt.year.max()
            
            if min_year == max_year:
                st.warning(f"All publications are from the year {min_year}. No range available.")
                selected_years = (min_year, max_year)  # Fixed value as no range is available
            else:
                # Create a slider for year selection
                selected_years = st.slider(
                    "Publication Year Range",
                    min_value=min_year,
                    max_value=max_year,
                    value=(min_year, max_year),
                    help="Select the range of publication years to filter"
            )

        with col3:
            # Country Multiselect
            countries = st.multiselect(
                "Filter by Countries",
                options=sorted(filtered_df['country'].unique().tolist()),
                default=None
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # Filter Logic
        if keyword or countries:
            filtered_df['publication_date'] = pd.to_datetime(filtered_df['publication_date'], errors='coerce')
            filtered_data = filtered_df[
                (filtered_df['title'].str.contains(keyword, case=False, na=False) |
                 filtered_df['affiliation'].str.contains(keyword, case=False, na=False) |
                 filtered_df['city'].str.contains(keyword, case=False, na=False)) &
                (filtered_df['publication_date'].dt.year >= selected_years[0]) &
                (filtered_df['publication_date'].dt.year <= selected_years[1])
            ]
            if countries:
                filtered_data = filtered_data[filtered_data['country'].isin(countries)]

            if filtered_data.empty:
                st.warning(f"No research papers found for '{keyword}'")
            else:
                tab1, tab2, tab3 = st.tabs(["📊 Data Table", "🗺️ Geospatial View", "📈 Publication Trends"])

                # Data Table
                with tab1:  # 📊 Data Table Tab
                    st.markdown("### 📊 Research Data Table")

                    # Apply dropdown filter for author names
                    author_list = filtered_data['author_name'].dropna().unique()
                    selected_author = st.selectbox("Filter by Author", options=["All"] + sorted(author_list), index=0)
                    
                    # Filter the data based on selected author
                    if selected_author == "All":
                        filtered_raw_data = filtered_data
                    else:
                        filtered_raw_data = filtered_data[filtered_data['author_name'] == selected_author]

                    # Reset index for clean display
                    filtered_raw_data = filtered_raw_data.reset_index(drop=True)

                    # Style the dataframe
                    styled_table = filtered_raw_data[['author_name', 'affiliation', 'title', 'publication_date']].style.apply(
                        lambda x: ['background-color: #f0f2f6' if i % 2 == 0 else '' for i in range(len(x))],
                        axis=0
                    ).highlight_max(
                        subset=['publication_date'], 
                        color='#e6f2ff'
                    ).set_properties(**{
                        'font-size': '12px',
                        'border': '1px solid #ddd',
                        'text-align': 'left'
                    })

                    # Display the styled dataframe
                    st.dataframe(
                        styled_table,
                        use_container_width=True,
                        hide_index=True
                    )

                with tab2:  # 🗺️ Geospatial View Tab
                    st.markdown("### 🗺️ Geospatial Analysis")

                    # Geospatial Visualization
                    country_counts = filtered_data['country'].value_counts().reset_index()
                    country_counts.columns = ['country', 'publication_count']

                    if not filtered_data.empty:
                        fig = px.choropleth(
                            country_counts, 
                            locations='country',
                            locationmode='country names',
                            color='publication_count',
                            hover_name='country',
                            color_continuous_scale='Viridis',
                            title='Geospatial Analysis'
                        )
                        fig.update_layout(
                            height=600,
                            plot_bgcolor="#f4f4f4", 
                            paper_bgcolor="#f4f4f4"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No geospatial data available.")

                # Publication Trends
                with tab3:
                    keyword_filtered_df = df[
                        (df['title'].str.contains(keyword, case=False, na=False) |
                         df['affiliation'].str.contains(keyword, case=False, na=False) |
                         df['city'].str.contains(keyword, case=False, na=False))
                    ]
                    yearly_trends = keyword_filtered_df.groupby(keyword_filtered_df['publication_date'].dt.year).size()
                    if not yearly_trends.empty:
                        trend_fig = go.Figure(data=[
                            go.Bar(
                                x=yearly_trends.index,
                                y=yearly_trends.values,
                                marker_color="#667eea",
                                hovertemplate='<b>Year: %{x}</b><br>Publications: %{y}<extra></extra>'
                            )
                        ])
                        trend_fig.update_layout(
                            title="Publication Trends by Keyword",
                            xaxis_title="Year",
                            yaxis_title="Number of Publications",
                            plot_bgcolor="#f4f4f4",
                            paper_bgcolor="#f4f4f4",
                            font=dict(family="Arial", size=12, color="#2c3e50"),
                            margin=dict(t=40, b=40)
                        )
                        st.plotly_chart(trend_fig, use_container_width=True)

                # Summary Metrics
                st.markdown("### 📖 Quick Statistics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Papers", len(filtered_data))
                with col2:
                    st.metric("Unique Countries", filtered_data['country'].nunique())
                with col3:
                    st.metric(
                        "Publication Range",
                        f"{filtered_data['publication_date'].dt.year.min()} - {filtered_data['publication_date'].dt.year.max()}"
                    )
    
    topic_keyword_filter(filtered_df, df)