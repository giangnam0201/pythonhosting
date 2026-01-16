import streamlit as st
import subprocess
import sys
import threading
import time
import io
import os
import psutil  # New dependency for Resource Monitor
from contextlib import redirect_stdout

# --- 1. CONFIG & HUD ---
st.set_page_config(page_title="NEXUS-OS V3", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #000000; color: #00ff41; }
    section[data-testid="stSidebar"] { background-color: #050505 !important; border-right: 2px solid #00ff41; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #0a0a0a !important; color: #00ff41 !important;
        border: 1px solid #00ff41 !important; font-family: 'Consolas', monospace !important;
    }
    .stButton>button { 
        background-color: #00ff41 !important; color: black !important; 
        font-weight: bold; border-radius: 2px; border: none; 
    }
    .stMetric { background-color: #111; border: 1px solid #333; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURITY ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("📟 NEXUS GATEWAY")
    if st.text_input("ACCESS KEY", type="password") == "Copilot":
        if st.button("CONNECT"):
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. SYSTEM STATE ---
if 'logs' not in st.session_state: st.session_state.logs = []
if 'bg_tasks' not in st.session_state: st.session_state.bg_tasks = {}

# --- 4. SIDEBAR HUD ---
with st.sidebar:
    st.title("🛰️ SYSTEM HUD")
    
    # Resource Monitor
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    st.metric("CPU LOAD", f"{cpu}%")
    st.metric("RAM USAGE", f"{ram}%")
    
    st.divider()
    app_mode = st.radio("NAVIGATE", ["TERMINAL", "FILES", "PIP", "TASKS"])
    
    if st.button("🧨 EMERGENCY REBOOT"):
        st.session_state.logs = []
        st.session_state.bg_tasks = {}
        st.rerun()

# --- 5. CORE MODULES ---

if app_mode == "TERMINAL":
    st.subheader("📟 CORE SHELL")
    
    # Mode Selector
    mode = st.radio("Interpreter", ["Python", "Bash/Shell"], horizontal=True)
    
    # Output Display
    log_text = "\n".join(st.session_state.logs[-20:])
    st.code(log_text if log_text else "--- SYSTEM IDLE ---", language="bash")
    
    # Command Input
    cmd = st.text_input("EXECUTE COMMAND", key="cmd_in")
    if st.button("SEND") and cmd:
        if mode == "Bash/Shell":
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            out = res.stdout if res.stdout else res.stderr
            st.session_state.logs.append(f"$ {cmd}\n{out}")
        else:
            f = io.StringIO()
            try:
                with redirect_stdout(f):
                    exec(cmd)
                st.session_state.logs.append(f">>> {cmd}\n{f.getvalue()}")
            except Exception as e:
                st.session_state.logs.append(f"!! ERROR: {str(e)}")
        st.rerun()

elif app_mode == "FILES":
    st.subheader("📁 NEXUS EXPLORER")
    path = st.text_input("Path", value=".")
    files = os.listdir(path)
    
    selected_file = st.selectbox("Select File to Edit", [""] + files)
    if selected_file:
        full_path = os.path.join(path, selected_file)
        try:
            with open(full_path, "r") as f:
                content = f.read()
            new_content = st.text_area("Edit Content", value=content, height=300)
            if st.button("💾 SAVE CHANGES"):
                with open(full_path, "w") as f:
                    f.write(new_content)
                st.success("File Overwritten Successfully.")
        except:
            st.error("Cannot edit this file type.")

elif app_mode == "PIP":
    st.subheader("📦 PACKAGE INJECTOR")
    pkg = st.text_input("Package Name")
    if st.button("INSTALL"):
        res = subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True, text=True)
        st.code(res.stdout)

elif app_mode == "TASKS":
    st.subheader("⚙️ BACKGROUND NODES")
    t_name = st.text_input("Task ID")
    t_code = st.text_area("Python Loop (Keep-Alive)", value="while True:\n    pass")
    
    if st.button("🚀 DEPLOY THREAD"):
        # This thread runs in the background of the Streamlit server
        def bg_worker(code):
            try: exec(code)
            except: pass
            
        thread = threading.Thread(target=bg_worker, args=(t_code,), daemon=True)
        thread.start()
        st.session_state.bg_tasks[t_name] = "RUNNING"
        st.success(f"Task {t_name} is now persistent.")
    
    st.write(st.session_state.bg_tasks)
