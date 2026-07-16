import numpy as np
import matplotlib.pyplot as plt
import os
from coupled_buck_model import simulate_coupled_buck, bode_analysis

# Target directory for artifacts
artifact_dir = "/Users/walter/.gemini/antigravity/brain/82e4d54a-9511-40c5-a256-65615249a460"
os.makedirs(artifact_dir, exist_ok=True)

# Default parameters
# Default parameters
vin = 54.0
vref = 12.2
L = 1.6e-6
k_coupling = 0.6
Rdcr = 2.0e-3
C = 1500.0e-6
Resr = 1.0e-3
r_load_init = 12.2 / (163.93 * 0.4) # 40% load
r_load_step = 12.2 / 163.93         # 100% load
t_step = 1.0e-3
fs = 210e3
fctrl = 100e3
delay_cycles = 1.5 * (fs / fctrl) # 3.15
kp = 0.00187
ki = 390.7
kd = 2.0e-7
tau_d = 1.0e-6

# 1. Frequency Domain Bode Response
bode_res = bode_analysis(
    Vin=vin, L=L, k_coupling=k_coupling, Rdcr=Rdcr, C=C, Resr=Resr, Rload=r_load_step,
    Kp=kp, Ki=ki, Kd=kd, tau_d=tau_d, delay_cycles=delay_cycles, fs=fs
)

# 2. Time Domain Simulations - Scenario 1: 0% -> 60% Load Step
t_arr1, i1_arr1, i2_arr1, v_out_arr1, i_load_arr1, d1_arr1, d2_arr1 = simulate_coupled_buck(
    Vin=vin, Vref=vref, L=L, k_coupling=k_coupling, Rdcr=Rdcr, C=C, Resr=Resr,
    Rload_init=1000.0, Rload_step=12.2/(163.93*0.6), t_step=t_step,
    fs=fs, fctrl=fctrl, Kp=kp, Ki=ki, Kd=kd, tau_d=tau_d, delay_cycles=delay_cycles, dcm_mode=True
)

_, i1_un1, i2_un1, v_un1, _, _, _ = simulate_coupled_buck(
    Vin=vin, Vref=vref, L=L, k_coupling=0.0, Rdcr=Rdcr, C=C, Resr=Resr,
    Rload_init=1000.0, Rload_step=12.2/(163.93*0.6), t_step=t_step,
    fs=fs, fctrl=fctrl, Kp=kp, Ki=ki, Kd=kd, tau_d=tau_d, delay_cycles=delay_cycles, dcm_mode=True
)

# 3. Time Domain Simulations - Scenario 2: 40% -> 100% Load Step
t_arr2, i1_arr2, i2_arr2, v_out_arr2, i_load_arr2, d1_arr2, d2_arr2 = simulate_coupled_buck(
    Vin=vin, Vref=vref, L=L, k_coupling=k_coupling, Rdcr=Rdcr, C=C, Resr=Resr,
    Rload_init=12.2/(163.93*0.4), Rload_step=12.2/163.93, t_step=t_step,
    fs=fs, fctrl=fctrl, Kp=kp, Ki=ki, Kd=kd, tau_d=tau_d, delay_cycles=delay_cycles, dcm_mode=True
)

_, i1_un2, i2_un2, v_un2, _, _, _ = simulate_coupled_buck(
    Vin=vin, Vref=vref, L=L, k_coupling=0.0, Rdcr=Rdcr, C=C, Resr=Resr,
    Rload_init=12.2/(163.93*0.4), Rload_step=12.2/163.93, t_step=t_step,
    fs=fs, fctrl=fctrl, Kp=kp, Ki=ki, Kd=kd, tau_d=tau_d, delay_cycles=delay_cycles, dcm_mode=True
)

# Generate Time Domain Transient Plot (3 rows, 2 columns)
fig, axs = plt.subplots(3, 2, figsize=(15, 10), sharex='col')
plt.subplots_adjust(hspace=0.25, wspace=0.2)

# ==========================================
# COLUMN 0: Scenario 1 (0% -> 60%)
# ==========================================
# Output Voltage
axs[0, 0].plot(t_arr1 * 1e3, v_out_arr1, label=f"Coupled (k={k_coupling})", color="#1E3A8A", linewidth=2)
axs[0, 0].plot(t_arr1 * 1e3, v_un1, label="Uncoupled (k=0)", color="#94A3B8", linestyle="--", linewidth=1.5)
axs[0, 0].axhline(y=vref, color="red", linestyle=":", label="Vref")
axs[0, 0].set_ylabel("Vo (V)", fontsize=10, fontweight="bold")
axs[0, 0].grid(True, linestyle=":", alpha=0.6)
axs[0, 0].legend(loc="upper right")
axs[0, 0].set_title("0% -> 60% Load Step: Output Voltage", fontsize=11, fontweight="bold")

