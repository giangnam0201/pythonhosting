import streamlit as st
import subprocess
import sys
import threading
import time
import io
import os

# --- 1. CONFIG & ULTRA-DARK UI ---
st.set_page_config(page_title="NEXUS-OS V2", layout="wide")

# Custom CSS for the "Freaking Beautiful" look
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: radial-gradient(circle, #1a1a1a 0%, #000000 100%);
        color: #00ff41;
    }
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 1px solid #00ff41;
    }
    /* Input Boxes */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #000000 !important;
        color: #00ff41 !important;
        border: 1px solid #00ff41 !important;
        font-family: 'Courier New', monospace !important;
    }
    /* Buttons */
    .stButton>button {
        background-color: #00ff41 !important;
        color: black !important;
        font-weight: bold !important;
        border: none !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        box-shadow: 0 0 15px #00ff41;
        transform: scale(1.02);
    }
    /* Logs and Code */
    code { color: #00ff41 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURITY GATE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("📟 SYSTEM_RESTRICTED")
    passwd = st.text_input("ENTER ACCESS KEY", type="password")
    if st.button("AUTHENTICATE"):
        if passwd == "Copilot":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("INVALID KEY. ACCESS LOGGED.")
    st.stop()

# --- 3. SESSION INITIALIZATION ---
if 'processes' not in st.session_state:
    st.session_state.processes = {}
if 'terminal_out' not in st.session_state:
    st.session_state.terminal_out = ["--- NEXUS SHELL READY ---"]

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("📡 NEXUS CORE")
    app_mode = st.selectbox("SELECT MODULE", 
        ["Terminal", "Background Apps", "File System", "Pip Lab"])
    
    st.divider()
    st.write("🌍 **Server Node:** Streamlit Cloud")
    st.write(f"🐍 **Python:** {sys.version.split()[0]}")
    if st.button("💀 NUKE ALL PROCESSES"):
        st.session_state.processes = {}
        st.rerun()

# --- 5. FUNCTIONAL MODULES ---

# MODULE: Terminal (The Interactive Feature)
if app_mode == "Terminal":
    st.subheader("📟 Interactive Command Line")
    
    # Display the rolling log
    log_display = "\n".join(st.session_state.terminal_out[-15:]) # Show last 15 lines
    st.code(log_display, language="bash")
    
    # Input area
    col_cmd, col_btn = st.columns([4, 1])
    with col_cmd:
        cmd_input = st.text_input("NEXUS@ROOT:~#", key="terminal_input", placeholder="Enter bash or python command...")
    with col_btn:
        run_cmd = st.button("EXECUTE")

    if run_cmd and cmd_input:
        # Check if it's a bash command or python code
        if cmd_input.startswith("!"): # Bash mode
            res = subprocess.run(cmd_input[1:], shell=True, capture_output=True, text=True)
            output = res.stdout if res.stdout else res.stderr
            st.session_state.terminal_out.append(f"> {cmd_input}\n{output}")
        else: # Python mode
            buffer = io.StringIO()
            try:
                with io.redirect_stdout(buffer):
                    exec(cmd_input)
                st.session_state.terminal_out.append(f">>> {cmd_input}\n{buffer.getvalue()}")
            except Exception as e:
                st.session_state.terminal_out.append(f"ERR: {str(e)}")
        st.rerun()

# MODULE: Background Apps (Keep-Alive)
elif app_mode == "Background Apps":
    st.subheader("⚙️ Keep-Alive Process Manager")
    
    app_name = st.text_input("App Name", value="My_Worker_App")
    app_code = st.text_area("Worker Script (Python Loop)", height=200, 
                           value="import time\nwhile True:\n    with open('log.txt', 'a') as f:\n        f.write('App Running...\\n')\n    time.sleep(60)")
    
    if st.button("🚀 DEPLOY BACKGROUND THREAD"):
        # We use a simple thread to keep it alive during the session
        t = threading.Thread(target=exec, args=(app_code,), daemon=True)
        t.start()
        st.session_state.processes[app_name] = {"status": "ALIVE", "start": time.ctime()}
        st.success(f"App '{app_name}' launched in background.")

    st.divider()
    st.write("### Active Nodes")
    st.write(st.session_state.processes)

# MODULE: File System
elif app_mode == "File System":
    st.subheader("📁 System Explorer")
    path = st.text_input("Directory Path", value=".")
    if os.path.exists(path):
        files = os.listdir(path)
        for f in files:
            col1, col2 = st.columns([3, 1])
            col1.write(f"📄 {f}")
            if col2.button("Read", key=f):
                try:
                    with open(os.path.join(path, f), 'r') as file:
                        st.code(file.read())
                except:
                    st.error("Cannot read binary/large file.")

# MODULE: Pip Lab
elif app_mode == "Pip Lab":
    st.subheader("📦 Package Laboratory")
    pkg = st.text_input("Install Library", placeholder="e.g. requests scikit-learn")
    if st.button("INSTALL"):
        with st.spinner("Injecting Package..."):
            res = subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True, text=True)
            st.code(res.stdout)
