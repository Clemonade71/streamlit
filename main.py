import pandas as pd
import zipfile
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from io import BytesIO
import streamlit as st

## LOAD DATA DIRECTLY FROM SS WEBSITE
@st.cache_data
def load_name_data():
    names_file = 'https://www.ssa.gov/oact/babynames/names.zip'
    response = requests.get(names_file)
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        dfs = []
        files = [file for file in z.namelist() if file.endswith('.txt')]
        for file in files:
            with z.open(file) as f:
                df = pd.read_csv(f, header=None)
                df.columns = ['name','sex','count']
                df['year'] = int(file[3:7])
                dfs.append(df)
        data = pd.concat(dfs, ignore_index=True)
    data['pct'] = data['count'] / data.groupby(['year', 'sex'])['count'].transform('sum')
    return data

# Load and preprocess the dataset
df = load_name_data()
df['total_births'] = df.groupby(['year', 'sex'])['count'].transform('sum')
df['prop'] = df['count'] / df['total_births']

# App title
st.title('👶 My Baby Name App')

# Sidebar input widgets
st.sidebar.title("🔧 Filters & Options")

# Name filter section
st.sidebar.subheader("📈 Name Trend")
noi = st.sidebar.text_input('Enter a name')
plot_female = st.sidebar.checkbox('Plot female line', value=True)
plot_male = st.sidebar.checkbox('Plot male line', value=True)

# Year and gender filter section
st.sidebar.subheader("📅 Top Names by Year")
year_of_interest = st.sidebar.number_input('Enter a year', min_value=1880, max_value=2025, value=1990)
gender_of_interest = st.sidebar.radio('Select gender', ['Female', 'Male'])

# Tabs layout
tab1, tab2, tab3 = st.tabs(['Overview', 'By Name', 'By Year'])

# Tab 1: Static or summary information
with tab1:
    st.subheader("📊 About the Dataset")
    st.write("""
        This dataset comes from the U.S. Social Security Administration and contains
        baby name counts from 1880 to 2022 (updated annually).
        
        You can explore name popularity trends, compare male vs. female name usage,
        and see the most popular names in any given year.
    """)
    st.dataframe(df.sample(10))  # random sample of the data

# Tab 2: Name trend over time
with tab2:
    st.subheader(f"Popularity of the name '{noi}' over time")
    name_df = df[df['name'].str.lower() == noi.lower()]

    if not name_df.empty:
        fig = plt.figure(figsize=(15, 8))

        if plot_female:
            sns.lineplot(data=name_df[name_df['sex'] == 'F'], x='year', y='prop', label='Female')

        if plot_male:
            sns.lineplot(data=name_df[name_df['sex'] == 'M'], x='year', y='prop', label='Male')

        plt.title(f'Popularity of {noi} over time')
        plt.xlim(1880, 2025)
        plt.xlabel('Year')
        plt.ylabel('Proportion of births')
        plt.xticks(rotation=90)
        plt.legend()
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("Please enter a valid name to display trends.")

# Tab 3: Top names by year and gender
with tab3:
    st.subheader(f"Top 10 {gender_of_interest} Names in {year_of_interest}")
    top_names = df[df['year'] == year_of_interest]

    if gender_of_interest == 'Female':
        top_female = top_names[top_names['sex'] == 'F'].sort_values(by='count', ascending=False).head(10)
        plt.figure(figsize=(10, 5))
        sns.barplot(data=top_female, x='count', y='name', ax=plt.gca())
        plt.title(f"Top 10 Female Names in {year_of_interest}")
        plt.xlabel('Count')
        plt.ylabel('Name')
        plt.tight_layout()
        st.pyplot(plt.gcf())

    elif gender_of_interest == 'Male':
        top_male = top_names[top_names['sex'] == 'M'].sort_values(by='count', ascending=False).head(10)
        plt.figure(figsize=(10, 5))
        sns.barplot(data=top_male, x='count', y='name', ax=plt.gca())
        plt.title(f"Top 10 Male Names in {year_of_interest}")
        plt.xlabel('Count')
        plt.ylabel('Name')
        plt.tight_layout()
        st.pyplot(plt.gcf())