# Currents
axs[1, 0].plot(t_arr1 * 1e3, i1_arr1, label="Phase 1 (Coupled)", color="#0284C7", linewidth=1.5)
axs[1, 0].plot(t_arr1 * 1e3, i2_arr1, label="Phase 2 (Coupled)", color="#F97316", linewidth=1.5)
axs[1, 0].plot(t_arr1 * 1e3, i1_arr1 + i2_arr1, label="Total Output (Coupled)", color="#10B981", linewidth=2)
axs[1, 0].plot(t_arr1 * 1e3, i1_un1, label="Phase 1 (Uncoupled)", color="#CBD5E1", linestyle="--", linewidth=1)
axs[1, 0].set_ylabel("Currents (A)", fontsize=10, fontweight="bold")
axs[1, 0].grid(True, linestyle=":", alpha=0.6)
axs[1, 0].legend(loc="upper right", ncol=2)
axs[1, 0].set_title("0% -> 60% Load Step: Currents", fontsize=11, fontweight="bold")

# Duty cycle & Load Current
ax3_twin1 = axs[2, 0].twinx()
axs[2, 0].plot(t_arr1 * 1e3, d1_arr1, label="Duty Cycle d1", color="#8B5CF6", linewidth=1.5)
ax3_twin1.plot(t_arr1 * 1e3, i_load_arr1, label="Load Current I_load", color="#EF4444", linestyle="-.", linewidth=2)
axs[2, 0].set_ylabel("Duty Cycle", fontsize=10, color="#8B5CF6", fontweight="bold")
ax3_twin1.set_ylabel("Load Current (A)", fontsize=10, color="#EF4444", fontweight="bold")
axs[2, 0].tick_params(axis='y', labelcolor="#8B5CF6")
ax3_twin1.tick_params(axis='y', labelcolor="#EF4444")
axs[2, 0].grid(True, linestyle=":", alpha=0.6)
axs[2, 0].set_xlabel("Time (ms)", fontsize=10)
axs[2, 0].set_title("0% -> 60% Load Step: Duty Cycle & Load", fontsize=11, fontweight="bold")

# ==========================================
# COLUMN 1: Scenario 2 (40% -> 100%)
# ==========================================
# Output Voltage
axs[0, 1].plot(t_arr2 * 1e3, v_out_arr2, label=f"Coupled (k={k_coupling})", color="#1E3A8A", linewidth=2)
axs[0, 1].plot(t_arr2 * 1e3, v_un2, label="Uncoupled (k=0)", color="#94A3B8", linestyle="--", linewidth=1.5)
axs[0, 1].axhline(y=vref, color="red", linestyle=":", label="Vref")
axs[0, 1].set_ylabel("Vo (V)", fontsize=10, fontweight="bold")
axs[0, 1].grid(True, linestyle=":", alpha=0.6)
axs[0, 1].legend(loc="upper right")
axs[0, 1].set_title("40% -> 100% Load Step: Output Voltage", fontsize=11, fontweight="bold")

# Currents
axs[1, 1].plot(t_arr2 * 1e3, i1_arr2, label="Phase 1 (Coupled)", color="#0284C7", linewidth=1.5)
axs[1, 1].plot(t_arr2 * 1e3, i2_arr2, label="Phase 2 (Coupled)", color="#F97316", linewidth=1.5)
axs[1, 1].plot(t_arr2 * 1e3, i1_arr2 + i2_arr2, label="Total Output (Coupled)", color="#10B981", linewidth=2)
axs[1, 1].plot(t_arr2 * 1e3, i1_un2, label="Phase 1 (Uncoupled)", color="#CBD5E1", linestyle="--", linewidth=1)
axs[1, 1].set_ylabel("Currents (A)", fontsize=10, fontweight="bold")
axs[1, 1].grid(True, linestyle=":", alpha=0.6)
axs[1, 1].legend(loc="upper right", ncol=2)
axs[1, 1].set_title("40% -> 100% Load Step: Currents", fontsize=11, fontweight="bold")

