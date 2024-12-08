import os
import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px
import plotly.graph_objs as go


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

# Function to load datasets for multiple years
def load_combined_dataset():
    """
    Load and merge CSV files for multiple years from 2013 to 2023.
    """
    base_path = '.'  # Directory containing the CSV files
    pattern = 'cluster_final_prepared_{}_data.csv'
    dataframes = []

    for year in range(2013, 2024):
        filename = pattern.format(year)
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath)
                df['year'] = year  # Add year column
                dataframes.append(df)
            except Exception as e:
                st.sidebar.warning(f"Error loading {filename}: {e}")

    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
        combined_df['publication_date'] = pd.to_datetime(combined_df['publication_date'], errors='coerce')
        combined_df = combined_df.dropna(subset=['publication_date'])  # Remove invalid dates

        # Fill missing values
        columns_to_fill = ['title', 'author_name', 'affiliation', 'city', 'country']
        for col in columns_to_fill:
            combined_df[col] = combined_df[col].fillna('Unknown')

        return combined_df
    else:
        st.error("No data files could be loaded!")
        return pd.DataFrame()



df = load_combined_dataset()


# Streamlit App Title with a more professional presentation
st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🔬 Research Analysis Dashboard</h1>", unsafe_allow_html=True)

# Add a subtle description
st.markdown("""
<div style='text-align: center; color: #7f8c8d; margin-bottom: 20px;'>
    Comprehensive Research Insights and Geographic Analysis
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
st.sidebar.markdown("## 📊 Dashboard Navigation")
page = st.sidebar.radio("Select Analysis View", ["Cluster Analysis", "Geographic Analysis", "Author and Affiliation Insights", "Topic/Keyword Filter"])

# Sidebar Filters for Year
st.sidebar.markdown("## 🔍 Filters")
selected_year = st.sidebar.slider("Select Year", int(df['year'].min()), int(df['year'].max()), 2017)

# Prepare the data (year)
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
    country_counts = filtered_df['country'].value_counts().reset_index()
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

    # Top Authors
    st.markdown("## 🏆 Top Authors")
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
    fig_authors.update_layout(
        plot_bgcolor='rgba(255,255,255,0.9)',
        font=dict(family="Arial", size=12, color="#2c3e50"),
        xaxis_tickangle=-45  # Rotate author names for readability
    )
    st.plotly_chart(fig_authors)

    # Affiliation Analysis
    st.markdown("## 🏫 Affiliation Analysis")
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
    st.plotly_chart(fig_affiliations)

    # Raw Data for Selected Year
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

    

# Topic/Keyword Filter Page
elif page == "Topic/Keyword Filter":

    def topic_keyword_filter(filtered_df, df):
        """
        Enhanced Topic/Keyword Filter with Advanced Styling and Visualization
        """
        # Custom CSS for enhanced styling
        st.markdown("""
        <style>
        /* Global Styling */
        .stApp {
            background-color: #F0F4F8;
            font-family: 'Arial', sans-serif;
        }
        
        /* Header Styling */
        .main-header {
            background: linear-gradient(135deg, #bde6ff 0%, #90cdf4 100%);
            color: white;
            text-align: center;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        
        /* Filter Section Styling */
        .filter-section {
            background-color: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        /* Custom Table Styling */
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        /* Metric Cards Styling */
        .metric-card {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .metric-card:hover {
            transform: scale(1.05);
        }
        </style>
        """, unsafe_allow_html=True)

        # Header with advanced styling
        st.markdown('<div class="main-header"><h1>🔍 Advanced Research Paper Explorer</h1></div>', unsafe_allow_html=True)
        
        # Filter Section
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        
        # Columns for filtering
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Enhanced Keyword Input
            keyword = st.text_input(
                "Enter research topic or keyword:",
                placeholder="e.g., Artificial Intelligence, Machine Learning",
                help="Search across titles, affiliations, and cities"
            )
        
        with col2:
            # Year range slider
            min_year = filtered_df['publication_date'].dt.year.min()
            max_year = filtered_df['publication_date'].dt.year.max()
            if min_year != max_year:
                selected_years = st.slider(
                    "Publication Year", 
                    min_value=min_year, 
                    max_value=max_year, 
                    value=(min_year, max_year)
                )
            else:
                # If all data is from the same year, use that year
                selected_years = (min_year, min_year)
                st.warning(f"All publications are from {min_year}")
        
        # Country multiselect
        countries = st.multiselect(
            "Filter by Countries",
            options=sorted(filtered_df['country'].unique().tolist()),
            default=None
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Apply Filters
        if keyword or countries:
            # Ensure publication_date is in datetime format
            filtered_df['publication_date'] = pd.to_datetime(filtered_df['publication_date'], errors='coerce')
            
            # Base filter for keyword and year range
            # Modify filter condition
            filtered_data = filtered_df[
                (filtered_df['title'].str.contains(keyword, case=False, na=False) |
                filtered_df['affiliation'].str.contains(keyword, case=False, na=False) |
                filtered_df['city'].str.contains(keyword, case=False, na=False)) &
                (filtered_df['publication_date'].dt.year >= selected_years[0]) &
                (filtered_df['publication_date'].dt.year <= selected_years[1])
            ]
            
            # Additional country filter
            if countries:
                filtered_data = filtered_data[filtered_data['country'].isin(countries)]
            
            # Results Display
            if filtered_data.empty:
                st.warning(f"No research papers found for '{keyword}'")
            else:
                # Tabs for different views
                tab1, tab2, tab3 = st.tabs(["📊 Data Table", "🗺️ Geospatial View", "📈 Publication Trends"])
                
                with tab1:
                    # Enhanced Data Table with Basic Styling
                    st.dataframe(
                        filtered_data[['title', 'author_name', 'affiliation', 'publication_date', 'city', 'country']],
                        use_container_width=True,
                        height=400,
                        # Optional: Add some basic column configuration
                        column_config={
                            "publication_date": st.column_config.DateColumn(
                                "Publication Date",
                                format="YYYY-MM-DD",
                            ),
                            "title": st.column_config.TextColumn("Title", width="large"),
                        }
                    )
                
                with tab2:
                    # Geospatial Visualization
                    if not filtered_data.empty:
                        country_counts = filtered_data['country'].value_counts().reset_index()
                        country_counts.columns = ['country', 'publication_count']
                        
                        fig = px.choropleth(
                            country_counts, 
                            locations='country',
                            locationmode='country names',
                            color='publication_count',
                            hover_name='country',
                            color_continuous_scale='Viridis',
                            title='Research Publications by Country'
                        )
                        fig.update_layout(height=600)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No geospatial data available")
                
                with tab3:
                    # Full dataset keyword trend
                    keyword_filtered_df = df[
                        (df['title'].str.contains(keyword, case=False, na=False) |
                        df['affiliation'].str.contains(keyword, case=False, na=False) |
                        df['city'].str.contains(keyword, case=False, na=False))
                    ]
                    
                    yearly_trends = keyword_filtered_df.groupby(keyword_filtered_df['publication_date'].dt.year).size()
                    
                    if yearly_trends.empty:
                        st.info(f"No publication trends found for the keyword '{keyword}'.")
                    else:
                        trend_fig = go.Figure(data=[
                            go.Bar(
                                x=yearly_trends.index,
                                y=yearly_trends.values,
                                marker_color='rgba(102, 126, 234, 0.7)',
                                marker_line_color='rgba(102, 126, 234, 1)',
                                marker_line_width=1.5
                            )
                        ])
                        trend_fig.update_layout(
                            title=f'Yearly Publication Trends for "{keyword}" (2013-2023)',
                            xaxis_title='Year',
                            yaxis_title='Number of Publications',
                            plot_bgcolor='rgba(240, 244, 248, 0.5)'
                        )
                        st.plotly_chart(trend_fig, use_container_width=True)
                
                # Summary Statistics with Styled Cards
                st.markdown("### 📊 Quick Statistics")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Total Papers</h3>
                        <p style="font-size: 24px; color: #667eea;">{len(filtered_data)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Unique Countries</h3>
                        <p style="font-size: 24px; color: #667eea;">{filtered_data['country'].nunique()}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Publication Range</h3>
                        <p style="font-size: 24px; color: #667eea;">{filtered_data['publication_date'].dt.year.min()} - {filtered_data['publication_date'].dt.year.max()}</p>
                    </div>
                    """, unsafe_allow_html=True)


    topic_keyword_filter(filtered_df, df)