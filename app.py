import streamlit as st
import model
import view

def main():
    view.initialize_page()
    
    search_query = view.draw_sidebar()
    uploaded_file = st.file_uploader("Upload Boomi Log (.log)", type="log")

    if uploaded_file:
        # Ask Model to parse data
        raw_text = uploaded_file.getvalue().decode("utf-8")
        df = model.get_log_dataframe(raw_text)

        if not df.empty:
            # Apply filtering
            if search_query:
                df = df[df['Action'].str.contains(search_query, case=False)]

            # Ask View to render visualizations
            view.display_trace_map(df)
            selection = view.display_main_table(df)

            # Handle row selection
            if selection and selection["selection"]["rows"]:
                selected_index = selection["selection"]["rows"][0]
                view.show_detail_pane(df.iloc[selected_index])
        else:
            st.warning("The uploaded file does not contain valid Boomi log entries.")

if __name__ == "__main__":
    main()