# Duty cycle & Load Current
ax3_twin2 = axs[2, 1].twinx()
axs[2, 1].plot(t_arr2 * 1e3, d1_arr2, label="Duty Cycle d1", color="#8B5CF6", linewidth=1.5)
ax3_twin2.plot(t_arr2 * 1e3, i_load_arr2, label="Load Current I_load", color="#EF4444", linestyle="-.", linewidth=2)
axs[2, 1].set_ylabel("Duty Cycle", fontsize=10, color="#8B5CF6", fontweight="bold")
ax3_twin2.set_ylabel("Load Current (A)", fontsize=10, color="#EF4444", fontweight="bold")
axs[2, 1].tick_params(axis='y', labelcolor="#8B5CF6")
ax3_twin2.tick_params(axis='y', labelcolor="#EF4444")
axs[2, 1].grid(True, linestyle=":", alpha=0.6)
axs[2, 1].set_xlabel("Time (ms)", fontsize=10)
axs[2, 1].set_title("40% -> 100% Load Step: Duty Cycle & Load", fontsize=11, fontweight="bold")

plt.savefig(os.path.join(artifact_dir, "transient_response.png"), dpi=150, bbox_inches='tight')
plt.close()

# Generate Frequency Domain Bode Plot (2x2 Grid)
freqs = bode_res['freqs']
T_mag = 20.0 * np.log10(np.abs(bode_res['T']))
T_phase = np.unwrap(np.angle(bode_res['T'], deg=True) * np.pi / 180.0) * 180.0 / np.pi

CL_mag = 20.0 * np.log10(np.abs(bode_res['G_CL']))
CL_phase = np.unwrap(np.angle(bode_res['G_CL'], deg=True) * np.pi / 180.0) * 180.0 / np.pi

# Find Closed-Loop -3dB Bandwidth (f_bw)
f_bw = None
under_3db = np.where(CL_mag < -3.0)[0]
if len(under_3db) > 0:
    f_bw = freqs[under_3db[0]]

fig_bode, axs_bode = plt.subplots(2, 2, figsize=(15, 8), sharex=True)
plt.subplots_adjust(hspace=0.2, wspace=0.2)

# ==========================================
# COLUMN 0: Open-Loop Bode Plot T(s)
# ==========================================
# Open-Loop Magnitude
ax_mag_ol = axs_bode[0, 0]
ax_mag_ol.semilogx(freqs, T_mag, color="#2563EB", linewidth=2.5, label="Loop Gain |T|")
ax_mag_ol.semilogx(freqs, 20.0 * np.log10(np.abs(bode_res['Gvd'])), color="#94A3B8", linestyle=":", alpha=0.8, label="|Gvd| Plant")
ax_mag_ol.semilogx(freqs, 20.0 * np.log10(np.abs(bode_res['Gc'])), color="#8B5CF6", linestyle="--", alpha=0.8, label="|Gc| Compensator")
ax_mag_ol.axhline(y=0, color="black", linestyle="-", linewidth=1.2)
if bode_res['fc']:
    ax_mag_ol.axvline(x=bode_res['fc'], color="red", linestyle="--", label=f"fc = {bode_res['fc']/1e3:.2f} kHz")
ax_mag_ol.set_ylabel("Gain (dB)", fontsize=10, fontweight="bold")
ax_mag_ol.grid(True, which="both", linestyle=":", alpha=0.5)
ax_mag_ol.legend(loc="lower left")
ax_mag_ol.set_title("Open-Loop Loop Gain T(s) Magnitude", fontsize=11, fontweight="bold")
ax_mag_ol.set_ylim([-40, 50])

# Open-Loop Phase
ax_phase_ol = axs_bode[1, 0]
ax_phase_ol.semilogx(freqs, T_phase, color="#E11D48", linewidth=2.5, label="Phase ∠T")
ax_phase_ol.axhline(y=-180, color="black", linestyle="-", linewidth=1.2)
if bode_res['fc']:
    ax_phase_ol.axvline(x=bode_res['fc'], color="red", linestyle="--")
    p_idx = np.argmin(np.abs(freqs - bode_res['fc']))
    ax_phase_ol.plot(bode_res['fc'], T_phase[p_idx], 'ro')
    ax_phase_ol.annotate(f"PM = {bode_res['PM']:.1f}°", 
                         xy=(bode_res['fc'], T_phase[p_idx]), 
                         xytext=(bode_res['fc']*1.5, T_phase[p_idx] + 20),
                         arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=6))
ax_phase_ol.set_ylabel("Phase (deg)", fontsize=10, fontweight="bold")
ax_phase_ol.set_xlabel("Frequency (Hz)", fontsize=10)
ax_phase_ol.grid(True, which="both", linestyle=":", alpha=0.5)
ax_phase_ol.set_ylim([-270, 90])
ax_phase_ol.set_yticks([-270, -180, -90, 0, 90])
ax_phase_ol.set_title("Open-Loop Loop Gain T(s) Phase", fontsize=11, fontweight="bold")

