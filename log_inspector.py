import streamlit as st
import pandas as pd
import re

st.set_page_config(layout="wide", page_title="Boomi Flow Inspector")

st.title("🌊 Boomi Flow & Data Inspector")
st.markdown("Visualize document flow, identify filters, and inspect payloads.")

uploaded_file = st.file_uploader("Upload Boomi .log file", type="log")

if uploaded_file is not None:
    parsed_lines = []
    # Regex for ISO-8601 + Tab format
    log_header_re = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s+(\w+)\s+(.*)')

    content = uploaded_file.getvalue().decode("utf-8").splitlines()
    
    for line in content:
        line_str = line.strip()
        if not line_str: continue
        match = log_header_re.match(line_str)
        if match:
            timestamp_iso, level, rest = match.groups()
            parts = rest.split('\t')
            shape = parts[0].strip() if len(parts) > 0 else "Unknown"
            action = " ".join(parts[1:]).strip() if len(parts) > 1 else ""
            parsed_lines.append({
                "Timestamp": timestamp_iso, 
                "Level": level, 
                "Shape": shape, 
                "Action": action
            })
        else:
            if parsed_lines:
                # Appends multi-line payloads (JSON/XML) to the current shape action
                parsed_lines[-1]["Action"] += f"\n{line_str}"

    df = pd.DataFrame(parsed_lines)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    # Calculate duration in milliseconds
    df['Duration (ms)'] = df['Timestamp'].diff().shift(-1).dt.total_seconds().fillna(0) * 1000

    # --- AGNOSTIC CATEGORIZATION ---
    def categorize_action(action):
        action_lower = action.lower()
        if "executing" in action_lower: return "🟢 Start/Entry"
        if "successfully" in action_lower: return "⚪ Completion"
        if any(x in action_lower for x in ["filter", "skip", "stop", "decision", "not present"]): return "🟠 Logic/Filter"
        if any(x in action_lower for x in ["document(s) found", "received", "returning"]): return "🔵 Data In"
        if "error" in action_lower or "fail" in action_lower: return "🔴 Error"
        return "📄 Info"

    df['Type'] = df['Action'].apply(categorize_action)

    # --- SIDEBAR ---
    st.sidebar.header("View Controls")
    search = st.sidebar.text_input("Global Data Search (Invoice #, ID, etc.)")
    
    # --- MAIN UI ---
    st.subheader("Process Trace")
    
    def style_rows(row):
        if "🔴" in row['Type']: return ['background-color: rgba(255, 0, 0, 0.1)'] * len(row)
        if "🔵" in row['Type']: return ['background-color: rgba(0, 100, 255, 0.2)'] * len(row)
        if "🟠" in row['Type']: return ['background-color: rgba(255, 165, 0, 0.1)'] * len(row)
        return [''] * len(row)

    # Filter by search if provided
    display_df = df.copy()
    if search:
        display_df = display_df[display_df['Action'].str.contains(search, case=False)]

    # The corrected selection_mode="single-row"
    selection = st.dataframe(
        display_df.style.apply(style_rows, axis=1),
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
        column_order=("Timestamp", "Type", "Shape", "Duration (ms)", "Action")
    )

    # --- INSPECTOR PANE ---
    if selection and selection["selection"]["rows"]:
        # Get the index of the selected row from the display_df
        idx = selection["selection"]["rows"][0]
        selected_data = display_df.iloc[idx]
        
        st.divider()
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("### Metadata")
            st.write(f"**Shape:** {selected_data['Shape']}")
            st.write(f"**Type:** {selected_data['Type']}")
            st.write(f"**Duration:** {selected_data['Duration (ms)']} ms")
        with col2:
            st.markdown("### Data Payload / Message")
            st.code(selected_data['Action'], wrap_lines=True)

    # --- TIMELINE ---
    with st.expander("Execution Timeline"):
        st.scatter_chart(df, x="Timestamp", y="Shape", color="Type", size="Duration (ms)")

else:
    st.info("Upload a Boomi log file to begin analysis.")
    