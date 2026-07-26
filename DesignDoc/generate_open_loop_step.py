import numpy as np
import matplotlib.pyplot as plt
import os

def simulate_open_loop(
    Vin=54.0, L=1.5e-6, k_coupling=0.70, Rdcr=0.35e-3,
    C1=5000e-6, Resr1=1.0e-3, C2=100e-6, Resr2=0.3e-3,
    Rload=12.2/163.93, t_sim=3.0e-3, t_step=1.0e-3,
    d_init=10.0/54.0, d_step=12.2/54.0, fs=210e3
):
    # Derived coupled parameters
    M = k_coupling * L
    delta = L**2 - M**2
    
    # State: x = [i1, i2, vc1, vc2]
    # Initialize at steady state for d_init
    v_init = d_init * Vin
    i_steady = (v_init / Rload) / 2.0
    x = np.array([i_steady, i_steady, v_init, v_init])
    
    Tsw = 1.0 / fs
    dt = Tsw / 200.0
    n_steps = int(np.ceil(t_sim / dt))
    t_arr = np.linspace(0, t_sim, n_steps)
    
    v_out_arr = np.zeros(n_steps)
    i1_arr = np.zeros(n_steps)
    i2_arr = np.zeros(n_steps)
    d_arr = np.zeros(n_steps)
    
    inv_resr1 = 1.0 / Resr1
    inv_resr2 = 1.0 / Resr2
    
    # Continuous-time state derivatives helpers
    # x_dot = A * x + B * u
    # i_dot = (L * v1 - M * v2 - L * Rdcr * i1 + M * Rdcr * i2 - (L - M) * v_out) / delta (Wait, let's check exact formula!)
    # Let's write the exact derivatives for coupled buck stage
    def derivatives(x_val, d1, d2):
        i1, i2, vc1, vc2 = x_val
        
        # Output voltage formula
        i_sum = i1 + i2
        vo = (vc1 * inv_resr1 + vc2 * inv_resr2 + i_sum) / (inv_resr1 + inv_resr2 + 1.0 / Rload)
        
        # Capacitor currents
        ic1 = (vo - vc1) / Resr1
        ic2 = (vo - vc2) / Resr2
        
        vc1_dot = ic1 / C1
        vc2_dot = ic2 / C2
        
        # Switch voltages
        v1_sw = d1 * Vin
        v2_sw = d2 * Vin
        
        # Inductor currents derivatives
        # L * di1/dt + M * di2/dt = v1_sw - i1 * Rdcr - vo
        # M * di1/dt + L * di2/dt = v2_sw - i2 * Rdcr - vo
        # di1/dt = [ L * (v1_sw - i1*Rdcr - vo) - M * (v2_sw - i2*Rdcr - vo) ] / delta
        # di2/dt = [ L * (v2_sw - i2*Rdcr - vo) - M * (v1_sw - i1*Rdcr - vo) ] / delta
        term1 = v1_sw - i1 * Rdcr - vo
        term2 = v2_sw - i2 * Rdcr - vo
        
        di1_dt = (L * term1 - M * term2) / delta
        di2_dt = (L * term2 - M * term1) / delta
        
        return np.array([di1_dt, di2_dt, vc1_dot, vc2_dot])

    # Run RK4 simulation
    for step in range(n_steps):
        t = t_arr[step]
        
        # Duty cycle step logic
        d_val = d_init if t < t_step else d_step
        d_arr[step] = d_val
        
        # Interleaved duty cycles
        # Phase 1: d1_val, Phase 2: d2_val (180 deg phase shift)
        # In open-loop average model, we can just use d1 = d2 = d_val
        d1 = d_val
        d2 = d_val
        
        # RK4 step
        k1 = dt * derivatives(x, d1, d2)
        k2 = dt * derivatives(x + 0.5 * k1, d1, d2)
        k3 = dt * derivatives(x + 0.5 * k2, d1, d2)
        k4 = dt * derivatives(x + k3, d1, d2)
        x = x + (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
        
        # Record output voltage
        i_sum = x[0] + x[1]
        vo = (x[2] * inv_resr1 + x[3] * inv_resr2 + i_sum) / (inv_resr1 + inv_resr2 + 1.0 / Rload)
        v_out_arr[step] = vo
        i1_arr[step] = x[0]
        i2_arr[step] = x[1]
        
    return t_arr, v_out_arr, i1_arr, i2_arr, d_arr

def plot_open_loop_response():
    # Set up matplotlib font for Chinese
    plt.rcParams['font.sans-serif'] = ['STHeiti', 'PingFang SC', 'Heiti TC', 'Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 1. Simulate Coupled (k = -0.70)
    t, v_c, i1_c, i2_c, d = simulate_open_loop(k_coupling=0.70)
    
    # 2. Simulate Uncoupled (k = 0)
    _, v_un, i1_un, i2_un, _ = simulate_open_loop(k_coupling=0.0)
    
    fig, axs = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True)
    
    # Voltage plot
    axs[0].plot(t * 1e3, v_c, label='耦合电感 (k = -0.70)', color='#1E3A8A', lw=2)
    axs[0].plot(t * 1e3, v_un, label='独立电感 (k = 0)', color='#94A3B8', linestyle='--', lw=1.5)
    axs[0].axhline(y=10.0, color='grey', linestyle=':', alpha=0.7)
    axs[0].axhline(y=12.2, color='red', linestyle=':', label='新稳态目标值 (12.2V)')
    axs[0].set_ylabel('输出电压 Vo (V)', fontsize=10, fontweight='bold')
    axs[0].grid(True, linestyle=':', alpha=0.6)
    axs[0].legend(loc='upper right')
    axs[0].set_title('开环占空比正阶跃响应 (D: 0.185 -> 0.226, 对应目标 Vo: 10V -> 12.2V)', fontsize=11, fontweight='bold')
    
    # Current plot
    axs[1].plot(t * 1e3, i1_c + i2_c, label='总电流 - 耦合电感', color='#10B981', lw=2)
    axs[1].plot(t * 1e3, i1_un + i2_un, label='总电流 - 独立电感', color='#F59E0B', linestyle='--', lw=1.5)
    axs[1].set_ylabel('输出总电流 Io (A)', fontsize=10, fontweight='bold')
    axs[1].set_xlabel('时间 Time (ms)', fontsize=10)
    axs[1].grid(True, linestyle=':', alpha=0.6)
    axs[1].legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig("/Users/walter/Downloads/WPSSync/Work/3.Engineering/Ctrl/2PhBuck/DesignDoc/open_loop_step_response.png", dpi=300)
    plt.close()
    print("Open-loop step response plot successfully generated and saved.")

if __name__ == '__main__':
    plot_open_loop_response()