# ==========================================
# COLUMN 1: Closed-Loop Bode Plot G_CL(s)
# ==========================================
# Closed-Loop Magnitude
ax_mag_cl = axs_bode[0, 1]
ax_mag_cl.semilogx(freqs, CL_mag, color="#10B981", linewidth=2.5, label="Closed-Loop |G_CL|")
ax_mag_cl.axhline(y=0, color="black", linestyle="-", linewidth=1.2)
ax_mag_cl.axhline(y=-3, color="gray", linestyle=":", alpha=0.7, label="-3 dB")
if f_bw:
    ax_mag_cl.axvline(x=f_bw, color="darkgreen", linestyle="--", label=f"BW (-3dB) = {f_bw/1e3:.2f} kHz")
ax_mag_cl.set_ylabel("Gain (dB)", fontsize=10, fontweight="bold")
ax_mag_cl.grid(True, which="both", linestyle=":", alpha=0.5)
ax_mag_cl.legend(loc="lower left")
ax_mag_cl.set_title("Closed-Loop G_CL(s) Magnitude", fontsize=11, fontweight="bold")
ax_mag_cl.set_ylim([-40, 10])

# Closed-Loop Phase
ax_phase_cl = axs_bode[1, 1]
ax_phase_cl.semilogx(freqs, CL_phase, color="#D97706", linewidth=2.5, label="Phase ∠G_CL")
if f_bw:
    ax_phase_cl.axvline(x=f_bw, color="darkgreen", linestyle="--")
ax_phase_cl.set_ylabel("Phase (deg)", fontsize=10, fontweight="bold")
ax_phase_cl.set_xlabel("Frequency (Hz)", fontsize=10)
ax_phase_cl.grid(True, which="both", linestyle=":", alpha=0.5)
ax_phase_cl.set_ylim([-270, 90])
ax_phase_cl.set_yticks([-270, -180, -90, 0, 90])
ax_phase_cl.set_title("Closed-Loop G_CL(s) Phase", fontsize=11, fontweight="bold")

plt.savefig(os.path.join(artifact_dir, "bode_plots.png"), dpi=150, bbox_inches='tight')
plt.close()

# Generate Output Impedance Plot
Z_ol_mag = np.abs(bode_res['Z_ol']) * 1e3 # convert to mOhm
Z_cl_mag = np.abs(bode_res['Z_cl']) * 1e3 # convert to mOhm

fig_z, ax_z = plt.subplots(figsize=(10, 5.5))
ax_z.loglog(freqs, Z_ol_mag, color="#94A3B8", linestyle="--", linewidth=2, label="Open-Loop Output Impedance |Z_ol|")
ax_z.loglog(freqs, Z_cl_mag, color="#EF4444", linewidth=2.5, label="Closed-Loop Output Impedance |Z_cl|")

# Reference levels
dcr_eq_mOhm = (Rdcr / 2.0) * 1e3
esr_mOhm = Resr * 1e3
ax_z.axhline(y=dcr_eq_mOhm, color="gray", linestyle=":", alpha=0.7, label=f"DCR_eq ({dcr_eq_mOhm:.1f} mΩ)")
ax_z.axhline(y=esr_mOhm, color="blue", linestyle=":", alpha=0.7, label=f"ESR ({esr_mOhm:.1f} mΩ)")

if f_bw:
    ax_z.axvline(x=f_bw, color="darkgreen", linestyle="--", label=f"Closed-Loop BW = {f_bw/1e3:.2f} kHz")
if bode_res['fc']:
    ax_z.axvline(x=bode_res['fc'], color="red", linestyle="--", label=f"Crossover fc = {bode_res['fc']/1e3:.2f} kHz")

ax_z.set_xlabel("Frequency (Hz)", fontsize=10)
ax_z.set_ylabel("Impedance Magnitude (mΩ)", fontsize=10, fontweight="bold")
ax_z.set_title("Converter Output Impedance Frequency Response (|Z_out|)", fontsize=11, fontweight="bold")
ax_z.grid(True, which="both", linestyle=":", alpha=0.5)
ax_z.legend(loc="upper right")
ax_z.set_ylim([1e-2, 1e3]) # from 10 uOhm to 1 Ohm

plt.savefig(os.path.join(artifact_dir, "output_impedance.png"), dpi=150, bbox_inches='tight')
plt.close()

print("Plots successfully generated in artifacts folder!")
print(f"fc: {bode_res['fc']/1e3 if bode_res['fc'] else None} kHz, PM: {bode_res['PM']} deg")
