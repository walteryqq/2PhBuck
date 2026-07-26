import numpy as np

def simulate_coupled_buck(
    # Converter parameters
    Vin=12.0,           # Input voltage (V)
    Vref=1.0,           # Reference output voltage (V)
    L=1.0e-6,           # Phase self-inductance (H)
    k_coupling=0.5,     # Coupling coefficient (0 = uncoupled, >0 = negative coupling)
    Rdcr=5.0e-3,        # Inductor DCR (Ohm)
    C1=800.0e-6,        # Output capacitance 1 (F)
    Resr1=2.0e-3,       # Capacitor 1 ESR (Ohm)
    C2=700.0e-6,        # Output capacitance 2 (F)
    Resr2=2.0e-3,       # Capacitor 2 ESR (Ohm)
    Rload_init=1.0,     # Initial load resistance (Ohm)
    Rload_step=0.2,     # Step load resistance (Ohm)
    t_step=1.0e-3,      # Time of load step (s)
    # Control parameters
    fs=200e3,           # Switching frequency (Hz)
    fctrl=200e3,        # Controller sampling/update frequency (Hz)
    Kp=2.0,             # PID proportional gain
    Ki=15000.0,         # PID integral gain (continuous equivalent)
    Kd=2.0e-6,          # PID derivative gain (continuous equivalent)
    tau_d=1.0e-6,       # Derivative filter time constant (s)
    delay_cycles=1.5,   # MCU delay in switching cycles (computation + PWM update delay)
    t_sim=2.5e-3,        # Total simulation time (s)
    dt=None,             # Simulation time step (s)
    dcm_mode=True        # Enable diode emulation (DCM) to prevent negative currents
):
    """
    Simulates a 2-phase interleaved Buck converter with a negatively coupled inductor and two parallel capacitors.
    Uses RK4 solver and models a digital MCU PID controller with sampling delay.
    """
    # 1. Derived parameters
    M = k_coupling * L
    delta = L**2 - M**2
    if delta <= 0:
        raise ValueError("Coupling coefficient must satisfy |k| < 1.0")
        
    Tsw = 1.0 / fs
    Tctrl = 1.0 / fctrl
    
    # Choose time step
    if dt is None:
        dt = Tsw / 250.0
        
    n_steps = int(np.ceil(t_sim / dt))
    
    # Controller delay buffer size
    delay_time = delay_cycles * Tsw
    delay_steps = int(np.round(delay_time / Tctrl))
    if delay_steps < 0:
        delay_steps = 0

    # Continuous Time coefficients
    c_i_self = - L * Rdcr / delta
    c_i_mut  = - M * Rdcr / delta
    c_i_vo   = - (L + M) / delta
    
    c_u_self = L / delta
    c_u_mut  = M / delta
    
    # 3. State initialization
    # x = [i1, i2, vc1, vc2]^T
    i_steady = (Vref / Rload_init) / 2.0
    x = np.array([i_steady, i_steady, Vref, Vref])
    
    # Arrays for recording results
    t_arr = np.linspace(0, t_sim, n_steps)
    i1_arr = np.zeros(n_steps)
    i2_arr = np.zeros(n_steps)
    v_out_arr = np.zeros(n_steps)
    i_load_arr = np.zeros(n_steps)
    d1_arr = np.zeros(n_steps)
    d2_arr = np.zeros(n_steps)
    
    # Controller variables
    d_cmd = Vref / Vin  # Initial duty cycle guess (open-loop)
    d_cmd_queue = [d_cmd] * (delay_steps + 1)
    
    # PI controller terms
    integral_error = d_cmd / Ki if Ki > 0 else 0.0
    prev_error = 0.0
    prev_deriv = 0.0
    
    last_ctrl_time = -Tctrl
    
    inv_resr1 = 1.0 / Resr1
    inv_resr2 = 1.0 / Resr2
    
    # 4. Simulation Loop (RK4)
    for step in range(n_steps):
        t = t_arr[step]
        
        # Load step logic
        Rload = Rload_init if t < t_step else Rload_step
        
        # Output voltage formula for parallel capacitors
        i_sum = x[0] + x[1]
        v_out = (x[2] * inv_resr1 + x[3] * inv_resr2 + i_sum) / (inv_resr1 + inv_resr2 + 1.0 / Rload)
        i_load = v_out / Rload
        
        # Digital Controller Update
        if t - last_ctrl_time >= Tctrl:
            last_ctrl_time = t
            v_sampled = v_out
            error = Vref - v_sampled
            
            if Ki > 0:
                integral_error += error * Tctrl
                
            deriv_term = (Kd * (error - prev_error) + tau_d * prev_deriv) / (tau_d + Tctrl)
            
            d_out = Kp * error + Ki * integral_error + deriv_term
            
            d_min, d_max = 0.02, 0.95
            if d_out > d_max:
                d_out = d_max
                if Ki > 0:
                    integral_error -= error * Tctrl
            elif d_out < d_min:
                d_out = d_min
                if Ki > 0:
                    integral_error -= error * Tctrl
                    
            prev_error = error
            prev_deriv = deriv_term
            
            d_cmd_queue.append(d_out)
            d_cmd_queue.pop(0)
            
        d_active = d_cmd_queue[0]
        
        # Interleaved PWM Generation
        t_cycle_norm_1 = (t % Tsw) / Tsw
        S1 = 1.0 if t_cycle_norm_1 < d_active else 0.0
        
        t_cycle_norm_2 = ((t + 0.5 * Tsw) % Tsw) / Tsw
        S2 = 1.0 if t_cycle_norm_2 < d_active else 0.0
        
        i1_arr[step] = x[0]
        i2_arr[step] = x[1]
        v_out_arr[step] = v_out
        i_load_arr[step] = i_load
        d1_arr[step] = S1 * d_active
        d2_arr[step] = S2 * d_active
        
        # RK4 ODE Integration
        def f_state(x_val, Rload_val, S1_val, S2_val):
            i1, i2, vc1, vc2 = x_val
            i_sum_val = i1 + i2
            v_out_val = (vc1 * inv_resr1 + vc2 * inv_resr2 + i_sum_val) / (inv_resr1 + inv_resr2 + 1.0 / Rload_val)
            
            vin1 = S1_val * Vin
            vin2 = S2_val * Vin
            
            di1_dt = c_i_self * i1 + c_i_mut * i2 + c_i_vo * v_out_val + c_u_self * vin1 + c_u_mut * vin2
            di2_dt = c_i_mut * i1 + c_i_self * i2 + c_i_vo * v_out_val + c_u_mut * vin1 + c_u_self * vin2
            
            dvc1_dt = (v_out_val - vc1) / (Resr1 * C1)
            dvc2_dt = (v_out_val - vc2) / (Resr2 * C2)
            
            return np.array([di1_dt, di2_dt, dvc1_dt, dvc2_dt])
            
        k1 = f_state(x, Rload, S1, S2)
        k2 = f_state(x + 0.5 * dt * k1, Rload, S1, S2)
        k3 = f_state(x + 0.5 * dt * k2, Rload, S1, S2)
        k4 = f_state(x + dt * k3, Rload, S1, S2)
        
        x = x + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        if dcm_mode:
            if x[0] < 0.0:
                x[0] = 0.0
            if x[1] < 0.0:
                x[1] = 0.0
        
    return t_arr, i1_arr, i2_arr, v_out_arr, i_load_arr, d1_arr, d2_arr


