import streamlit as st
import subprocess
import sys
import io
from contextlib import redirect_stdout

st.set_page_config(page_title="Streamlit Python Host", layout="wide")

st.title("🚀 Python Interactive Host")

# Sidebar for Package Management
with st.sidebar:
    st.header("📦 Package Manager")
    package_name = st.text_input("Install pip package", placeholder="e.g. pandas")
    if st.button("Install"):
        with st.spinner(f"Installing {package_name}..."):
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", package_name],
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                st.success(f"Successfully installed {package_name}")
            else:
                st.error(f"Error: {stderr}")

# Main Layout: Editor and Console
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Code Editor")
    code_input = st.text_area(
        "Enter Python Code", 
        value='print("Hello from Streamlit!")\nimport os\nprint(os.getcwd())',
        height=400
    )
    run_btn = st.button("▶️ Run Code")

with col2:
    st.header("🖥️ Live Console")
    if run_btn:
        output_buffer = io.StringIO()
        try:
            with redirect_stdout(output_buffer):
                # Execute the code in the current environment
                exec(code_input)
            st.code(output_buffer.getvalue(), language="text")
        except Exception as e:
            st.error(f"Execution Error: {e}")
    else:
        st.info("Results will appear here after clicking 'Run'")

# System Info Feature
with st.expander("🛠️ System Status"):
    st.write(f"Python Version: {sys.version}")
    if st.button("Check Installed Packages"):
        result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
        st.text(result.stdout)
