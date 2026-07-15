#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 11:50:59 2025

@author: dina
"""

import streamlit as st
import seaborn as sns
import pandas as pd
import plotly.express as px

# SWD-flavoured palette: one muted highlight hue instead of a rainbow.
# CVD-safe anchors; single-hue sequentials for the treemap/heatmap.
BLUE = "#2E75B6"
ORANGE = "#E07B39"

# setting up the page
st.set_page_config(page_title="Diamond Dashboard", page_icon="💎", layout="wide")
st.title("💎 Diamond Analytics Dashboard 💎")

# loading the data and caching it for spead
@st.cache_data
def load_data():
     return sns.load_dataset("diamonds")
# function call
df = load_data()

# adding a pandas dataframe head with a title
st.header("Sample of Raw Data")
st.dataframe(df.head())

# adding side bar with filters
st.sidebar.header("Filter Diamonds 🔍")

# adding filters for cut, color, clarity
# filter by cut 
selected_cuts = st.sidebar.multiselect("Select cut:", df["cut"].unique(), default=df["cut"].unique())
# filter by color
selected_colors = st.sidebar.multiselect("Select color:", df["color"].unique(), default=df["color"].unique())
# filter by clarity
selected_clarity = st.sidebar.multiselect("Select clarity:", df["clarity"].unique(), default=df["clarity"].unique())

# filtered data based on the mutiselect widgets
boolean_filter = df["cut"].isin(selected_cuts) & df["color"].isin(selected_colors) & df["clarity"].isin(selected_clarity)
filtered = df.loc[boolean_filter]


# Calculate metrics using pandas
num_diamonds = len(filtered)
avg_price = filtered["price"].mean()
avg_carat = filtered["carat"].mean()
max_price = filtered["price"].max()

# display metrics using streamlit
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="# of Diamonds", value=f"{num_diamonds:,}")
col2.metric(label="Avg. Price $", value=f"${avg_price:,.0f}")
col3.metric(label="Avg. Carat", value=f"{avg_carat:.2f}")
col4.metric(label="Max Price $", value=f"${max_price:,.0f}")


# figure 1: Heatmap
# Group by cut and color, and calculate the mean price and create a pivot table
pivot_table = filtered.pivot_table(values='price', index='cut', columns='color', aggfunc='mean')
fig_heatmap = px.imshow(
    pivot_table,  # Set 'cut' as the index,  
    # Axis and color labels
    title="Heatmap of Mean Price by Cut and Color",
    labels= {'x': 'Color', 'y': 'Cut', 'color': 'Average Price in US $'},
    text_auto="1.0f",  # Show text with 2 decimal places
    color_continuous_scale=px.colors.sequential.Blues,
    width=1000,
    height=700,
    aspect='auto' # allows the aspect ratio to be not equal to one, i.e. the heatmap will not be a square
)

st.plotly_chart(fig_heatmap, use_container_width=True)


# figure2: price by cut bar plot — ordered by bar height (descending)
# observed=True avoids NaN bars for cuts filtered out in the sidebar
avg_by_cut = (
    filtered.groupby("cut", observed=True)["price"]
    .mean()
    .reset_index()
    .sort_values("price", ascending=False)
)
# declarative ordering: force the x-axis to follow bar height, overriding the
# categorical's natural order (Fair < Good < ... < Ideal)
cut_order = avg_by_cut["cut"].tolist()

avg_by_cut["color_role"] = "other"
avg_by_cut.loc[avg_by_cut["price"].idxmax(), "color_role"] = "highlight"

fig_cut = px.bar(
    avg_by_cut, x="cut", y="price", title="Average Diamond Price by Cut",
    labels={"price": "Avg Price ($)", "cut": "Cut"},
    category_orders={"cut": cut_order},
    color="color_role",
    color_discrete_map={"highlight": ORANGE, "other": BLUE},
).update_layout(showlegend=False)

# figure 3: Clarity Breakdown — treemap (replaces the donut)
clarity_counts = filtered["clarity"].value_counts().reset_index()
fig_clarity = px.treemap(
    clarity_counts, path=[px.Constant('Selected Diamonds'), "clarity"], values="count",
    title="Diamond Clarity Distribution",
    color="count", color_continuous_scale=px.colors.sequential.Blues,
)

fig_clarity.update_traces(
    textinfo="label+value+percent root",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "Diamonds: %{value:,}<br>"
        "Share: %{percentRoot:.1%}"
        "<extra></extra>"
    ),
)


#figure 4: price histogram
fig_hist_price = px.histogram(
    filtered, x="price", nbins=30, title="Price Distribution", labels={"price":"Price ($)"},
    color_discrete_sequence=[BLUE])

#figure 5: carat histogram
fig_hist_carat = px.histogram(
    filtered, x="carat", nbins=30, title="Carat Distribution", labels={"carat":"Carat"},
    color_discrete_sequence=[BLUE])



col1, col2 = st.columns(2)

col1.plotly_chart(fig_cut)
col2.plotly_chart(fig_clarity)
col1.plotly_chart(fig_hist_carat)
col2.plotly_chart(fig_hist_price)