def bode_analysis(
    Vin=12.0, L=1.0e-6, k_coupling=0.5, Rdcr=5.0e-3, C1=800.0e-6, Resr1=2.0e-3, C2=700.0e-6, Resr2=2.0e-3, Rload=1.0,
    Kp=2.0, Ki=15000.0, Kd=2.0e-6, tau_d=1.0e-6, delay_cycles=1.5, fs=200e3,
    freqs=None
):
    """
    Calculates the frequency response of the plant Gvd(s) with two parallel capacitors,
    and open-loop loop gain T(s) = Gvd(s) * Gc(s) * exp(-s * Tdelay).
    """
    if freqs is None:
        freqs = np.logspace(1, 6, 1000)
        
    s = 2j * np.pi * freqs
    
    Leq = L * (1.0 - k_coupling) / 2.0
    Rdcr_eq = Rdcr / 2.0
    
    # 1. Z_L series branch impedance
    Z_L = s * Leq + Rdcr_eq
    
    # 2. Capacitor impedances
    Z_C1 = np.zeros_like(s, dtype=complex)
    Z_C2 = np.zeros_like(s, dtype=complex)
    
    valid_c = freqs > 0
    Z_C1[valid_c] = 1.0 / (s[valid_c] * C1) + Resr1
    Z_C1[~valid_c] = 1e6
    
    Z_C2[valid_c] = 1.0 / (s[valid_c] * C2) + Resr2
    Z_C2[~valid_c] = 1e6
    
    # Equivalent parallel capacitor impedance
    Z_C = (Z_C1 * Z_C2) / (Z_C1 + Z_C2)
    
    # Parallel branch impedance Z_p = Z_C || Rload
    Z_p = (Z_C * Rload) / (Z_C + Rload)
    
    # Transfer function Gvd(s) = Vin * Z_p / (Z_L + Z_p)
    Gvd = Vin * Z_p / (Z_L + Z_p)
    
    # 3. PID Compensator Gc(s)
    Gc = np.zeros_like(s, dtype=complex)
    Gc[valid_c] = Kp + Ki / s[valid_c] + (Kd * s[valid_c]) / (1.0 + tau_d * s[valid_c])
    Gc[~valid_c] = Kp + Ki / (1e-6 * 2j * np.pi)
    
    # 4. Delay term
    Tdelay = delay_cycles / fs
    Gdelay = np.exp(-s * Tdelay)
    
    # 5. Open-loop Loop Gain
    T = Gvd * Gc * Gdelay
    
    # 6. Stability Margins
    mag_T = np.abs(T)
    phase_T = np.angle(T, deg=True)
    
    fc = None
    pm = None
    
    zero_db_crossings = np.where(np.diff(np.sign(mag_T - 1)))[0]
    if len(zero_db_crossings) > 0:
        idx = zero_db_crossings[-1]
        f1, f2 = freqs[idx], freqs[idx+1]
        m1, m2 = mag_T[idx], mag_T[idx+1]
        fc = f1 + (f2 - f1) * (1.0 - m1) / (m2 - m1)
        
        p1, p2 = phase_T[idx], phase_T[idx+1]
        phase_at_fc = p1 + (p2 - p1) * (fc - f1) / (f2 - f1)
        pm = phase_at_fc + 180.0
        pm = (pm + 180.0) % 360.0 - 180.0
        
    gm = None
    gm_freq = None
    phase_crossings = np.where(np.diff(np.sign(phase_T + 180.0)))[0]
    if len(phase_crossings) > 0:
        idx_g = phase_crossings[0]
        f1, f2 = freqs[idx_g], freqs[idx_g+1]
        p1, p2 = phase_T[idx_g], phase_T[idx_g+1]
        gm_freq = f1 + (f2 - f1) * (-180.0 - p1) / (p2 - p1)
        
    # 7. Output Impedance
    Z_ol = (Z_L * Z_C) / (Z_L + Z_C)
    Z_cl = Z_ol / (1.0 + T)
    
    G_CL = T / (1.0 + T)
        
    return {
        'freqs': freqs,
        'Gvd': Gvd,
        'Gc': Gc,
        'T': T,
        'G_CL': G_CL,
        'Z_ol': Z_ol,
        'Z_cl': Z_cl,
        'fc': fc,
        'PM': pm,
        'GM': gm,
        'gm_freq': gm_freq,
        'Leq': Leq
    }

