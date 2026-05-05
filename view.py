import streamlit as st
import pandas as pd
import altair as alt

def initialize_page():
    st.set_page_config(layout="wide", page_title="Boomi MVC Inspector")
    st.title("🌊 Boomi MVC Log Inspector")

def draw_sidebar():
    st.sidebar.header("Navigation & Filters")
    return st.sidebar.text_input("🔍 Search Payloads/Actions")

def display_trace_map(df):
    """Renders the cohesive chronological process flow."""
    with st.expander("Execution Flow Visualizer", expanded=True):
        # 1. Define order based on first appearance (Logical Flow)
        shape_order = df.groupby('Shape')['Timestamp'].min().sort_values().index.tolist()
        
        base = alt.Chart(df).encode(
            x=alt.X('Timestamp:T', title='Time'),
            y=alt.Y('Shape:N', sort=shape_order, title='Process Path'),
            color=alt.Color('Type:N', scale=alt.Scale(
                domain=['🟢 Start', '🔵 Data', '🟠 Logic', '🔴 Error', '⚪ Done', '📄 Info'],
                range=['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#bdc3c7', '#95a5a6']
            ))
        )

        # 2. Cohesive path lines (Connecting the hand-offs)
        lines = base.mark_line(opacity=0.4, color='gray', strokeDash=[3,3]).encode(
            order='Timestamp:T' 
        )

        # 3. Shape execution points
        points = base.mark_circle(size=100, opacity=0.8).encode(
            tooltip=['Timestamp', 'Shape', 'Type', 'Duration (ms)']
        )

        st.altair_chart((lines + points).properties(height=400).interactive(), use_container_width=True)
        st.caption("🔗 Lines indicate the chronological sequence of hand-offs between Boomi shapes.")

def display_main_table(df):
    """Renders the color-coded interactive dataframe."""
    def style_rows(row):
        if "🔴" in row['Type']: return ['background-color: rgba(255, 0, 0, 0.1)'] * len(row)
        if "🔵" in row['Type']: return ['background-color: rgba(0, 100, 255, 0.15)'] * len(row)
        if "🟠" in row['Type']: return ['background-color: rgba(255, 165, 0, 0.1)'] * len(row)
        return [''] * len(row)

    st.subheader("Process Execution Trace")
    return st.dataframe(
        df.style.apply(style_rows, axis=1), 
        use_container_width=True, 
        on_select="rerun", 
        selection_mode="single-row",
        column_order=("Timestamp", "Type", "Shape", "Duration (ms)", "Action")
    )

def show_detail_pane(selected_row):
    st.divider()
    st.markdown(f"### 🔍 Detail: {selected_row['Shape']}")
    st.code(selected_row['Action'], wrap_lines=True)