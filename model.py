import pandas as pd
import re

def get_log_dataframe(raw_text):
    """
    Parses raw Boomi log text into a structured and enriched DataFrame.
    """
    # Regex for ISO-8601 timestamps and log headers
    log_header_re = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s+(\w+)\s+(.*)')
    parsed_lines = []
    
    for line in raw_text.splitlines():
        line_str = line.strip()
        if not line_str:
            continue
            
        match = log_header_re.match(line_str)
        if match:
            timestamp_iso, level, rest = match.groups()
            parts = rest.split('\t')
            shape = parts[0].strip() if len(parts) > 0 else "Unknown"
            action = " ".join(parts[1:]).strip() if len(parts) > 1 else ""
            
            parsed_lines.append({
                "Timestamp": pd.to_datetime(timestamp_iso), 
                "Level": level, 
                "Shape": shape, 
                "Action": action
            })
        else:
            # Multi-line payload handling (JSON/XML)
            if parsed_lines:
                parsed_lines[-1]["Action"] += f"\n{line_str}"

    df = pd.DataFrame(parsed_lines)
    
    if not df.empty:
        # Calculate time spent in each shape
        df['Duration (ms)'] = df['Timestamp'].diff().shift(-1).dt.total_seconds().fillna(0) * 1000
        
        # Agnostic Categorization for UI Styling
        def categorize(action):
            a = action.lower()
            if "executing" in a: return "🟢 Start"
            if "successfully" in a: return "⚪ Done"
            if any(x in a for x in ["filter", "decision", "stop"]): return "🟠 Logic"
            if any(x in a for x in ["found", "received"]): return "🔵 Data"
            if "error" in a: return "🔴 Error"
            return "📄 Info"
            
        df['Type'] = df['Action'].apply(categorize)
        
    return df