def simulate_open_loop(
    Vin=12.0, Vref=1.0, L=1.0e-6, k_coupling=0.5, Rdcr=5.0e-3,
    C1=800.0e-6, Resr1=2.0e-3, C2=700.0e-6, Resr2=2.0e-3,
    Rload_init=1.0, Rload_step=0.2, t_sim=2.5e-3, t_step=1.0e-3,
    fs=200e3
):
    """
    Simulates the open-loop transient response of the coupled buck converter under a load step,
    while operating at a fixed, constant duty cycle (D = Vref / Vin).
    """
    M = k_coupling * L
    delta = L**2 - M**2
    if delta <= 0:
        raise ValueError("Coupling coefficient must satisfy |k| < 1.0")
        
    d_fixed = Vref / Vin
    i_steady_init = (Vref / Rload_init) / 2.0
    x = np.array([i_steady_init, i_steady_init, Vref, Vref])
    
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
    
    def derivatives(x_val, Rload_val):
        i1, i2, vc1, vc2 = x_val
        i_sum = i1 + i2
        vo = (vc1 * inv_resr1 + vc2 * inv_resr2 + i_sum) / (inv_resr1 + inv_resr2 + 1.0 / Rload_val)
        ic1 = (vo - vc1) / Resr1
        ic2 = (vo - vc2) / Resr2
        vc1_dot = ic1 / C1
        vc2_dot = ic2 / C2
        
        v1_sw = d_fixed * Vin
        v2_sw = d_fixed * Vin
        
        term1 = v1_sw - i1 * Rdcr - vo
        term2 = v2_sw - i2 * Rdcr - vo
        
        di1_dt = (L * term1 - M * term2) / delta
        di2_dt = (L * term2 - M * term1) / delta
        
        return np.array([di1_dt, di2_dt, vc1_dot, vc2_dot])

    for step in range(n_steps):
        t = t_arr[step]
        Rload = Rload_init if t < t_step else Rload_step
        d_arr[step] = d_fixed
        
        k1 = dt * derivatives(x, Rload)
        k2 = dt * derivatives(x + 0.5 * k1, Rload)
        k3 = dt * derivatives(x + 0.5 * k2, Rload)
        k4 = dt * derivatives(x + k3, Rload)
        x = x + (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
        
        i_sum = x[0] + x[1]
        vo = (x[2] * inv_resr1 + x[3] * inv_resr2 + i_sum) / (inv_resr1 + inv_resr2 + 1.0 / Rload)
        v_out_arr[step] = vo
        i1_arr[step] = x[0]
        i2_arr[step] = x[1]
        
    return t_arr, v_out_arr, i1_arr, i2_arr, d_arr
