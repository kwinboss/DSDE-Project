import os
import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px
import plotly.graph_objs as go

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

# Load all data
df = load_combined_dataset()

# Streamlit App Title
st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🔬 Research Analysis Dashboard</h1>", unsafe_allow_html=True)

# Sidebar for navigation and filters
st.sidebar.markdown("## 📊 Dashboard Navigation")
page = st.sidebar.radio("Select Analysis View", ["Cluster Analysis", "Geographic Analysis", "Author and Affiliation Insights", "Topic/Keyword Filter"])

# Sidebar Filters
st.sidebar.markdown("## 🔍 Filters")
selected_year = st.sidebar.slider("Select Year", int(df['year'].min()), int(df['year'].max()), 2017)

# Filter the data based on selected year
filtered_df = df[df['year'] == selected_year]

# Define a color mapping for clusters
color_map = {
    -1: [80, 80, 80, 160],  # Dark Gray for outliers
    0: [255, 0, 0, 160],  # Red
    1: [0, 128, 0, 160],  # Dark Green
    # Add more colors as needed for your clusters
}

filtered_df['color'] = filtered_df['cluster'].map(color_map)

# Handle different pages
if page == "Cluster Analysis":
    st.markdown("## 🌍 Clustered Geomap")
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
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
    st.markdown("## 📊 Cluster Composition")
    cluster_counts = filtered_df['cluster'].value_counts().reset_index()
    cluster_counts.columns = ['Cluster', 'Number of Points']
    fig = px.bar(cluster_counts, x='Cluster', y='Number of Points', title="Cluster Composition")
    st.plotly_chart(fig)

elif page == "Geographic Analysis":
    country_counts = filtered_df['country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'Publications']
    st.markdown("## 🌐 Research Publications by Country")
    fig = px.choropleth(
        country_counts,
        locations='Country',
        locationmode='country names',
        color='Publications',
        hover_name='Country',
        title="Global Distribution of Research Publications"
    )
    st.plotly_chart(fig)

elif page == "Author and Affiliation Insights":
    st.markdown("## 🏆 Top Authors")
    top_authors = filtered_df['author_name'].value_counts().head(10).reset_index()
    top_authors.columns = ['Author', 'Number of Publications']
    fig = px.bar(top_authors, x='Author', y='Number of Publications', title="Top 10 Authors")
    st.plotly_chart(fig)

    st.markdown("## 🏫 Top Affiliations")
    top_affiliations = filtered_df['affiliation'].value_counts().head(10).reset_index()
    top_affiliations.columns = ['Affiliation', 'Number of Publications']
    fig = px.pie(top_affiliations, names='Affiliation', values='Number of Publications', title="Top 10 Affiliations")
    st.plotly_chart(fig)

elif page == "Topic/Keyword Filter":
    st.markdown("## 🔍 Research Topic/Keyword Filter")
    keyword = st.text_input("Enter a keyword to search:", placeholder="e.g., Artificial Intelligence")
    if keyword:
        keyword_filtered_df = filtered_df[
            filtered_df['title'].str.contains(keyword, case=False, na=False)
        ]
        if not keyword_filtered_df.empty:
            st.dataframe(keyword_filtered_df[['title', 'author_name', 'affiliation', 'city', 'country', 'publication_date']])
        else:
            st.warning("No results found for the entered keyword.")