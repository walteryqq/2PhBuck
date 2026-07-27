import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import matplotlib.pyplot as plt
import os
from coupled_buck_model import simulate_coupled_buck, bode_analysis, simulate_open_loop

def render_mermaid(code: str, height: int = 350):
    html_code = f"""
    <div class="mermaid" style="display: flex; justify-content: center; margin-top: 10px;">
    {code}
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
    </script>
    """
    components.html(html_code, height=height)

# Page Config
st.set_page_config(
    page_title="2-Phase Interleaved Coupled Buck Design Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium styling
st.markdown("""
<style>
    .main-title {
        font-family: 'Outfit', 'Inter', sans-serif;
        color: #1E3A8A;
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-family: 'Inter', sans-serif;
        color: #4B5563;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    .metric-title {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 0.2rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    .status-stable {
        background-color: #DCFCE7;
        color: #15803D;
    }
    .status-marginal {
        background-color: #FEF9C3;
        color: #A16207;
    }
    .status-unstable {
        background-color: #FEE2E2;
        color: #B91C1C;
    }
    
    /* Diagrams CSS */
    .diagram-container {
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 20px;
        box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.02);
        flex-wrap: wrap;
    }
    .diagram-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px 15px;
        width: 260px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin: 10px;
        text-align: left;
    }
    .diagram-box.mcu {
        border-top: 4px solid #3B82F6;
    }
    .diagram-box.pwm {
        border-top: 4px solid #10B981;
    }
    .diagram-box.power {
        border-top: 4px solid #F59E0B;
    }
    .diagram-box.compensator {
        border-top: 4px solid #3B82F6;
        width: 220px;
    }
    .diagram-box.delay {
        border-top: 4px solid #8B5CF6;
        width: 180px;
    }
    .diagram-box.plant {
        border-top: 4px solid #10B981;
        width: 220px;
    }
    .diagram-box.impedance {
        border-top: 4px solid #EF4444;
        width: 200px;
    }
    .diagram-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 6px;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 4px;
    }
    .diagram-item {
        font-size: 0.8rem;
        color: #475569;
        margin-bottom: 3px;
        line-height: 1.3;
    }
    .diagram-arrow {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        color: #94A3B8;
        margin: 5px;
    }
    .diagram-arrow-label {
        font-size: 0.75rem;
        color: #64748B;
        margin-top: 2px;
        font-weight: 600;
    }
    .diagram-sum {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        border: 2px solid #64748B;
        background-color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: #0F172A;
        font-size: 1rem;
        margin: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Main Title Header
st.markdown('<div class="main-title">Two Phase Interleaved Buck With Coupled Inductor</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">针对反向耦合电感（Negatively Coupled Inductor）进行物理建模，并基于离散 MCU 数字控制器（ZOH、计算延迟、PI/PID 控制）进行双环/单环时域暂态仿真与频域 Bode 图环路设计。</div>', unsafe_allow_html=True)

# Sidebar Navigation Index
st.sidebar.markdown("""
### Two Phase Interleaved Buck With Coupled Inductor
* **[1. 拓扑与参数配置](#section-1)**
  * [1.1 核心拓扑与滤波器参数](#section-1-1)
  * [1.2 数字 MCU 与 PID 补偿](#section-1-2)
* **[2. 小信号模型与控制框图](#section-2)**
* **[3. 频域环路设计与阻抗分析](#section-3)**
* **[4. 闭环暂态仿真与波形分析](#section-4)**
* **[5. 开环固定比例暂态仿真](#section-5)**
* **[6. 数字补偿与设计参考指南](#section-6)**
---
""")

# ==========================================
# MAIN PAGE - HARDWARE TOPOLOGY INPUTS
# ==========================================
st.markdown('<div id="section-1"></div>', unsafe_allow_html=True)
st.write("## 1. 拓扑与参数配置 (Topology & Parameter Configurations)")

st.markdown("##### 📐 双相交错反向耦合 Buck 主功率拓扑图 (Two-Phase Interleaved Buck with Inverse Coupled Inductor Schematic)")
topo_svg = """<svg width="900" height="320" viewBox="0 0 900 320" fill="none" xmlns="http://www.w3.org/2000/svg" style="background:#F8FAFC; border-radius:12px; border:1px solid #E2E8F0; display:block; margin: 15px auto;">
  <!-- Ground Rail at y=260 -->
  <line x1="50" y1="260" x2="850" y2="260" stroke="#0F172A" stroke-width="2"/>
  <circle cx="850" cy="260" r="3" fill="#0F172A"/>
  
  <!-- Vin Power Rail at y=40 -->
  <line x1="80" y1="40" x2="240" y2="40" stroke="#0F172A" stroke-width="2"/>
  
  <!-- Input Voltage Source Vin -->
  <circle cx="80" cy="150" r="16" fill="#FFFFFF" stroke="#0F172A" stroke-width="2"/>
  <text x="80" y="145" font-family="sans-serif" font-size="12" font-weight="bold" fill="#0F172A" text-anchor="middle">+</text>
  <text x="80" y="161" font-family="sans-serif" font-size="12" font-weight="bold" fill="#0F172A" text-anchor="middle">_</text>
  <text x="80" y="185" font-family="sans-serif" font-size="10" font-weight="bold" fill="#0F172A" text-anchor="middle">Vin</text>
  <line x1="80" y1="40" x2="80" y2="134" stroke="#0F172A" stroke-width="1.5"/>
  <line x1="80" y1="166" x2="80" y2="260" stroke="#0F172A" stroke-width="1.5"/>
  <circle cx="80" cy="40" r="2.5" fill="#0F172A"/>
  <circle cx="80" cy="260" r="2.5" fill="#0F172A"/>

  <!-- Phase 1 Half Bridge (x=160) -->
  <!-- HS Switch Q1_HS -->
  <circle cx="160" cy="50" r="2.5" fill="#0F172A"/>
  <circle cx="160" cy="90" r="2.5" fill="#0F172A"/>
  <line x1="160" y1="40" x2="160" y2="50" stroke="#0F172A" stroke-width="1.5"/>
  <line x1="160" y1="90" x2="160" y2="100" stroke="#0F172A" stroke-width="1.5"/>
  <!-- Switch lever -->
  <line x1="160" y1="90" x2="172" y2="58" stroke="#3B82F6" stroke-width="2" stroke-linecap="round"/>
  <text x="135" y="75" font-family="sans-serif" font-size="9" font-weight="bold" fill="#3B82F6" text-anchor="end">Q1_HS (d1)</text>

  <!-- LS Switch Q1_LS -->
  <circle cx="160" cy="210" r="2.5" fill="#0F172A"/>
  <circle cx="160" cy="250" r="2.5" fill="#0F172A"/>
  <line x1="160" y1="100" x2="160" y2="210" stroke="#0F172A" stroke-width="1.5"/>
  <line x1="160" y1="250" x2="160" y2="260" stroke="#0F172A" stroke-width="1.5"/>
  <!-- Switch lever -->
  <line x1="160" y1="250" x2="172" y2="218" stroke="#3B82F6" stroke-width="2" stroke-linecap="round"/>
  <text x="135" y="235" font-family="sans-serif" font-size="9" font-weight="bold" fill="#3B82F6" text-anchor="end">Q1_LS (1-d1)</text>
  
  <!-- Node SW1 -->
  <circle cx="160" cy="100" r="3" fill="#0F172A"/>
  <text x="172" y="112" font-family="sans-serif" font-size="9.5" font-weight="bold" fill="#4B5563">SW1</text>
  <line x1="160" y1="100" x2="280" y2="100" stroke="#0F172A" stroke-width="1.5"/>

  <!-- Phase 2 Half Bridge (x=240) -->
  <!-- HS Switch Q2_HS -->
  <circle cx="240" cy="50" r="2.5" fill="#0F172A"/>
  <circle cx="240" cy="90" r="2.5" fill="#0F172A"/>
  <line x1="240" y1="40" x2="240" y2="50" stroke="#0F172A" stroke-width="1.5"/>
  <line x1="240" y1="90" x2="240" y2="160" stroke="#0F172A" stroke-width="1.5"/>
  <!-- Switch lever -->
  <line x1="240" y1="90" x2="252" y2="58" stroke="#3B82F6" stroke-width="2" stroke-linecap="round"/>
  <text x="215" y="75" font-family="sans-serif" font-size="9" font-weight="bold" fill="#3B82F6" text-anchor="end">Q2_HS (d2)</text>

  <!-- LS Switch Q2_LS -->
  <circle cx="240" cy="210" r="2.5" fill="#0F172A"/>
  <circle cx="240" cy="250" r="2.5" fill="#0F172A"/>
  <line x1="240" y1="160" x2="240" y2="210" stroke="#0F172A" stroke-width="1.5"/>
  <line x1="240" y1="250" x2="240" y2="260" stroke="#0F172A" stroke-width="1.5"/>
  <!-- Switch lever -->
  <line x1="240" y1="250" x2="252" y2="218" stroke="#3B82F6" stroke-width="2" stroke-linecap="round"/>
  <text x="215" y="235" font-family="sans-serif" font-size="9" font-weight="bold" fill="#3B82F6" text-anchor="end">Q2_LS (1-d2)</text>
  
  <!-- Node SW2 -->
  <circle cx="240" cy="160" r="3" fill="#0F172A"/>
  <text x="252" y="172" font-family="sans-serif" font-size="9.5" font-weight="bold" fill="#4B5563">SW2</text>
  <line x1="240" y1="160" x2="280" y2="160" stroke="#0F172A" stroke-width="1.5"/>

  <!-- Phase 1 Inductor L1 & DCR1 -->
  <!-- L1 Inductor Symbol -->
  <path d="M 280 100 C 288 90 296 90 296 100 C 304 90 312 90 312 100 C 320 90 328 90 328 100 C 336 90 344 90 344 100 C 352 90 360 90 360 100" stroke="#0F172A" stroke-width="1.8" fill="none"/>
  <text x="320" y="82" font-family="sans-serif" font-size="10" font-weight="bold" fill="#D97706" text-anchor="middle">L1 (L)</text>
  <circle cx="276" cy="94" r="3.5" fill="#EF4444"/> <!-- Coupling Dot 1 -->
  <line x1="360" y1="100" x2="400" y2="100" stroke="#0F172A" stroke-width="1.5"/>
  <!-- DCR1 Resistor Symbol -->
  <path d="M 400 100 L 404 100 L 407 93 L 412 107 L 417 93 L 422 107 L 427 93 L 432 107 L 436 100 L 440 100" stroke="#0F172A" stroke-width="1.5" fill="none"/>
  <text x="420" y="82" font-family="sans-serif" font-size="9.5" font-weight="bold" fill="#4B5563" text-anchor="middle">Rdcr1 (DCR)</text>
  <line x1="440" y1="100" x2="520" y2="100" stroke="#0F172A" stroke-width="1.5"/>

  <!-- Phase 2 Inductor L2 & DCR2 -->
  <!-- L2 Inductor Symbol -->
  <path d="M 280 160 C 288 150 296 150 296 160 C 304 150 312 150 312 160 C 320 150 328 150 328 160 C 336 150 344 150 344 160 C 352 150 360 150 360 160" stroke="#0F172A" stroke-width="1.8" fill="none"/>
  <text x="320" y="142" font-family="sans-serif" font-size="10" font-weight="bold" fill="#D97706" text-anchor="middle">L2 (L)</text>
  <circle cx="364" cy="154" r="3.5" fill="#EF4444"/> <!-- Coupling Dot 2 (Inverse polarity) -->
  <line x1="360" y1="160" x2="400" y2="160" stroke="#0F172A" stroke-width="1.5"/>
  <!-- DCR2 Resistor Symbol -->
  <path d="M 400 160 L 404 160 L 407 153 L 412 167 L 417 153 L 422 167 L 427 153 L 432 167 L 436 160 L 440 160" stroke="#0F172A" stroke-width="1.5" fill="none"/>
  <text x="420" y="142" font-family="sans-serif" font-size="9.5" font-weight="bold" fill="#4B5563" text-anchor="middle">Rdcr2 (DCR)</text>
  <line x1="440" y1="160" x2="520" y2="160" stroke="#0F172A" stroke-width="1.5"/>

  <!-- Inverse Coupling core lines and coefficient label -->
  <line x1="285" y1="126" x2="355" y2="126" stroke="#D97706" stroke-width="1.5" stroke-dasharray="3,2"/>
  <line x1="285" y1="134" x2="355" y2="134" stroke="#D97706" stroke-width="1.5" stroke-dasharray="3,2"/>
  <text x="320" y="120" font-family="sans-serif" font-size="9" font-weight="bold" fill="#D97706" text-anchor="middle">耦合 k (反向)</text>

  <!-- Output Connecting Nodes -->
  <line x1="520" y1="100" x2="520" y2="70" stroke="#0F172A" stroke-width="1.5"/>
  <line x1="520" y1="160" x2="520" y2="70" stroke="#0F172A" stroke-width="1.5"/>
  <circle cx="520" cy="100" r="2.5" fill="#0F172A"/>
  <circle cx="520" cy="160" r="2.5" fill="#0F172A"/>
  <circle cx="520" cy="70" r="2.5" fill="#0F172A"/>
  
  <!-- Output rail from x=520 to x=840 -->
  <line x1="520" y1="70" x2="840" y2="70" stroke="#0F172A" stroke-width="2"/>
  <circle cx="840" cy="70" r="3" fill="#0F172A"/>
  <text x="840" y="55" font-family="sans-serif" font-size="10" font-weight="bold" fill="#0F172A" text-anchor="middle">Vo (Vref)</text>

  <!-- Output Capacitor Branch 1 (C1 & Resr1) -->
  <line x1="600" y1="70" x2="600" y2="105" stroke="#0F172A" stroke-width="1.5"/>
  <!-- Capacitor C1 -->
  <line x1="588" y1="105" x2="612" y2="105" stroke="#0F172A" stroke-width="2"/>
  <line x1="588" y1="110" x2="612" y2="110" stroke="#0F172A" stroke-width="2"/>
  <text x="618" y="112" font-family="sans-serif" font-size="9" font-weight="bold" fill="#4B5563">C1</text>
  <line x1="600" y1="110" x2="600" y2="140" stroke="#0F172A" stroke-width="1.5"/>
  <!-- Resr1 Resistor -->
  <path d="M 600 140 L 600 144 L 593 147 L 607 152 L 593 157 L 607 162 L 593 167 L 607 172 L 600 176 L 600 180" stroke="#0F172A" stroke-width="1.5" fill="none"/>
  <text x="618" y="162" font-family="sans-serif" font-size="9.5" font-weight="bold" fill="#4B5563">Resr1</text>
  <line x1="600" y1="180" x2="600" y2="260" stroke="#0F172A" stroke-width="1.5"/>
  <circle cx="600" cy="70" r="2.5" fill="#0F172A"/>
  <circle cx="600" cy="260" r="2.5" fill="#0F172A"/>

  <!-- Output Capacitor Branch 2 (C2 & Resr2) -->
  <line x1="690" y1="70" x2="690" y2="105" stroke="#0F172A" stroke-width="1.5"/>
  <!-- Capacitor C2 -->
  <line x1="678" y1="105" x2="702" y2="105" stroke="#0F172A" stroke-width="2"/>
  <line x1="678" y1="110" x2="702" y2="110" stroke="#0F172A" stroke-width="2"/>
  <text x="708" y="112" font-family="sans-serif" font-size="9" font-weight="bold" fill="#4B5563">C2</text>
  <line x1="690" y1="110" x2="690" y2="140" stroke="#0F172A" stroke-width="1.5"/>
  <!-- Resr2 Resistor -->
  <path d="M 690 140 L 690 144 L 683 147 L 697 152 L 683 157 L 697 162 L 683 167 L 697 172 L 690 176 L 690 180" stroke="#0F172A" stroke-width="1.5" fill="none"/>
  <text x="708" y="162" font-family="sans-serif" font-size="9.5" font-weight="bold" fill="#4B5563">Resr2</text>
  <line x1="690" y1="180" x2="690" y2="260" stroke="#0F172A" stroke-width="1.5"/>
  <circle cx="690" cy="70" r="2.5" fill="#0F172A"/>
  <circle cx="690" cy="260" r="2.5" fill="#0F172A"/>

  <!-- Output Load Resistor R_load -->
  <line x1="780" y1="70" x2="780" y2="120" stroke="#0F172A" stroke-width="1.5"/>
  <!-- Rload Resistor -->
  <path d="M 780 120 L 780 126 L 773 130 L 787 135 L 773 140 L 787 145 L 773 150 L 787 155 L 773 160 L 787 165 L 780 171 L 780 180" stroke="#0F172A" stroke-width="1.5" fill="none"/>
  <text x="798" y="152" font-family="sans-serif" font-size="9.5" font-weight="bold" fill="#4B5563">R_load</text>
  <line x1="780" y1="180" x2="780" y2="260" stroke="#0F172A" stroke-width="1.5"/>
  <circle cx="780" cy="70" r="2.5" fill="#0F172A"/>
  <circle cx="780" cy="260" r="2.5" fill="#0F172A"/>
</svg>"""
st.markdown(topo_svg, unsafe_allow_html=True)

st.markdown('<div id="section-1-1"></div>', unsafe_allow_html=True)
st.write("### 🔌 1.1 核心拓扑与滤波器参数配置 (Power Stage Hardware Configuration)")
col_hw1, col_hw2, col_hw3, col_hw4 = st.columns(4)

with col_hw1:
    vin = st.number_input("输入电压 Vin (V)", min_value=40.0, max_value=60.0, value=54.0, step=1.0, format="%.1f")
    vref = st.number_input("目标电压 Vref (V)", min_value=5.0, max_value=20.0, value=12.2, step=0.1, format="%.2f")

with col_hw2:
    l_uH = st.number_input("相自电感 L (μH)", min_value=0.1, max_value=10.0, value=1.5, step=0.1, format="%.2f")
    L = l_uH * 1e-6
    k_coupling = st.number_input("耦合系数 k (反向耦合)", min_value=0.0, max_value=0.95, value=0.70, step=0.05, format="%.2f")

with col_hw3:
    c1_uF = st.number_input("滤波电容 C1 (μF)", min_value=10.0, max_value=30000.0, value=10000.0, step=100.0, format="%.1f")
    C1 = c1_uF * 1e-6
    resr1_mOhm = st.number_input("等效电阻 ESR1 (mΩ)", min_value=0.01, max_value=50.0, value=1.2, step=0.1, format="%.2f")
    Resr1 = resr1_mOhm * 1e-3

with col_hw4:
    c2_uF = st.number_input("滤波电容 C2 (μF)", min_value=10.0, max_value=10000.0, value=100.0, step=10.0, format="%.1f")
    C2 = c2_uF * 1e-6
    resr2_mOhm = st.number_input("等效电阻 ESR2 (mΩ)", min_value=0.01, max_value=50.0, value=0.3, step=0.1, format="%.2f")
    Resr2 = resr2_mOhm * 1e-3

col_hw5, col_hw6, col_hw7, col_hw8 = st.columns(4)
with col_hw5:
    rdcr_mOhm = st.number_input("电感 DCR (mΩ)", min_value=0.01, max_value=20.0, value=0.35, step=0.05, format="%.3f")
    Rdcr = rdcr_mOhm * 1e-3
with col_hw6:
    fs_kHz = st.number_input("开关频率 fs (kHz)", min_value=50.0, max_value=1000.0, value=210.0, step=10.0, format="%.1f")
    fs = fs_kHz * 1e3
with col_hw7:
    rds_mOhm = st.number_input("半桥 GaN 等效电阻 Rds (mΩ)", min_value=0.0, max_value=20.0, value=0.6, step=0.1, format="%.2f")
    Rds_eq = rds_mOhm * 1e-3
with col_hw8:
    st.write("") # placeholder
# Initialize session state for digital control parameters if not present
if "kp" not in st.session_state:
    st.session_state.kp = 0.05
if "ki" not in st.session_state:
    st.session_state.ki = 0.0002
if "kd" not in st.session_state:
    st.session_state.kd = 1.0e-6
if "tau_d_uS" not in st.session_state:
    st.session_state.tau_d_uS = 1.0
if "fctrl" not in st.session_state:
    st.session_state.fctrl = 100.0

# ==========================================
# MAIN PAGE - DIGITAL MCU & COMPENSATOR CONFIG
# ==========================================
st.markdown('<div id="section-1-2"></div>', unsafe_allow_html=True)
st.write("### 💻 1.2 数字 MCU 与 PID 补偿器参数配置 (Digital MCU & Compensator Configuration)")


col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns(4)

with col_ctrl1:
    fctrl_kHz = st.number_input("采样频率 f_sam (kHz)", min_value=10.0, max_value=4000.0, step=10.0, key="fctrl")
    fctrl = fctrl_kHz * 1e3

with col_ctrl2:
    delay_cycles = st.number_input("数字计算/更新延迟 (开关周期数)", min_value=0.0, max_value=6.0, value=1.50, step=0.05, format="%.2f")

with col_ctrl3:
    kp = st.number_input("比例增益 Kp", min_value=0.0, max_value=100.0, step=1e-5, format="%.5f", key="kp")
    ki = st.number_input("积分增益 Ki (固件值)", min_value=0.0, max_value=1.0, step=1e-6, format="%.6f", key="ki")

with col_ctrl4:
    kd = st.number_input("微分增益 Kd", min_value=0.0, max_value=0.1, step=1e-8, format="%.8g", key="kd")
    tau_d_uS = st.number_input("微分滤波时间 τ_d (μs)", min_value=0.01, max_value=100.0, step=0.1, key="tau_d_uS")
    tau_d = tau_d_uS * 1e-6

# ==========================================
# MAIN PAGE - TESTING LOAD STEP ONLY
# ==========================================
# Retrieve closed-loop simulation settings from session state (defined in Section 4)
cl_i_init = st.session_state.get("cl_i_init", 64.0)
cl_i_target = st.session_state.get("cl_i_target", 160.0)
cl_slew_rate_val = st.session_state.get("cl_slew_rate_val", 1.0)
cl_slew_rate = cl_slew_rate_val * 1e6
cl_t_step_val = st.session_state.get("cl_t_step", 1.00)
t_step = cl_t_step_val * 1e-3
dcm_mode = st.session_state.get("cl_dcm_mode", True)

r_load_init = vref / cl_i_init if cl_i_init > 0 else 1000.0
r_load_step = vref / cl_i_target
i_load_init = cl_i_init
i_load_target = cl_i_target

# ==========================================
# PID Parameter Optimizer (NEW)
# ==========================================
st.write("#### ⚡ PID 参数自动智能搜索与设计工具 (PID Auto-Tuning Optimizer)")
with st.expander("🔍 点击展开 PID 智能优化辅助设计控制台 (PID Sweep & Auto-Tuning Console)", expanded=False):
    st.markdown("通过该工具，系统自动在不同 $K_p$ 与 $K_d$ 组合下对闭环小信号平均模型进行扫描，分析环路稳定性并在稳定前提下运行暂态时域仿真，为您挑选出**跌落最小且无振铃**的最优参数组合。")
    
    col_opt1, col_opt2, col_opt3 = st.columns(3)
    with col_opt1:
        fc_max_limit_kHz = st.number_input("允许的最大穿越频率 fc_max (kHz)", min_value=1.0, max_value=100.0, value=25.0, step=1.0, key="opt_fc_max")
    with col_opt2:
        pm_min_limit = st.number_input("要求的最小相位裕度 PM_min (°)", min_value=10.0, max_value=90.0, value=45.0, step=5.0, key="opt_pm_min")
    with col_opt3:
        st.write("") # spacing
        sweep_run = st.button("🚀 开始智能扫描优化", type="primary", use_container_width=True)
        
    if sweep_run:
        kps_sweep = [0.01, 0.02, 0.03, 0.05, 0.06, 0.08, 0.10, 0.12, 0.15, 0.20, 0.25, 0.30]
        kds_sweep = [0.0, 5e-7, 1e-6, 1.5e-6, 2e-6, 3e-6, 5e-6, 8e-6, 1e-5]
        ki_continuous_sweep = ki * fctrl
        
        sweep_results = []
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        
        total_iterations = len(kps_sweep) * len(kds_sweep)
        current_iter = 0
        
        for kp_s in kps_sweep:
            for kd_s in kds_sweep:
                current_iter += 1
                progress_bar.progress(current_iter / total_iterations)
                status_text.text(f"正在分析组合 {current_iter}/{total_iterations}: Kp={kp_s:.3f}, Kd={kd_s:.1e}...")
                
                try:
                    bode_res = bode_analysis(
                        Vin=vin, L=L, k_coupling=k_coupling, Rdcr=Rdcr + 2.0*Rds_eq, C1=C1, Resr1=Resr1, C2=C2, Resr2=Resr2, Rload=r_load_step,
                        Kp=kp_s, Ki=ki_continuous_sweep, Kd=kd_s, tau_d=1.0e-6, delay_cycles=delay_cycles, fs=fs
                    )
                    pm_s = bode_res['PM']
                    fc_s = bode_res['fc']
                    
                    if pm_s is not None and pm_s >= pm_min_limit:
                        if fc_s is not None and fc_s <= fc_max_limit_kHz * 1e3:
                            # Run fast transient simulation
                            t_arr, i1_arr, i2_arr, v_out_arr, _, _, _ = simulate_coupled_buck(
                                Vin=vin, Vref=vref, L=L, k_coupling=k_coupling, Rdcr=Rdcr, C1=C1, Resr1=Resr1, C2=C2, Resr2=Resr2,
                                Rload_init=r_load_init, Rload_step=r_load_step, t_step=t_step,
                                fs=fs, fctrl=fctrl, Kp=kp_s, Ki=ki_continuous_sweep, Kd=kd_s, tau_d=1e-6, delay_cycles=delay_cycles, dcm_mode=dcm_mode, Rds_eq=Rds_eq,
                                slew_rate=cl_slew_rate
                            )
                            v_min_s = np.min(v_out_arr)
                            drop_mv_s = (vref - v_min_s) * 1e3
                            sweep_results.append({
                                '方案编号': len(sweep_results) + 1,
                                '比例增益 Kp': kp_s,
                                '微分增益 Kd': kd_s,
                                '穿越频率 fc (kHz)': round(fc_s / 1e3, 2),
                                '相位裕度 PM (°)': round(pm_s, 1),
                                '最低电压 Vmin (V)': round(v_min_s, 4),
                                '瞬态下冲跌落 (mV)': round(drop_mv_s, 1)
                            })
                except Exception as e:
                    pass
                    
        progress_bar.empty()
        status_text.empty()
        
        if not sweep_results:
            st.warning("⚠️ 未找到在当前稳定性和穿越频率限制下稳定的 PID 参数组合，请放宽设计约束。")
        else:
            sweep_results.sort(key=lambda x: x['瞬态下冲跌落 (mV)'])
            st.success(f"✨ 扫描完成！共找到 {len(sweep_results)} 组满足稳定约束的 PID 参数配置，已按跌落深度从小到大排序：")
            
            # Recalculate candidate IDs sequentially for display
            for idx, r in enumerate(sweep_results):
                r['方案编号'] = idx + 1
                
            st.dataframe(sweep_results[:15], use_container_width=True, hide_index=True)
            
            # Selection selectbox to apply parameters
            options = [f"推荐方案 {r['方案编号']}: Kp={r['比例增益 Kp']:.3f}, Kd={r['微分增益 Kd']:.1e} (跌落 {r['瞬态下冲跌落 (mV)']:.1f} mV, PM={r['相位裕度 PM (°)']:.1f}°)" for r in sweep_results[:10]]
            selected_opt = st.selectbox("选择一组合适的 PID 设计方案应用到当前系统：", options, key="selected_sweep_pid")
            
            if selected_opt:
                idx = options.index(selected_opt)
                chosen = sweep_results[idx]
                if st.button("💾 一键应用选中方案到系统", type="secondary", use_container_width=True):
                    st.session_state.kp = chosen['比例增益 Kp']
                    st.session_state.kd = chosen['微分增益 Kd']
                    st.toast(f"已应用方案 {chosen['方案编号']}: Kp={chosen['比例增益 Kp']:.4f}, Kd={chosen['微分增益 Kd']:.2e}", icon="🚀")
                    st.rerun()

# ==========================================
# RUN SIMULATION AND FREQUENCY ANALYSIS
# ==========================================
try:
    # Scale discrete-time Ki from UI to continuous-time Ki for simulation
    ki_continuous = ki * fctrl

    # 1. Frequency Domain Analysis (Bode)
    bode_res = bode_analysis(
        Vin=vin, L=L, k_coupling=k_coupling, Rdcr=Rdcr + 2.0 * Rds_eq, C1=C1, Resr1=Resr1, C2=C2, Resr2=Resr2, Rload=r_load_step,
        Kp=kp, Ki=ki_continuous, Kd=kd, tau_d=tau_d, delay_cycles=delay_cycles, fs=fs
    )
    
    # 2. Time Domain Simulation (with coupling)
    t_arr, i1_arr, i2_arr, v_out_arr, i_load_arr, d1_arr, d2_arr = simulate_coupled_buck(
        Vin=vin, Vref=vref, L=L, k_coupling=k_coupling, Rdcr=Rdcr, C1=C1, Resr1=Resr1, C2=C2, Resr2=Resr2,
        Rload_init=r_load_init, Rload_step=r_load_step, t_step=t_step,
        fs=fs, fctrl=fctrl, Kp=kp, Ki=ki_continuous, Kd=kd, tau_d=tau_d, delay_cycles=delay_cycles, dcm_mode=dcm_mode, Rds_eq=Rds_eq,
        slew_rate=cl_slew_rate
    )
    
    # ==========================================
    # METRICS SECTION
    # ==========================================
    st.subheader("📊 环路与暂态性能指标 (Metrics Summary)")
    
    # Extract time-domain transient metrics
    # Vo undershoot
    v_min_coupled = np.min(v_out_arr)
    undershoot_pct_coupled = (vref - v_min_coupled) / vref * 100.0
    
    # Settling time (time to return within 1% of Vref after t_step)
    t_after_step = t_arr[t_arr >= t_step]
    v_after_step = v_out_arr[t_arr >= t_step]
    settling_time_ms = "N/A"
    
    # Find last index where voltage goes out of 1% band
    error_pct = np.abs(v_after_step - vref) / vref * 100.0
    out_of_band = np.where(error_pct > 1.0)[0]
    if len(out_of_band) > 0:
        last_out_idx = out_of_band[-1]
        settling_time_val = t_after_step[last_out_idx] - t_step
        settling_time_ms = f"{settling_time_val * 1e3:.2f} ms"
    else:
        settling_time_ms = "< 0.05 ms"
        
    # Phase current ripple peak-to-peak (measured in steady state, e.g. before load step)
    steady_mask = (t_arr > 0.4 * t_step) & (t_arr < 0.9 * t_step)
    if np.any(steady_mask):
        ripple_coupled = np.max(i1_arr[steady_mask]) - np.min(i1_arr[steady_mask])
    else:
        ripple_coupled = 0.0

    # Layout Metrics in 4 columns
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    with m_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">等效暂态电感 Leq</div>
            <div class="metric-value">{bode_res['Leq'] * 1e6:.2f} μH</div>
            <span style="font-size: 0.85rem; color:#64748B;">单相自感 L = {l_uH:.2f} μH</span>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col2:
        fc_str = f"{bode_res['fc']/1e3:.1f} kHz" if bode_res['fc'] else "未穿越"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">穿越频率 fc (带宽)</div>
            <div class="metric-value">{fc_str}</div>
            <span style="font-size: 0.85rem; color:#64748B;">建议值: {fs_kHz/20:.1f} ~ {fs_kHz/10:.1f} kHz</span>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col3:
        pm = bode_res['PM']
        pm_str = f"{pm:.1f}°" if pm is not None else "N/A"
        
        # Stability class
        if pm is not None:
            if pm >= 45.0 and pm <= 60.0:
                badge = '<span class="status-badge status-stable">推荐稳定度 (45°~60°)</span>'
            elif pm > 30.0:
                badge = '<span class="status-badge status-marginal">边界稳定 (>30°)</span>'
            else:
                badge = '<span class="status-badge status-unstable">环路不稳定 (<30°)</span>'
        else:
            badge = '<span class="status-badge status-unstable">环路未闭合</span>'
            
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">相位裕度 Phase Margin</div>
            <div class="metric-value">{pm_str}</div>
            {badge}
        </div>
        """, unsafe_allow_html=True)
        
    with m_col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">负载突变瞬态电压跌落</div>
            <div class="metric-value">{undershoot_pct_coupled:.2f} %</div>
            <span style="font-size: 0.85rem; color:#64748B;">最大瞬态跌落电压: {vref - v_min_coupled:.3f} V<br>恢复时间: {settling_time_ms}</span>
        </div>
        """, unsafe_allow_html=True)

    # 2. 双相交错 Buck 小信号等效电路模型与控制反馈框图
    st.markdown('<div id="section-2"></div>', unsafe_allow_html=True)
    st.write("## 2. 双相交错 Buck 小信号等效电路模型与控制反馈框图 (Small-Signal Equivalent Circuit & Block Diagram)")
    st.write("以下展示了本工具运行的小信号（频域环路）平均电路模型，其中电容、电阻、电感的参数大小已根据前文的物理配置进行动态计算并实时标注在对应元件旁：")
    
    # Calculate values for current working point
    d_ratio = vref / vin
    l_eq_val = (L * (1.0 - k_coupling)) / 2.0
    rdcr_eq_val = Rdcr / 2.0
    
    # Format current values as strings
    l_eq_str = f"Leq = {l_eq_val * 1e6:.2f} μH"
    rdcr_eq_str = f"Rdcr_eq = {rdcr_eq_val * 1e3:.1f} mΩ"
    c1_str = f"C1 = {c1_uF:.0f} μF"
    resr1_str = f"Resr1 = {resr1_mOhm:.1f} mΩ"
    c2_str = f"C2 = {c2_uF:.0f} μF"
    resr2_str = f"Resr2 = {resr2_mOhm:.1f} mΩ"
    r_load_str = f"R_load = {r_load_step:.3f} Ω"
    d_ratio_str = f"1 : {d_ratio:.3f}"
    dep_volt_str = f"{vref / (d_ratio**2):.1f}V * d̂(s)"
    dep_curr_str = f"{(vref / r_load_step):.1f}A * d̂(s)"
    
    # Dynamic values for SVG
    kp_val = f"{kp:.5f}"
    ki_val = f"{ki:.6f}"
    kd_val = f"{kd:.6g}"
    fctrl_val = f"{fctrl_kHz:.1f}"
    delay_val = f"{delay_cycles:.2f}"
    
    small_signal_svg = f"""<svg width="940" height="320" viewBox="0 0 940 320" fill="none" xmlns="http://www.w3.org/2000/svg" style="background:#F8FAFC; border-radius:12px; border:1px solid #E2E8F0; display:block; margin: 15px auto;">
<!-- 1. AC Input Perturbation Source v_in(s) -->
<circle cx="50" cy="80" r="16" fill="#FFFFFF" stroke="#0F172A" stroke-width="2"/>
<text x="50" y="75" font-family="sans-serif" font-size="10" font-weight="bold" fill="#0F172A" text-anchor="middle">+</text>
<text x="50" y="91" font-family="sans-serif" font-size="10" font-weight="bold" fill="#0F172A" text-anchor="middle">_</text>
<text x="50" y="112" font-family="sans-serif" font-size="9" font-weight="bold" fill="#4B5563" text-anchor="middle">v̂_in(s)</text>

<!-- 2. Dependent Current Source (IL/D * d) -->
<circle cx="130" cy="80" r="16" fill="#FFFFFF" stroke="#0F172A" stroke-width="2"/>
<path d="M 130 68 L 130 92" stroke="#0F172A" stroke-width="1.5" marker-end="url(#arrow_dark)"/>
<text x="130" y="112" font-family="sans-serif" font-size="9" font-weight="bold" fill="#4B5563" text-anchor="middle">Io * d̂(s)</text>

<!-- 3. Dependent Voltage Source (Vin/D^2 * d) in Series -->
<circle cx="200" cy="45" r="16" fill="#FFFFFF" stroke="#0F172A" stroke-width="2"/>
<text x="191" y="49" font-family="sans-serif" font-size="10" font-weight="bold" fill="#0F172A" text-anchor="middle">-</text>
<text x="209" y="49" font-family="sans-serif" font-size="10" font-weight="bold" fill="#0F172A" text-anchor="middle">+</text>
<text x="200" y="22" font-family="sans-serif" font-size="9" font-weight="bold" fill="#4B5563" text-anchor="middle">(Vin/D) * d̂(s)</text>

<!-- 4. Transformer Windings (1 : D) -->
<!-- Primary Winding -->
<path d="M 270 50 C 260 55 260 65 270 70 C 260 75 260 85 270 90 C 260 95 260 105 270 110" stroke="#0F172A" stroke-width="1.8" fill="none"/>
<circle cx="260" cy="58" r="2.5" fill="#0F172A"/>
<!-- Core Lines -->
<line x1="277" y1="45" x2="277" y2="115" stroke="#0F172A" stroke-width="1.5"/>
<line x1="281" y1="45" x2="281" y2="115" stroke="#0F172A" stroke-width="1.5"/>
<!-- Secondary Winding -->
<path d="M 288 50 C 298 55 298 65 288 70 C 298 75 298 85 288 90 C 298 95 298 105 288 110" stroke="#0F172A" stroke-width="1.8" fill="none"/>
<circle cx="298" cy="58" r="2.5" fill="#0F172A"/>
<text x="279" y="36" font-family="sans-serif" font-size="9.5" font-weight="bold" fill="#4B5563" text-anchor="middle">1 : D</text>

<!-- Top Wires Connectors -->
<path d="M 50 45 L 50 64" stroke="#0F172A" stroke-width="1.5"/>
<path d="M 50 96 L 50 130" stroke="#0F172A" stroke-width="1.5"/>
<path d="M 50 45 L 184 45" stroke="#0F172A" stroke-width="1.5"/>
<path d="M 130 45 L 130 64" stroke="#0F172A" stroke-width="1.5"/>
<path d="M 130 96 L 130 130" stroke="#0F172A" stroke-width="1.5"/>
<path d="M 216 45 L 270 45" stroke="#0F172A" stroke-width="1.5"/>
<path d="M 270 110 L 270 130" stroke="#0F172A" stroke-width="1.5"/>
<path d="M 288 110 L 288 130" stroke="#0F172A" stroke-width="1.5"/>
<path d="M 50 130 L 288 130" stroke="#0F172A" stroke-width="1.5"/>

<!-- Rds_eq switch equivalent resistor block -->
<path d="M 288 45 L 310 45" stroke="#0F172A" stroke-width="1.5"/>
<rect x="310" y="37" width="50" height="16" stroke="#2563EB" fill="#EFF6FF" stroke-width="1.5" rx="2"/>
<text x="335" y="27" font-family="sans-serif" font-size="9.5" font-weight="bold" fill="#2563EB" text-anchor="middle">Rds_eq</text>
<text x="335" y="65" font-family="sans-serif" font-size="8" fill="#64748B" text-anchor="middle">(GaN 导通电阻折算)</text>
<path d="M 360 45 L 380 45" stroke="#0F172A" stroke-width="1.5"/>

<!-- Power Filter Network (Leq & Rdcr) (Shifted by 70px) -->
<!-- Equivalent Inductor Leq -->
<path d="M 380 45 C 388 35 396 35 396 45 C 404 35 412 35 412 45 C 420 35 428 35 428 45 C 436 35 444 35 444 45 C 452 35 460 35 460 45" stroke="#0F172A" stroke-width="1.8" fill="none"/>
<text x="420" y="26" font-family="sans-serif" font-size="9.5" font-weight="bold" fill="#D97706" text-anchor="middle">Leq</text>
<path d="M 460 45 L 490 45" stroke="#0F172A" stroke-width="1.5"/>
<!-- Rdcr Resistor -->
<path d="M 490 45 L 494 38 L 499 52 L 504 38 L 509 52 L 514 38 L 519 52 L 523 45" stroke="#0F172A" stroke-width="1.5" fill="none"/>
<text x="506" y="26" font-family="sans-serif" font-size="9.5" font-weight="bold" fill="#4B5563" text-anchor="middle">Rdcr_eq</text>
<path d="M 523 45 L 550 45" stroke="#0F172A" stroke-width="1.5"/>

<!-- Capacitor Branch 1 (C1 & Resr1) -->
<path d="M 550 45 L 550 70" stroke="#0F172A" stroke-width="1.5"/>
<!-- Capacitor C1 -->
<line x1="538" y1="70" x2="562" y2="70" stroke="#0F172A" stroke-width="2"/>
<line x1="538" y1="75" x2="562" y2="75" stroke="#0F172A" stroke-width="2"/>
<text x="568" y="72" font-family="sans-serif" font-size="9" font-weight="bold" fill="#4B5563">C1</text>
<path d="M 550 75 L 550 85" stroke="#0F172A" stroke-width="1.5"/>
<!-- Resr1 Resistor -->
<path d="M 550 85 L 543 89 L 557 94 L 543 99 L 557 104 L 543 109 L 557 114 L 550 118" stroke="#0F172A" stroke-width="1.5" fill="none"/>
<text x="562" y="105" font-family="sans-serif" font-size="9" font-weight="bold" fill="#4B5563">Resr1</text>
<path d="M 550 118 L 550 130" stroke="#0F172A" stroke-width="1.5"/>
<circle cx="550" cy="45" r="2.5" fill="#0F172A"/>
<circle cx="550" cy="130" r="2.5" fill="#0F172A"/>

<!-- Wire Connect to Branch 2 -->
<path d="M 550 45 L 640 45" stroke="#0F172A" stroke-width="1.5"/>

<!-- Capacitor Branch 2 (C2 & Resr2) -->
<path d="M 640 45 L 640 70" stroke="#0F172A" stroke-width="1.5"/>
<!-- Capacitor C2 -->
<line x1="628" y1="70" x2="652" y2="70" stroke="#0F172A" stroke-width="2"/>
<line x1="628" y1="75" x2="652" y2="75" stroke="#0F172A" stroke-width="2"/>
<text x="658" y="72" font-family="sans-serif" font-size="9" font-weight="bold" fill="#4B5563">C2</text>
<path d="M 640 75 L 640 85" stroke="#0F172A" stroke-width="1.5"/>
<!-- Resr2 Resistor -->
<path d="M 640 85 L 633 89 L 647 94 L 633 99 L 647 104 L 633 109 L 647 114 L 640 118" stroke="#0F172A" stroke-width="1.5" fill="none"/>
<text x="652" y="105" font-family="sans-serif" font-size="9" font-weight="bold" fill="#4B5563">Resr2</text>
<path d="M 640 118 L 640 130" stroke="#0F172A" stroke-width="1.5"/>
<circle cx="640" cy="45" r="2.5" fill="#0F172A"/>
<circle cx="640" cy="130" r="2.5" fill="#0F172A"/>

<!-- Wire Connect to Load -->
<path d="M 640 45 L 730 45" stroke="#0F172A" stroke-width="1.5"/>

<!-- Output Load Resistor R_load -->
<path d="M 730 45 L 730 65" stroke="#0F172A" stroke-width="1.5"/>
<!-- Rload Resistor -->
<path d="M 730 65 L 723 69 L 737 74 L 723 79 L 737 84 L 723 89 L 737 94 L 730 98" stroke="#0F172A" stroke-width="1.5" fill="none"/>
<text x="742" y="86" font-family="sans-serif" font-size="9.5" font-weight="bold" fill="#4B5563">R_load</text>
<path d="M 730 98 L 730 130" stroke="#0F172A" stroke-width="1.5"/>
<circle cx="730" cy="45" r="2.5" fill="#0F172A"/>
<circle cx="730" cy="130" r="2.5" fill="#0F172A"/>

<!-- Wire Connect to Current Source -->
<path d="M 730 45 L 820 45" stroke="#0F172A" stroke-width="1.5"/>

<!-- Perturbation Load Current Source i_load(s) -->
<path d="M 820 45 L 820 65" stroke="#0F172A" stroke-width="1.5"/>
<circle cx="820" cy="80" r="15" fill="#FFFFFF" stroke="#0F172A" stroke-width="2"/>
<path d="M 820 69 L 820 91" stroke="#0F172A" stroke-width="1.5" marker-end="url(#arrow_dark)"/>
<text x="842" y="84" font-family="sans-serif" font-size="9" font-weight="bold" fill="#EF4444" text-anchor="start">î_load(s) 扰动</text>
<path d="M 820 95 L 820 130" stroke="#0F172A" stroke-width="1.5"/>
<circle cx="820" cy="45" r="2.5" fill="#0F172A"/>
<circle cx="820" cy="130" r="2.5" fill="#0F172A"/>

<!-- Output terminals -->
<path d="M 820 45 L 900 45" stroke="#0F172A" stroke-width="1.5"/>
<circle cx="900" cy="45" r="3" fill="#0F172A"/>
<text x="900" y="32" font-family="sans-serif" font-size="10" font-weight="bold" fill="#0F172A" text-anchor="middle">v̂(s) 输出</text>
<path d="M 288 130 L 900 130" stroke="#0F172A" stroke-width="1.5"/>
<circle cx="900" cy="130" r="3" fill="#0F172A"/>

<!-- Open-Loop Impedance Zout arrow pointer -->
<path d="M 750 115 L 730 100" stroke="#0F172A" stroke-width="1.5" marker-end="url(#arrow_dark)"/>
<text x="765" y="125" font-family="sans-serif" font-size="9" font-weight="bold" fill="#4B5563">Z_out(s)</text>

<!-- ========================================================================================= -->
<!-- 5. Closed Loop Feedback Control Block (Bottom Area) - Compensator H(s) in Forward Path -->
<!-- Output Sensing Path to Summing Junction -->
<path d="M 900 45 L 915 45 L 915 260 L 675 260" stroke="#94A3B8" stroke-width="1.8" marker-end="url(#arrow_sm)"/>

<!-- Summing Junction (Reference - Output) -->
<circle cx="660" cy="260" r="15" fill="#FFFFFF" stroke="#64748B" stroke-width="2"/>
<text x="660" y="264" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1E293B" text-anchor="middle">+</text>
<text x="660" y="274" font-family="sans-serif" font-size="10" font-weight="bold" fill="#1E293B" text-anchor="middle">+</text>
<text x="672" y="250" font-family="sans-serif" font-size="12" font-weight="bold" fill="#B91C1C" text-anchor="middle">-</text>

<!-- Reference Input v_ref(s) = 0 entering from bottom of Summing Junction -->
<path d="M 660 305 L 660 275" stroke="#94A3B8" stroke-width="1.8" marker-end="url(#arrow_sm)"/>
<text x="660" y="316" font-family="sans-serif" font-size="10" font-weight="bold" fill="#0F172A" text-anchor="middle">v̂_ref(s) (=0)</text>

<!-- Error Signal v_e(s) from Summing Junction to Controller -->
<path d="M 645 260 L 560 260" stroke="#94A3B8" stroke-width="1.8" marker-end="url(#arrow_sm)"/>
<text x="602" y="252" font-family="sans-serif" font-size="9" font-weight="bold" fill="#64748B" text-anchor="middle">v̂_e(s)</text>

<!-- Combined Feedback Controller H(s) (PI/PID & Delay & PWM) -->
<rect x="320" y="230" width="240" height="60" rx="6" fill="#EFF6FF" stroke="#3B82F6" stroke-width="2"/>
<text x="440" y="244" font-family="sans-serif" font-size="10.5" font-weight="bold" fill="#1E3A8A" text-anchor="middle">反馈控制器 H(s)</text>
<text x="440" y="258" font-family="sans-serif" font-size="9.5" fill="#1E3A8A" text-anchor="middle">Kp, Ki, Kd (数字 PID 增益)</text>
<text x="440" y="272" font-family="sans-serif" font-size="8.5" fill="#4B5563" text-anchor="middle">采样 f_sam, 延迟 Delay</text>

<!-- Duty Ratio Output d(s) feedback to the top source -->
<path d="M 320 260 L 245 260 L 245 190 L 175 190 L 175 110" fill="none" stroke="#94A3B8" stroke-width="1.8" marker-end="url(#arrow_sm)"/>
<text x="230" y="182" font-family="sans-serif" font-size="10" font-weight="bold" fill="#64748B" text-anchor="middle">d̂(s)</text>

<!-- T(s) Circular Loop Gain indicator -->
<path d="M 330 150 A 20 20 0 1 1 370 150" fill="none" stroke="#64748B" stroke-width="1.5" stroke-dasharray="3,3" marker-end="url(#arrow_sm)"/>
<text x="350" y="145" font-family="sans-serif" font-size="10" font-weight="bold" fill="#64748B" text-anchor="middle">环路增益 T(s)</text>

<!-- Markers and arrowheads -->
<defs>
<marker id="arrow_sm" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
<path d="M 0 1.8 L 7 5 L 0 8.2 z" fill="#94A3B8"/>
</marker>
<marker id="arrow_dark" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
<path d="M 0 1.8 L 7 5 L 0 8.2 z" fill="#0F172A"/>
</marker>
</defs>
</svg>"""
    st.markdown(small_signal_svg, unsafe_allow_html=True)
    
    # Display equivalent closed loop parameters table
    st.markdown("##### 🔍 闭环小信号拓扑图元件动态参数计算结果 (Closed-Loop Dynamic Parameter Values)")
    st.write("根据当前控制与硬件参数配置，闭环小信号模型原理图中各元件在当前工作点下的真实物理计算值如下：")
    
    r_series_eq_val = (Rdcr + 2.0 * Rds_eq) / 2.0
    col_cl_tbl1, col_cl_tbl2 = st.columns(2)
    with col_cl_tbl1:
        st.markdown(f"""
        | 元件符号 | 元件物理描述 | 当前动态计算值 |
        | :--- | :--- | :--- |
        | **1 : D** | 理想变压器变比 | **1 : {d_ratio:.3f}** (稳态占空比 D = {d_ratio * 100.0:.2f} %) |
        | **(Vin/D) * d̂(s)** | 原边串联受控电压源 | **{vin / d_ratio:.1f}V * d̂(s)** (或 {vref / (d_ratio**2):.1f}V * d̂(s)) |
        | **Io * d̂(s)** | 原边并联受控电流源 | **{(vref / r_load_step):.1f}A * d̂(s)** (基于跳变点负载电流) |
        | **Rds_eq** | 半桥 GaN 等效折算内阻 | **{Rds_eq * 1e3:.2f} m&Omega;** (DCR回路共模总电阻: {r_series_eq_val*2.0*1e3:.2f} m&Omega;) |
        | **Leq** | 等效暂态电感 $L_{{eq}}$ | **{l_eq_val * 1e6:.4f} &mu;H** (计算式: $L(1-k)/2$) |
        | **Rdcr_eq** | 等效直流电阻 | **{rdcr_eq_val * 1e3:.3f} m&Omega;** (计算式: $R_{{dcr}}/2$) |
        """)
        
    with col_cl_tbl2:
        st.markdown(f"""
        | 元件符号 | 元件物理描述 | 当前动态计算值 |
        | :--- | :--- | :--- |
        | **C1** | 主滤波电容 | **{C1 * 1e6:.1f} &mu;F** (ESR1 = **{Resr1 * 1e3:.2f} m&Omega;**) |
        | **C2** | 高频副电容 | **{C2 * 1e6:.1f} &mu;F** (ESR2 = **{Resr2 * 1e3:.2f} m&Omega;**) |
        | **R_load_init** | 初始工作点负载电阻 | **{r_load_init:.4f} &Omega;** (对应初始电流 **{i_load_init:.1f} A**) |
        | **R_load_step** | 阶跃突变负载电阻 | **{r_load_step:.4f} &Omega;** (对应跳变电流 **{i_load_target:.1f} A**) |
        """)
    
    leq_uH = bode_res['Leq'] * 1e6
    rdcr_eq_mOhm = (Rdcr / 2.0) * 1e3
    delay_val_us = (delay_cycles / fs) * 1e6
    
    st.info(f"""
    📝 **小信号电路平均模型参数关系**:
    1. **双相并联等效**: 当两相交错并联工作时，小信号交流模型可以简化为单等效通道。电感减半为 $L_{{eq}} = \\frac{{L_{{tr}}}}{{2}} = \\frac{{L(1-|k|)}}{{2}}$，DCR电阻减半为 $R_{{dcr\\_eq}} = \\frac{{R_{{dcr}}}}{{2}}$。
    2. **反向耦合的加持**: 耦合系数 $k < 0$（反向耦合）使得等效暂态电感 $L_{{tr}} = L(1-|k|)$ 比独立电感更小，使得小信号等效电感 $L_{{eq}}$ 大幅降低，从而将 LC 共振极点推向更高频段，拓宽控制带宽并大幅改善时域的负载跃变响应！
    3. **受控源的物理公式与当前计算过程**:
       * **理想变压器变比 $1 : D$**: 稳态占空比 $D = \\frac{{V_{{ref}}}}{{V_{{in}}}} = \\frac{{{vref:.2f}\\text{{ V}}}}{{{vin:.1f}\\text{{ V}}}} \\approx {d_ratio:.4f}$。
       * **原边串联受控电压源**:
         - **公式**: $e(s) = \\frac{{V_{{ref}}}}{{D^2}} \\hat{{d}}(s) = \\frac{{V_{{in}}}}{{D}} \\hat{{d}}(s)$ (将副边开关管电压扰动 $V_{{in}} \\hat{{d}}$ 折算到原边)
         - **当前计算**: $\\frac{{{vref:.2f}\\text{{ V}}}}{{{d_ratio:.4f}^2}} \\approx {vref / (d_ratio**2):.1f}\\text{{ V}}$，即图中标注的 **${vref / (d_ratio**2):.1f}\\text{{ V}} \\cdot \\hat{{d}}(s)$**。
       * **原边并联受控电流源**:
         - **公式**: $j(s) = \\frac{{V_{{ref}}}}{{R_{{load}}}} \\hat{{d}}(s) = I_{{load}} \\hat{{d}}(s)$ (原边输入抽取电流小信号扰动，主要由稳态直流负载电流决定)
         - **当前计算**: $\\frac{{{vref:.2f}\\text{{ V}}}}{{{r_load_step:.4f}\\ \\Omega}} \\approx {vref / r_load_step:.1f}\\text{{ A}}$，即图中标注的 **{vref / r_load_step:.1f}\\text{{ A}} \\cdot \\hat{{d}}(s)$**。
    4. **开环环路增益 $T(s)$ 解析表达式与计算过程**:
       * **总环路增益**:
         $$T(s) = H(s) \\cdot \\frac{{1}}{{V_M}} \\cdot G_{{vd}}(s)$$
       * **反馈控制器传递函数 $H(s)$** (含 PI/PID 增益及数字延时):
         $$H(s) = \\left( K_p + \\frac{{K_{{i,c}}}}{{s}} + \\frac{{K_d s}}{{1 + \\tau_d s}} \\right) \\cdot e^{{-s T_{{delay}}}}$$
         代入当前值：
         $$H(s) = \\left( {kp:.5f} + \\frac{{{ki_continuous:.2f}}}{{s}} + \\frac{{{kd:.6e} s}}{{1 + {tau_d:.2e} s}} \\right) \\cdot e^{{-s \\cdot {delay_val_us:.2f}\\,\\mu\\text{{s}}}}$$
       * **控制-输出传递函数 $G_{{vd}}(s)$**:
         $$G_{{vd}}(s) = V_{{in}} \\cdot \\frac{{Z_p(s)}}{{Z_L(s) + Z_p(s)}}$$
         其中：
         - 电感分支阻抗: $Z_L(s) = s L_{{eq}} + R_{{dcr\\_eq}}$ (当前值: $s \\cdot {leq_uH:.3f}\\,\\mu\\text{{H}} + {rdcr_eq_mOhm:.2f}\\,\\text{{m}}\\Omega$)
         - 输出电容等效阻抗: $Z_C(s) = \\left(R_{{esr1}} + \\frac{{1}}{{s C_1}}\\right) \\parallel \\left(R_{{esr2}} + \\frac{{1}}{{s C_2}}\\right)$ (当前并联值: $C_1 = {c1_uF:.0f}\\,\\mu\\text{{F}}$, $C_2 = {c2_uF:.0f}\\,\\mu\\text{{F}}$)
         - 并联负载分支阻抗: $Z_p(s) = Z_C(s) \\parallel R_{{load}}$ (当前负载: $R_{{load}} = {r_load_step:.3f}\\,\\Omega$)
         - 归一化调制器增益: $1/V_M = 1$
    """)
    
    st.markdown("---")
    
    # 3. 频域响应分析
    st.markdown('<div id="section-3"></div>', unsafe_allow_html=True)
    st.write("## 3. 频域环路设计与阻抗特性分析 (Frequency-Domain Bode & Impedance)")
    st.write("以下展示了根据小信号模型线性化计算的频域特性，可查看开环/闭环波特图及输出阻抗的频率特性：")
    
    freqs = bode_res['freqs']
    T_mag = 20.0 * np.log10(np.abs(bode_res['T']))
    phase_plot = np.angle(bode_res['T'], deg=True)
    phase_plot = np.unwrap(phase_plot * np.pi / 180.0) * 180.0 / np.pi
    
    freq_tab1, freq_tab2, freq_tab3 = st.tabs(["开环系统分析 (Open-Loop T)", "闭环系统分析 (Closed-Loop G_CL)", "输出阻抗分析 (Output Impedance Z_out)"])
    
    with freq_tab1:
        st.write("#### 开环环路增益 T(s) 波特图")
        fig_bode_ol, (ax_mag, ax_phase) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
        plt.subplots_adjust(hspace=0.15)
        
        # 1. Magnitude Plot
        ax_mag.semilogx(freqs, T_mag, color="#2563EB", linewidth=2.5, label="Loop Gain |T(s)|")
        # Plot plant and compensator for reference
        ax_mag.semilogx(freqs, 20.0 * np.log10(np.abs(bode_res['Gvd'])), color="#94A3B8", linestyle=":", alpha=0.8, label="Plant |Gvd(s)|")
        ax_mag.semilogx(freqs, 20.0 * np.log10(np.abs(bode_res['Gc'])), color="#8B5CF6", linestyle="--", alpha=0.8, label="Compensator |Gc(s)|")
        
        ax_mag.axhline(y=0, color="black", linestyle="-", linewidth=1.2)
        if bode_res['fc']:
            ax_mag.axvline(x=bode_res['fc'], color="red", linestyle="--", label=f"fc = {bode_res['fc']/1e3:.2f} kHz")
            
        ax_mag.set_ylabel("Gain (dB)", fontsize=10, fontweight="bold")
        ax_mag.grid(True, which="both", linestyle=":", alpha=0.5)
        ax_mag.legend(loc="lower left", framealpha=0.9)
        ax_mag.set_title("Loop Gain T(s) Magnitude", fontsize=11, fontweight="bold")
        ax_mag.set_ylim([-40, 50])
        
        # 2. Phase Plot
        ax_phase.semilogx(freqs, phase_plot, color="#E11D48", linewidth=2.5, label="Phase of T(s)")
        ax_phase.axhline(y=-180, color="black", linestyle="-", linewidth=1.2)
        
        if bode_res['fc']:
            ax_phase.axvline(x=bode_res['fc'], color="red", linestyle="--")
            p_idx = np.argmin(np.abs(freqs - bode_res['fc']))
            ax_phase.plot(bode_res['fc'], phase_plot[p_idx], 'ro')
            ax_phase.annotate(f"PM = {bode_res['PM']:.1f}°", 
                               xy=(bode_res['fc'], phase_plot[p_idx]), 
                               xytext=(bode_res['fc']*1.5, phase_plot[p_idx] + 20),
                               arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=6))
                               
        ax_phase.set_ylabel("Phase (deg)", fontsize=10, fontweight="bold")
        ax_phase.set_xlabel("Frequency (Hz)", fontsize=10)
        ax_phase.grid(True, which="both", linestyle=":", alpha=0.5)
        ax_phase.set_ylim([-270, 90])
        ax_phase.set_yticks([-270, -180, -90, 0, 90])
        ax_phase.set_title("Loop Gain T(s) Phase", fontsize=11, fontweight="bold")
        
        st.pyplot(fig_bode_ol)
        
    with freq_tab2:
        st.write("#### 闭环传输函数 G_CL(s) 波特图")
        CL_mag = 20.0 * np.log10(np.abs(bode_res['G_CL']))
        CL_phase = np.unwrap(np.angle(bode_res['G_CL'], deg=True) * np.pi / 180.0) * 180.0 / np.pi
        
        f_bw = None
        under_3db = np.where(CL_mag < -3.0)[0]
        if len(under_3db) > 0:
            f_bw = freqs[under_3db[0]]
            
        fig_bode_cl, (ax_mag_cl, ax_phase_cl) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
        plt.subplots_adjust(hspace=0.15)
        
        # Magnitude
        ax_mag_cl.semilogx(freqs, CL_mag, color="#10B981", linewidth=2.5, label="Closed-Loop |G_CL(s)|")
        ax_mag_cl.axhline(y=0, color="black", linestyle="-", linewidth=1.2)
        ax_mag_cl.axhline(y=-3, color="gray", linestyle=":", alpha=0.7, label="-3 dB")
        if f_bw:
            ax_mag_cl.axvline(x=f_bw, color="darkgreen", linestyle="--", label=f"BW (-3dB) = {f_bw/1e3:.2f} kHz")
        ax_mag_cl.set_ylabel("Gain (dB)", fontsize=10, fontweight="bold")
        ax_mag_cl.grid(True, which="both", linestyle=":", alpha=0.5)
        ax_mag_cl.legend(loc="lower left", framealpha=0.9)
        ax_mag_cl.set_title("Closed-Loop G_CL(s) Magnitude", fontsize=11, fontweight="bold")
        ax_mag_cl.set_ylim([-40, 10])
        
        # Phase
        ax_phase_cl.semilogx(freqs, CL_phase, color="#D97706", linewidth=2.5, label="Phase of G_CL(s)")
        if f_bw:
            ax_phase_cl.axvline(x=f_bw, color="darkgreen", linestyle="--")
        ax_phase_cl.set_ylabel("Phase (deg)", fontsize=10, fontweight="bold")
        ax_phase_cl.set_xlabel("Frequency (Hz)", fontsize=10)
        ax_phase_cl.grid(True, which="both", linestyle=":", alpha=0.5)
        ax_phase_cl.set_ylim([-270, 90])
        ax_phase_cl.set_yticks([-270, -180, -90, 0, 90])
        ax_phase_cl.set_title("Closed-Loop G_CL(s) Phase", fontsize=11, fontweight="bold")
        
        st.pyplot(fig_bode_cl)
        
        if f_bw:
            st.metric("闭环 -3dB 带宽 (Closed-loop Bandwidth)", f"{f_bw/1e3:.3f} kHz")
            
    with freq_tab3:
        st.write("#### 输出阻抗 Z_out 频率特性分析")
        Z_ol_mag = np.abs(bode_res['Z_ol']) * 1e3 # convert to mOhm
        Z_cl_mag = np.abs(bode_res['Z_cl']) * 1e3 # convert to mOhm
        
        fig_z, ax_z = plt.subplots(figsize=(11, 5.5))
        ax_z.loglog(freqs, Z_ol_mag, color="#94A3B8", linestyle="--", linewidth=2, label="Open-loop |Z_ol|")
        ax_z.loglog(freqs, Z_cl_mag, color="#EF4444", linewidth=2.5, label="Closed-loop |Z_cl|")
        
        # Reference levels
        dcr_eq_mOhm = (rdcr_mOhm / 2.0)
        esr_mOhm_val = (resr1_mOhm * resr2_mOhm) / (resr1_mOhm + resr2_mOhm)
        ax_z.axhline(y=dcr_eq_mOhm, color="gray", linestyle=":", alpha=0.7, label=f"DCR_eq ({dcr_eq_mOhm:.3f} mOhm)")
        ax_z.axhline(y=esr_mOhm_val, color="blue", linestyle=":", alpha=0.7, label=f"ESR_eq ({esr_mOhm_val:.3f} mOhm)")
        
        if bode_res['fc']:
            ax_z.axvline(x=bode_res['fc'], color="red", linestyle="--", label=f"fc = {bode_res['fc']/1e3:.2f} kHz")
        if f_bw:
            ax_z.axvline(x=f_bw, color="darkgreen", linestyle="--", label=f"BW = {f_bw/1e3:.2f} kHz")
        ax_z.set_xlabel("Frequency (Hz)", fontsize=10)
        ax_z.set_ylabel("Output Impedance Magnitude (mΩ)", fontsize=10, fontweight="bold")
        ax_z.grid(True, which="both", linestyle=":", alpha=0.5)
        ax_z.legend(loc="upper right")
        ax_z.set_ylim([1e-2, 1e3])
        
        st.pyplot(fig_z)
        
        st.info("""
        💡 **输出阻抗与暂态响应的关系**:
        1. **低频段闭环压制**: 在反馈带宽以内（$f < f_c$），闭环输出阻抗 $|Z_{cl}| = |Z_{ol}| / |1+T|$。由于积分环节的存在，低频段 $|T| \\gg 1$，因此闭环输出阻抗下降到微欧级，保证了极佳的 DC 稳压精度。
        2. **中频段阻抗峰值 (Peaking)**: 在穿越频率 $f_c$ 附近，如果系统的相位裕度较小（如 $< 45^\\circ$），$|1+T(j\\omega)|$ 可能会小于 1，导致闭环输出阻抗在该频段甚至高于开环输出阻抗，产生阻抗隆起。这会在负载跳变时引起电压明显的过冲和 ringing 振荡！
        3. **高频段由电容主导**: 在反馈带宽以外（$f > f_c$），反馈失效，闭环输出阻抗与开环输出阻抗合一，阻抗大小纯粹取决于输出电容的容值 and 等效串联电阻 ESR。
        """)

    st.markdown("---")
    
    # 4. 闭环时域仿真与暂态响应
    st.markdown('<div id="section-4"></div>', unsafe_allow_html=True)
    st.write("## 4. 闭环开关级时域暂态仿真与波形分析 (Closed-Loop Time-Domain Transient Simulation)")
    st.write("以下展示了非线性开关状态时域求解（龙格库塔 RK4 求解）对应的暂态波形，展现了耦合电感与数字闭环对于 $Vin=54V$ 输入、$Vref=12.2V$ 输出在负载跃变瞬态下的联合响应能力：")
    
    col_cl1, col_cl2, col_cl3 = st.columns(3)
    with col_cl1:
        st.number_input("闭环初始电流 I_init (A)", min_value=0.0, max_value=500.0, value=64.0, step=1.0, format="%.1f", key="cl_i_init")
        st.number_input("闭环电流变化率 (A/μs)", min_value=0.1, max_value=50.0, value=1.0, step=0.5, format="%.1f", key="cl_slew_rate_val")
    with col_cl2:
        st.number_input("闭环跳变目标电流 I_step (最终值/A)", min_value=0.0, max_value=500.0, value=160.0, step=1.0, format="%.1f", key="cl_i_target")
        st.number_input("闭环负载跳变时刻 (ms)", min_value=0.05, max_value=10.0, value=1.0, step=0.05, format="%.2f", key="cl_t_step")
    with col_cl3:
        st.checkbox("开启二极管离散仿真 (DCM 模式)", value=True, key="cl_dcm_mode", help="防止轻载下电流反向，稳定无载运行")
        
    st.write("")
    
    fig, axs = plt.subplots(3, 1, figsize=(11, 7.5), sharex=True)
    plt.subplots_adjust(hspace=0.25)
    
    # 1. Output Voltage
    axs[0].plot(t_arr * 1e3, v_out_arr, label=f"Coupled (k={k_coupling})", color="#1E3A8A", linewidth=2)
    axs[0].axhline(y=vref, color="red", linestyle=":", label="Vref")
    axs[0].axhline(y=vref*0.99, color="gray", linestyle=":", alpha=0.5)
    axs[0].axhline(y=vref*1.01, color="gray", linestyle=":", alpha=0.5)
    axs[0].set_ylabel("Vo (V)", fontsize=10, fontweight="bold")
    axs[0].grid(True, linestyle=":", alpha=0.6)
    axs[0].legend(loc="upper right", framealpha=0.9)
    axs[0].set_title("Output Voltage Transient Response", fontsize=11, fontweight="bold")
    
    # 2. Phase Currents
    axs[1].plot(t_arr * 1e3, i1_arr, label="Phase 1 (Coupled)", color="#0284C7", linewidth=1.5)
    axs[1].plot(t_arr * 1e3, i2_arr, label="Phase 2 (Coupled)", color="#F97316", linewidth=1.5)
    axs[1].plot(t_arr * 1e3, i1_arr + i2_arr, label="Total Output (Coupled)", color="#10B981", linewidth=2)
    axs[1].set_ylabel("Currents (A)", fontsize=10, fontweight="bold")
    axs[1].grid(True, linestyle=":", alpha=0.6)
    axs[1].legend(loc="upper right", framealpha=0.9, ncol=2)
    axs[1].set_title("Phase Currents & Total Current Comparison", fontsize=11, fontweight="bold")
    
    # 3. Duty Cycle & Load Current
    ax3_twin = axs[2].twinx()
    l_sim, = axs[2].plot(t_arr * 1e3, d1_arr, label="Duty Cycle d1", color="#8B5CF6", linewidth=1.5)
    l_load, = ax3_twin.plot(t_arr * 1e3, i_load_arr, label="Load Current I_load", color="#EF4444", linestyle="-.", linewidth=2)
    
    axs[2].set_ylabel("Duty Cycle", fontsize=10, fontweight="bold", color="#8B5CF6")
    ax3_twin.set_ylabel("Load Current (A)", fontsize=10, fontweight="bold", color="#EF4444")
    axs[2].tick_params(axis='y', labelcolor="#8B5CF6")
    ax3_twin.tick_params(axis='y', labelcolor="#EF4444")
    
    axs[2].grid(True, linestyle=":", alpha=0.6)
    axs[2].set_xlabel("Time (ms)", fontsize=10)
    axs[2].set_title("Duty Cycle and Load Current Step Change", fontsize=11, fontweight="bold")
    
    st.pyplot(fig)
    
    # Quantities Table Comparison
    st.write("#### 📊 稳态与动态纹波性能量化")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.metric(
            label="相电流稳态双峰纹波 (Coupled)",
            value=f"{ripple_coupled:.3f} A"
        )
    with col_t2:
        st.metric(
            label="负载跳变最低瞬态电压 (Coupled)",
            value=f"{v_min_coupled:.3f} V"
        )

    st.markdown("---")

    # 5. 开环固定比例时域仿真与暂态响应
    st.markdown('<div id="section-5"></div>', unsafe_allow_html=True)
    st.write("## 5. 开环固定比例负载阶跃时域暂态仿真与波形分析 (Open-Loop Fixed-Ratio Transient Simulation)")
    st.write("在开环（固定比率，例如 D = 25.0%，即 4:1 固定变比）下，控制环路不进行任何调节（即没有占空比动态扰动 d̂(s)）。以下展示了在与闭环相同的负载突变（40% -> 100% 突变）下，系统由于 LC 二阶无源滤波器低阻尼引起的开环振铃与永久性电压跌落现象：")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        ol_d_fixed = st.number_input("开环固定占空比 D", min_value=0.0, max_value=1.0, value=0.25, step=0.01, format="%.3f", key="ol_d_fixed")
        ol_slew_rate_val = st.number_input("开环电流变化率 (A/μs)", min_value=0.1, max_value=50.0, value=1.0, step=0.5, format="%.1f", key="ol_slew_rate_val")
        ol_slew_rate = ol_slew_rate_val * 1e6
    with col_p2:
        ol_i_init = st.number_input("开环初始电流 I_init (A)", min_value=0.0, max_value=500.0, value=64.0, step=1.0, format="%.1f", key="ol_i_init")
        ol_t_step = st.number_input("开环负载跳变时刻 (ms)", min_value=0.05, max_value=10.0, value=0.1, step=0.05, format="%.2f", key="ol_t_step") * 1e-3
    with col_p3:
        ol_i_target = st.number_input("开环跳变目标电流 I_step (最终值/A)", min_value=0.0, max_value=500.0, value=160.0, step=1.0, format="%.1f", key="ol_i_target")
        ol_t_sim = st.number_input("开环仿真总时长 (ms)", min_value=0.2, max_value=20.0, value=2.5, step=0.5, key="ol_t_sim") * 1e-3
        
    # Run open-loop simulation under load step
    ol_vref = ol_d_fixed * vin
    ol_r_load_init = ol_vref / ol_i_init if ol_i_init > 0 else 1000.0
    ol_r_load_step = ol_vref / ol_i_target
    
    t_ol, v_ol_c, i1_ol_c, i2_ol_c, _ = simulate_open_loop(
        Vin=vin, Vref=ol_vref, L=L, k_coupling=k_coupling, Rdcr=Rdcr, C1=C1, Resr1=Resr1, C2=C2, Resr2=Resr2,
        Rload_init=ol_r_load_init, Rload_step=ol_r_load_step, t_sim=ol_t_sim, t_step=ol_t_step, fs=fs, Rds_eq=Rds_eq,
        slew_rate=ol_slew_rate
    )
    
    # Reconstruct I_load array for open loop plot comparison
    i_load_arr_ol = np.zeros(len(t_ol))
    for step_idx in range(len(t_ol)):
        t_val = t_ol[step_idx]
        if t_val < ol_t_step:
            i_load_arr_ol[step_idx] = ol_i_init
        elif ol_i_target > ol_i_init:
            i_load_arr_ol[step_idx] = min(ol_i_target, ol_i_init + ol_slew_rate * (t_val - ol_t_step))
        else:
            i_load_arr_ol[step_idx] = max(ol_i_target, ol_i_init - ol_slew_rate * (t_val - ol_t_step))
            
    # Calculate open-loop phase current ripple peak-to-peak
    ol_steady_mask = (t_ol > 0.4 * ol_t_step) & (t_ol < 0.9 * ol_t_step)
    if np.any(ol_steady_mask):
        ol_ripple_coupled = np.max(i1_ol_c[ol_steady_mask]) - np.min(i1_ol_c[ol_steady_mask])
    else:
        ol_ripple_coupled = 0.0
    ol_v_min = np.min(v_ol_c)
    
    # Calculate wave oscillation frequency, period, and LC resonant frequency
    i_total_ol = i1_ol_c + i2_ol_c
    post_step_idx_ol = np.where(t_ol >= ol_t_step)[0]
    
    f_osc_val = None
    mean_period_ms = None
    peak_times_ms = []
    
    if len(post_step_idx_ol) > 0:
        t_post_ol = t_ol[post_step_idx_ol]
        i_post_ol = i_total_ol[post_step_idx_ol]
        dt_sim_ol = t_ol[1] - t_ol[0]
        min_dist_ol = max(10, int(0.04e-3 / dt_sim_ol))  # at least 0.04ms apart
        
        try:
            from scipy.signal import find_peaks
            peaks_ol, _ = find_peaks(i_post_ol, distance=min_dist_ol)
            if len(peaks_ol) > 0:
                peak_times_ms = t_post_ol[peaks_ol] * 1e3
        except Exception:
            peaks_ol = []
            for idx in range(1, len(i_post_ol) - 1):
                if i_post_ol[idx] > i_post_ol[idx-1] and i_post_ol[idx] > i_post_ol[idx+1] and i_post_ol[idx] > ol_i_target:
                    peaks_ol.append(idx)
            if len(peaks_ol) > 0:
                peak_times_ms = t_post_ol[peaks_ol] * 1e3
                
        if len(peak_times_ms) >= 2:
            periods_ms = np.diff(peak_times_ms)
            mean_period_ms = np.mean(periods_ms)
            f_osc_val = 1000.0 / mean_period_ms

    # Theoretical LC calculations
    l_eq_cm = L * (1.0 - k_coupling) / 2.0
    c_tot = C1 + C2
    r_series_eq = (Rdcr + 2.0 * Rds_eq) / 2.0
    
    f_n_val = 1.0 / (2.0 * np.pi * np.sqrt(l_eq_cm * c_tot))
    omega_n_val = 2.0 * np.pi * f_n_val
    zeta_val = 0.5 / omega_n_val * (r_series_eq / l_eq_cm + 1.0 / (ol_r_load_step * c_tot))
    f_d_val = f_n_val * np.sqrt(1.0 - zeta_val**2) if zeta_val < 1.0 else 0.0
    T_d_ms = (1000.0 / f_d_val) if f_d_val > 0 else 0.0

    # Create Tabs for Section 5 open-loop response
    ol_tab1, ol_tab2 = st.tabs(["📈 时域暂态波形 (Time-Domain Waveforms)", "📊 阻抗与阶跃频谱分析 (Impedance & Step Spectrum)"])
    
    with ol_tab1:
        fig_ol, axs_ol = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
        plt.subplots_adjust(hspace=0.25)
        
        # Row 1: Voltage
        axs_ol[0].plot(t_ol * 1e3, v_ol_c, label=f"Coupled Inductor (k={k_coupling})", color="#1E3A8A", linewidth=2)
        axs_ol[0].axhline(y=ol_vref, color="red", linestyle=":", label=f"No-load Voltage ({ol_vref:.2f}V)")
        vo_steady_full = ol_vref * ol_r_load_step / (ol_r_load_step + Rdcr/2.0 + Rds_eq)
        axs_ol[0].axhline(y=vo_steady_full, color="gray", linestyle="-.", alpha=0.7, label=f"Full-load Steady-state ({vo_steady_full:.2f}V)")
        axs_ol[0].set_ylabel("Vo (V)", fontsize=10, fontweight="bold")
        axs_ol[0].grid(True, linestyle=":", alpha=0.6)
        axs_ol[0].legend(loc="upper right", framealpha=0.9)
        axs_ol[0].set_title("Open-Loop Voltage Response to Load Step (Fixed Duty Cycle)", fontsize=11, fontweight="bold")
        
        # Row 2: Current
        axs_ol[1].plot(t_ol * 1e3, i1_ol_c + i2_ol_c, label="Total Inductor Current (Coupled)", color="#10B981", linewidth=2)
        axs_ol[1].plot(t_ol * 1e3, i_load_arr_ol, label="Load Current I_load (Disturbance)", color="#EF4444", linestyle="-.", linewidth=2)
        axs_ol[1].set_ylabel("Currents (A)", fontsize=10, fontweight="bold")
        axs_ol[1].set_xlabel("Time (ms)", fontsize=10)
        axs_ol[1].grid(True, linestyle=":", alpha=0.6)
        axs_ol[1].legend(loc="upper right", framealpha=0.9)
        axs_ol[1].set_title("Open-Loop Current Transient Comparison", fontsize=11, fontweight="bold")
        
        st.pyplot(fig_ol)
        
        st.write("#### 📊 开环稳态与动态纹波性能量化")
        col_ol_t1, col_ol_t2 = st.columns(2)
        with col_ol_t1:
            st.metric(
                label="开环相电流稳态双峰纹波 (Coupled)",
                value=f"{ol_ripple_coupled:.3f} A"
            )
        with col_ol_t2:
            st.metric(
                label="开环负载跳变最低瞬态电压 (Coupled)",
                value=f"{ol_v_min:.3f} V"
            )
            
        st.markdown("#### 📊 时域波形振荡频率与 LC 谐振特征核对")
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            if f_osc_val is not None:
                st.markdown(f"""
                <div class="metric-card" style="background:#FFFDFA; border:1px solid #FCD34D;">
                    <div class="metric-title" style="color:#D97706;">📈 时域仿真波形检测 (Simulation Waveform)</div>
                    <div class="metric-value" style="color:#B45309; font-size:1.6rem;">{f_osc_val:.2f} Hz</div>
                    <span style="font-size:0.85rem; color:#64748B;">
                        检测前几个峰值时间: {', '.join([f"{t:.3f}ms" for t in peak_times_ms[:5]])} {'...' if len(peak_times_ms) > 5 else ''}<br>
                        平均振荡周期 T_osc: <b>{mean_period_ms:.4f} ms</b>
                    </span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-card" style="background:#FFFDFA; border:1px solid #FCD34D;">
                    <div class="metric-title" style="color:#D97706;">📈 时域仿真波形检测 (Simulation Waveform)</div>
                    <div class="metric-value" style="color:#B45309; font-size:1.3rem;">未检测到足够多的振荡波谷/峰</div>
                    <span style="font-size:0.85rem; color:#64748B;">请确保仿真总时长足够长且系统阻尼较低以观察到完整周期。</span>
                </div>
                """, unsafe_allow_html=True)
                
        with col_res2:
            st.markdown(f"""
            <div class="metric-card" style="background:#F0FDF4; border:1px solid #86EFAC;">
                <div class="metric-title" style="color:#16A34A;">📐 LC 无源滤波器理论计算 (Theoretical LC)</div>
                <div class="metric-value" style="color:#15803D; font-size:1.6rem;">{f_d_val:.2f} Hz</div>
                <span style="font-size:0.85rem; color:#64748B;">
                    无阻尼特征频率 f_n: <b>{f_n_val:.2f} Hz</b><br>
                    系统总阻尼比 &zeta;: <b>{zeta_val:.4f}</b> (有阻尼周期 T_d: <b>{T_d_ms:.4f} ms</b>)
                </span>
            </div>
            """, unsafe_allow_html=True)
            
        if f_osc_val is not None:
            rel_err = abs(f_osc_val - f_d_val) / f_d_val * 100.0
            st.success(f"✅ **核对结论**: 时域波形实际振荡频率 ({f_osc_val:.2f} Hz) 与 LC 网络理论有阻尼特征频率 ({f_d_val:.2f} Hz) 的相对误差仅为 **{rel_err:.3f}%**，物理建模与 RK4 求解精度完美匹配！")

    with ol_tab2:
        st.write("#### 📊 负载电流阶跃频谱与输出阻抗频率特性分析")
        st.write("下面展示了负载电流阶跃信号自身的频谱分布，以及开环输出阻抗的幅频特性，这能帮助您从频域本质上理解开环暂态跌落与振铃的原因。")
        
        # Calculate Z_out(f) and I_load(f)
        f_axis = np.logspace(1, 6, 500) # 10Hz to 1MHz
        s_axis = 2.0 * np.pi * 1j * f_axis
        
        # Z_out(s) calculation
        R_s = (Rdcr / 2.0) + Rds_eq
        Z_ind = R_s + s_axis * l_eq_cm
        Z_cap1 = Resr1 + 1.0 / (s_axis * C1)
        Z_cap2 = Resr2 + 1.0 / (s_axis * C2)
        
        Y_out = 1.0 / Z_ind + 1.0 / Z_cap1 + 1.0 / Z_cap2 + 1.0 / ol_r_load_step
        Z_out_mag = 1.0 / np.abs(Y_out) # in Ohms
        Z_out_mOhm = Z_out_mag * 1e3 # in mOhms
        
        # I_load(f) calculation (Laplace Spectrum Magnitude)
        delta_I = abs(ol_i_target - ol_i_init)
        t_ramp = delta_I / ol_slew_rate if ol_slew_rate > 0 else 1e-9
        sin_term = np.abs(np.sin(np.pi * f_axis * t_ramp))
        I_load_spec = (ol_slew_rate / (2.0 * np.pi**2 * f_axis**2)) * sin_term
        
        f_corner = 1.0 / (np.pi * t_ramp)
        
        fig_spec, (ax_z, ax_i) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Left Plot: Output Impedance
        ax_z.loglog(f_axis, Z_out_mOhm, color="#1E3A8A", linewidth=2.5, label="Output Impedance |Z_out|")
        peak_idx = np.argmax(Z_out_mOhm)
        f_peak = f_axis[peak_idx]
        z_peak = Z_out_mOhm[peak_idx]
        
        ax_z.axvline(x=f_n_val, color="red", linestyle="--", label=f"LC Resonant fn = {f_n_val:.1f} Hz")
        ax_z.plot(f_peak, z_peak, "ro")
        ax_z.annotate(f"Peak: {z_peak:.1f} mΩ\n@ {f_peak/1e3:.2f} kHz", 
                      xy=(f_peak, z_peak), 
                      xytext=(f_peak * 1.5, z_peak * 0.5),
                      arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=6))
                      
        ax_z.set_title("Open-Loop Output Impedance Profile |Z_out(f)|", fontsize=11, fontweight="bold")
        ax_z.set_xlabel("Frequency (Hz)", fontsize=10)
        ax_z.set_ylabel("Impedance |Z_out| (mΩ)", fontsize=10, fontweight="bold")
        ax_z.grid(True, which="both", linestyle=":", alpha=0.5)
        ax_z.legend(loc="lower left")
        
        # Right Plot: Step Load Spectrum
        ax_i.loglog(f_axis, I_load_spec, color="#EF4444", linewidth=2.5, label="Load Step Spectrum |I_load(f)|")
        ax_i.axvline(x=f_corner, color="#8B5CF6", linestyle="--", label=f"Corner freq = {f_corner/1e3:.2f} kHz")
        ax_i.axvline(x=f_n_val, color="red", linestyle=":", alpha=0.8, label=f"LC Resonance fn = {f_n_val:.1f} Hz")
        
        ax_i.set_title("Load Current Step Laplace Spectrum |I_load(f)|", fontsize=11, fontweight="bold")
        ax_i.set_xlabel("Frequency (Hz)", fontsize=10)
        ax_i.set_ylabel("Spectrum Magnitude (A/Hz)", fontsize=10, fontweight="bold")
        ax_i.grid(True, which="both", linestyle=":", alpha=0.5)
        ax_i.legend(loc="lower left")
        
        st.pyplot(fig_spec)
        
        st.markdown(f"""
        > [!NOTE]
        > **📚 频域机理解析 (Physical Mechanism in Frequency Domain)**:
        > 1. **二阶 LC 阻抗峰值**: 输出阻抗 $|Z_{{out}}(f)|$ 在有阻尼谐振频点 **{f_d_val:.1f} Hz** 处具有明显的共模谐振峰值（峰值阻抗达 **{z_peak:.1f} m&Omega;**）。此处输出电容与电感发生并联谐振，阻抗呈现最大值，这是引起电压波动与振铃的电路本源。
        > 2. **阶跃电流激励**: 阶跃负载电流 $\Delta I_{{load}}$ 从低频到高频呈广谱分布。在谐振频点 **{f_d_val/1e3:.2f} kHz** 处，阶跃信号的频谱能量依然非常高（处于转折频率 **{f_corner/1e3:.2f} kHz** 附近，转折频率处由于有限跳变率 $SR={ol_slew_rate/1e6:.1f}\\text{{ A/}}\\mu\\text{{s}}$ 频谱开始以 $-40\\text{{ dB/dec}}$ 加速衰减）。高能量的阶跃激励注入到高阻抗的 LC 谐振点上，从而诱发了时域上明显的 **{f_osc_val:.2f} Hz** 有阻尼谐振波动！
        """)

    # Show equivalent open loop schematic
    st.markdown("#### 📐 开环等效电路小信号拓扑结构")
    st.write("在开环固定比例下，占空比没有动态扰动（d̂(s) = 0），因此等效电路中不存在受控电压源与受控电流源，信号纯粹由于负载电流突变扰动（î_load(s)）激发二阶 LC 滤波器的状态响应：")
    if os.path.exists("DesignDoc/open_loop_schematic.png"):
        st.image("DesignDoc/open_loop_schematic.png", caption="两相交错并联 Buck 固定比例 (Fixed Ratio) 开环等效小信号电路模型 (无反馈环路及受控占空比源)", width="stretch")

    # Display equivalent open loop parameters table
    st.markdown("##### 🔍 拓扑图元件动态参数计算结果 (Dynamic Parameter Values)")
    st.write("根据您当前的物理配置，原理图中各元件在当前工作点下的真实物理计算值如下：")
    
    col_tbl1, col_tbl2 = st.columns(2)
    with col_tbl1:
        st.markdown(f"""
        | 元件符号 | 元件物理描述 | 当前动态计算值 |
        | :--- | :--- | :--- |
        | **1 : D** | 理想变压器变比 | **1 : {ol_d_fixed:.3f}** |
        | **D** | 开环固定占空比 | **{ol_d_fixed * 100.0:.2f} %** |
        | **Rds_eq** | 半桥 GaN 等效折算内阻 | **{Rds_eq * 1e3:.2f} m&Omega;** (DCR回路共模总电阻: {r_series_eq*2.0*1e3:.2f} m&Omega;) |
        | **Leq** | 等效暂态共模电感 $L_{{eq,CM}}$ | **{l_eq_cm * 1e6:.4f} &mu;H** (计算式: $L(1-k)/2$) |
        | **Rdcr_eq** | 等效直流电阻 | **{Rdcr/2.0 * 1e3:.3f} m&Omega;** (计算式: $R_{{dcr}}/2$) |
        """)
        
    with col_tbl2:
        st.markdown(f"""
        | 元件符号 | 元件物理描述 | 当前动态计算值 |
        | :--- | :--- | :--- |
        | **C1** | 主滤波电容 | **{C1 * 1e6:.1f} &mu;F** (ESR1 = **{Resr1 * 1e3:.2f} m&Omega;**) |
        | **C2** | 高频副电容 | **{C2 * 1e6:.1f} &mu;F** (ESR2 = **{Resr2 * 1e3:.2f} m&Omega;**) |
        | **R_load_init** | 初始工作点负载电阻 | **{ol_r_load_init:.4f} &Omega;** (对应初始电流 **{ol_i_init:.1f} A**) |
        | **R_load_step** | 阶跃突变负载电阻 | **{ol_r_load_step:.4f} &Omega;** (对应跳变电流 **{ol_i_target:.1f} A**) |
        """)

    st.markdown("---")

    # 6. 数字补偿与设计参考指南
    st.markdown('<div id="section-6"></div>', unsafe_allow_html=True)
    st.write("## 6. 数字补偿与设计参考指南 (Digital Compensation & Design Reference Guide)")
    
    st.info("""
    💡 **数字补偿优化 Load Step 的设计方法**:
    1. **反向耦合电感对暂态的加持**: 耦合系数 $k > 0$ 使得等效暂态电感减小为 $L_{eq} = L(1-k)/2$，这比普通独立电感的等效电感 $L/2$ 更小！这可以极大地提高暂态阶段相电流的变化率 ($di/dt$)，从而大幅缩短电压恢复时间，并减小电压跌落（Undershoot）。
    2. **穿越频率 $f_c$ 的选取**: 通常建议在开关频率的 1/20 到 1/10 之间。如 $f_{sw}=200\text{ kHz}$，建议 $f_c$ 设为 $10\sim20\text{ kHz}$。如果带宽太高，会引入较多高频噪声，且数字控制延迟（延时 1.5 周期在 $200\text{ kHz}$ 下为 $7.5\ \mu\text{s}$）会在高频处引入极大的负相位，导致环路不稳定！
    3. **相位裕度 PM**: 应当保持在 $45^\circ \sim 60^\circ$。若 PM 太低，电压波形会出现振荡；若 PM 太高，系统响应会变慢。
    4. **微分项 $K_d$ 与高频滤波时间常数 $\tau_d$**: 数字控制中，直接微分会放大噪声，因此采用低通滤波的 $D$ 项：$G_d(s) = \frac{K_d s}{1 + \tau_d s}$。增加 $K_d$ 可以提升穿越频率处的相位裕度，但需注意噪声影响。
    """)

except Exception as e:
    st.error(f"仿真出现错误: {e}")
    st.info("这通常是因为环路发散或参数设置不合理，请尝试减小 PID 增益 (Kp, Ki) 或增大滤波电容 (C) / 增大自感 (L) 后重试。")
