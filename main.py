import streamlit as st
import subprocess
import sys
import threading
import time
import io
import os

# --- 1. CONFIG & BEAUTIFICATION ---
st.set_page_config(page_title="Nexus-OS Terminal", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #00ff41; }
    .stTextInput>div>div>input { background-color: #1e1e1e; color: #00ff41; border: 1px solid #00ff41; }
    .stTextArea>div>div>textarea { background-color: #1e1e1e; color: #00ff41; font-family: 'Courier New', monospace; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #262730; color: white; border: 1px solid #444; }
    .stButton>button:hover { border-color: #00ff41; color: #00ff41; }
    </style>
    """, unsafe_allow_index=True)

# --- 2. SECURITY GATE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 System Locked")
    passwd = st.text_input("Enter Access Key", type="password")
    if st.button("Decrypt"):
        if passwd == "Copilot":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Access Denied.")
    st.stop()

# --- 3. PERSISTENT STATE MANAGEMENT ---
if 'processes' not in st.session_state:
    st.session_state.processes = {} # Store background apps here
if 'terminal_log' not in st.session_state:
    st.session_state.terminal_log = "Nexus-OS v1.0 Booted...\n"

# --- 4. THE ENGINE (Keep-Alive Logic) ---
def run_in_background(app_name, code):
    """Executes code in a separate thread to keep it alive."""
    try:
        # Redirect output for background tasks
        output = io.StringIO()
        exec(code, {'st': st, 'print': lambda *args: output.write(" ".join(map(str, args)) + "\n")})
        st.session_state.processes[app_name] = "Completed successfully."
    except Exception as e:
        st.session_state.processes[app_name] = f"Error: {str(e)}"

# --- 5. SIDEBAR NAVIGATION (Multi-App Panel) ---
with st.sidebar:
    st.title("🚀 NEXUS PANEL")
    app_mode = st.radio("Switch Environment", 
        ["🖥️ Interactive Console", "📦 Package Manager", "⚙️ Process Monitor", "📁 File Explorer"])
    
    st.divider()
    if st.button("🛑 Emergency Kill All"):
        st.session_state.processes = {}
        st.success("All background threads cleared.")

# --- 6. APP MODULES ---

# MODULE: Interactive Console
if app_mode == "🖥️ Interactive Console":
    st.header("Interactive Python Console")
    
    col_code, col_out = st.columns([1, 1])
    
    with col_code:
        code_to_run = st.text_area("Write Python Code (Supports loops/background)", height=300, value="import time\nfor i in range(10):\n    print(f'Step {i}...')\n    time.sleep(1)")
        keep_alive = st.checkbox("Keep Alive (Run in Background)", value=False)
        
        if st.button("🚀 Execute"):
            if keep_alive:
                task_id = f"Task_{len(st.session_state.processes)+1}"
                thread = threading.Thread(target=run_in_background, args=(task_id, code_to_run))
                thread.start()
                st.session_state.processes[task_id] = "Running..."
            else:
                # Standard Immediate Execution
                buffer = io.StringIO()
                try:
                    exec(code_to_run)
                    st.session_state.terminal_log += "\n" + "Success."
                except Exception as e:
                    st.error(e)

    with col_out:
        st.subheader("Live Output")
        # In a real environment, we'd use a websocket, but for Streamlit we refresh the log
        st.code(st.session_state.terminal_log)
        if st.button("🗑️ Clear Logs"):
            st.session_state.terminal_log = ""
            st.rerun()

# MODULE: Package Manager
elif app_mode == "📦 Package Manager":
    st.header("Pip Installer")
    pkg = st.text_input("Library Name")
    if st.button("Install"):
        with st.spinner("Downloading..."):
            res = subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True, text=True)
            st.code(res.stdout)

# MODULE: Process Monitor
elif app_mode == "⚙️ Process Monitor":
    st.header("Active Background Processes")
    if not st.session_state.processes:
        st.info("No apps running in keep-alive mode.")
    else:
        for p_id, status in st.session_state.processes.items():
            st.write(f"**{p_id}**: {status}")

# MODULE: File Explorer
elif app_mode == "📁 File Explorer":
    st.header("System Files")
    files = os.listdir(".")
    st.table({"Files in Container": files})
    new_file = st.text_input("Create new file (name)")
    content = st.text_area("File Content")
    if st.button("Save File"):
        with open(new_file, "w") as f:
            f.write(content)
        st.success("Saved!")
