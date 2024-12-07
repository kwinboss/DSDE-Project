import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.graph_objs as go
import plotly.express as px

# Custom CSS for a more professional look
st.markdown("""
<style>
    /* Main background and text color */
    .stApp {
        background-color: #f4f4f4;
        color: #333;
    }
    
    /* Header styling */
    .stMarkdown h1 {
        color: #2c3e50;
        text-align: center;
        font-weight: bold;
        margin-bottom: 30px;
    }
    
    /* Sidebar styling */
    .css-1aumxhk {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Sidebar header */
    .css-1aumxhk .css-1v3fvcr {
        color: #2c3e50;
        font-weight: bold;
    }
    
    /* Card-like containers */
    .stContainer, .stCard {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Subheader styling */
    .stSubheader {
        color: #2980b9;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    
    /* Button styling */
    .stRadio > div {
        display: flex;
        justify-content: center;
    }
    
    .stButton > button {
        background-color: #3498db;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        transition: background-color 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #2980b9;
    }
</style>
""", unsafe_allow_html=True)

# Load the dataset (replace with the path to your file)
data = pd.read_csv('data_in_cluster.csv')
df = pd.DataFrame(data)

# Streamlit App Title with a more professional presentation
st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🔬 Research Analysis Dashboard</h1>", unsafe_allow_html=True)

# Add a subtle description
st.markdown("""
<div style='text-align: center; color: #7f8c8d; margin-bottom: 20px;'>
    Comprehensive Research Insights and Geographic Analysis
</div>
""", unsafe_allow_html=True)

# Sidebar for page selection
st.sidebar.markdown("## 📊 Dashboard Navigation")
page = st.sidebar.radio("Select Analysis View", ["Cluster Analysis", "Geographic Analysis", "Author and Affiliation Insights"])

# Sidebar Filters for Year and Country/City
st.sidebar.markdown("## 🔍 Filters")
selected_year = st.sidebar.slider("Select Year", 2011, 2021, 2017)

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

# Prepare the data
df["year"] = pd.to_datetime(df["publication_date"]).dt.year
filtered_df = df[df["year"] == selected_year]

# Conditional filtering based on selected page
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
    # For Cluster Analysis, we don't show the country or city filters
    selected_country = "All"
    selected_city = "All"

# Map the color for each row based on its cluster
filtered_df["color"] = filtered_df["cluster"].map(color_map)

# Handle different pages in the app
if page == "Cluster Analysis":
    # Clustered Geomap
    st.markdown("## 🌍 Clustered Geomap")
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",  # Light theme for better readability
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

    def rgba_to_plotly(rgba):
        return f'rgba({rgba[0]},{rgba[1]},{rgba[2]},{rgba[3]/255})'

    fig = go.Figure(data=[
        go.Bar(
            x=cluster_counts['Cluster'],
            y=cluster_counts['Number of Points'],
            marker_color=[rgba_to_plotly(color_map.get(cluster, [128, 128, 128, 160])) for cluster in cluster_counts['Cluster']],
            hovertemplate='<b>Cluster: %{x}</b><br>Number of Points: %{y}<br><extra></extra>',
            opacity=0.8
        )
    ])
    fig.update_layout(
        title="Cluster Composition Analysis",
        xaxis_title='Cluster ID',
        yaxis_title='Number of Points in Cluster',
        plot_bgcolor='rgba(255,255,255,0.9)',
        font=dict(family="Arial", size=12, color="#2c3e50"),
    )

    # Add annotation for the maximum cluster
    max_cluster = cluster_counts.loc[cluster_counts['Number of Points'].idxmax()]
    fig.add_annotation(
        x=max_cluster['Cluster'], y=max_cluster['Number of Points'],
        text=f"Max: {max_cluster['Number of Points']}",
        showarrow=True, arrowhead=2, 
        font=dict(size=12, color="#2c3e50"),
        bordercolor="#3498db",
        borderwidth=2,
        borderpad=4,
        bgcolor="#ffffff"
    )

    st.plotly_chart(fig)

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
    
    # Check if there's data to plot
    if city_data.empty:
        st.warning(f"No geographic data available for {selected_city} in {selected_country}")
    else:
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9", 
            initial_view_state=pdk.ViewState(
                latitude=city_data['latitude'].mean(),
                longitude=city_data['longitude'].mean(),
                zoom=5 if selected_city != "All" else 3,
                pitch=50,
            ),
            layers=[
                pdk.Layer(
                    "HeatmapLayer",
                    data=city_data,
                    get_position="[longitude, latitude]",
                    get_weight=1,
                    radius_pixels=30,
                    opacity=0.7,
                ),
            ],
        ))

    # Top Research Countries (Bar Chart)
    st.markdown("## 🌐 Top Research Countries")
    country_counts = df['country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'Number of Publications']
    fig = px.bar(
        country_counts, 
        x='Country', 
        y='Number of Publications', 
        title="Research Publications by Country",
        color='Number of Publications',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(
        plot_bgcolor='rgba(255,255,255,0.9)',
        font=dict(color="#2c3e50")
    )
    st.plotly_chart(fig)

    # City-Level Analysis (Table)
    st.markdown("## 📍 City-Level Analysis")
    if selected_country == "All":
        st.info("Please select a specific country to view city-level details.")
    else:
        # Filter table data based on country and city selection
        if selected_city == "All":
            table_data = df[df['country'] == selected_country]
        else:
            table_data = df[(df['country'] == selected_country) & (df['city'] == selected_city)]
    
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

    # Filter data by selected year
    year_filtered_df = df[df['year'] == selected_year]

    # Top Authors
    st.markdown("## 🏆 Top Authors")
    # Calculate top authors by number of publications
    top_authors = year_filtered_df['author_name'].value_counts().head(10).reset_index()
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
    fig_authors.update_layout(
        plot_bgcolor='rgba(255,255,255,0.9)',
        font=dict(family="Arial", size=12, color="#2c3e50"),
        xaxis_tickangle=-45  # Rotate author names for readability
    )
    st.plotly_chart(fig_authors)

    # Affiliation Analysis
    st.markdown("## 🏫 Affiliation Analysis")
    # Calculate top affiliations by number of publications
    top_affiliations = year_filtered_df['affiliation'].value_counts().head(10).reset_index()
    top_affiliations.columns = ['Affiliation', 'Number of Publications']

    # Pie chart for top affiliations
    fig_affiliations = px.pie(
        top_affiliations,
        names='Affiliation',
        values='Number of Publications',
        title="Top 10 Affiliations by Publications",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig_affiliations)

    # Raw Data for Selected Year
    st.markdown("### Raw Data for Selected Year")
    # Dropdown or text input for author name filter
    author_list = year_filtered_df['author_name'].dropna().unique()
    selected_author = st.selectbox("Filter by Author", options=["All"] + sorted(author_list), index=0)
    # Filter the data based on selected author
    if selected_author == "All":
        filtered_raw_data = year_filtered_df
    else:
        filtered_raw_data = year_filtered_df[year_filtered_df['author_name'] == selected_author]
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

    # Add a footer
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d; margin-top: 30px;'>
    © 2024 Research Analysis Dashboard | Powered by Streamlit
    </div>
    """, unsafe_allow_html=True)