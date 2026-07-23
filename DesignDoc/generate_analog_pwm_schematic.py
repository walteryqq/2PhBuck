import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def draw_analog_pwm():
    plt.rcParams['font.sans-serif'] = ['STHeiti', 'PingFang SC', 'Heiti TC', 'Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 4.5)
    ax.axis('off')
    
    # Title
    ax.text(5.25, 4.2, '经典模拟 PWM 调制与反馈环路实现电路图', fontsize=12, fontweight='bold', color='#1E3A8A', ha='center')
    
    # ---------------------------------------------------------
    # 1. Error Amplifier (EA) - PI/PID补偿器部分
    # ---------------------------------------------------------
    ea_x = 2.5
    ea_y = 2.8
    # Draw Op-Amp symbol (triangle pointing right)
    op_pts = np.array([[ea_x - 0.5, ea_y - 0.4], [ea_x - 0.5, ea_y + 0.4], [ea_x + 0.3, ea_y]])
    op_tri = patches.Polygon(op_pts, edgecolor='#475569', facecolor='#FFFFFF', lw=1.5)
    ax.add_patch(op_tri)
    ax.text(ea_x - 0.35, ea_y + 0.18, '-', fontsize=14, color='#475569', ha='center', va='center')
    ax.text(ea_x - 0.35, ea_y - 0.22, '+', fontsize=11, color='#475569', ha='center', va='center')
    ax.text(ea_x - 0.2, ea_y + 0.4, '误差放大器 (EA)', fontsize=8.5, color='#475569', ha='center')
    
    # Non-inverting input (+) connection to Vref
    plt.plot([ea_x - 1.2, ea_x - 0.5], [ea_y - 0.2, ea_y - 0.2], color='#475569', lw=1.5)
    ax.text(ea_x - 1.3, ea_y - 0.2, '基准电压\nVref', fontsize=8.5, color='#1E293B', ha='right', va='center')
    
    # Inverting input (-) connection from feedback divider
    plt.plot([ea_x - 1.2, ea_x - 0.5], [ea_y + 0.2, ea_y + 0.2], color='#475569', lw=1.5)
    ax.text(ea_x - 1.3, ea_y + 0.2, '采样反馈\nv_fb', fontsize=8.5, color='#1E293B', ha='right', va='center')
    
    # Feedback loop components (Rf and Cf in series)
    # Line up from (-) input
    plt.plot([ea_x - 0.8, ea_x - 0.8], [ea_y + 0.2, ea_y + 1.0], color='#475569', lw=1.5)
    # Rf resistor
    rect_rf = patches.Rectangle((ea_x - 0.6, ea_y + 0.9), 0.4, 0.2, edgecolor='#475569', facecolor='#FFFFFF', lw=1.5)
    ax.add_patch(rect_rf)
    ax.text(ea_x - 0.4, ea_y + 1.25, 'Rf', fontsize=8, color='#475569', ha='center')
    plt.plot([ea_x - 0.8, ea_x - 0.6], [ea_y + 1.0, ea_y + 1.0], color='#475569', lw=1.5)
    plt.plot([ea_x - 0.2, ea_x + 0.2], [ea_y + 1.0, ea_y + 1.0], color='#475569', lw=1.5)
    # Cf capacitor
    plt.plot([ea_x + 0.2, ea_x + 0.2], [ea_y + 0.8, ea_y + 1.2], color='#475569', lw=2)
    plt.plot([ea_x + 0.3, ea_x + 0.3], [ea_y + 0.8, ea_y + 1.2], color='#475569', lw=2)
    ax.text(ea_x + 0.25, ea_y + 1.3, 'Cf', fontsize=8, color='#475569', ha='center')
    plt.plot([ea_x + 0.3, ea_x + 0.5], [ea_y + 1.0, ea_y + 1.0], color='#475569', lw=1.5)
    # Line down to EA output
    plt.plot([ea_x + 0.5, ea_x + 0.5], [ea_y + 1.0, ea_y], color='#475569', lw=1.5)
    plt.plot([ea_x + 0.3, ea_x + 0.5], [ea_y, ea_y], color='#475569', lw=1.5)
    
    # ---------------------------------------------------------
    # 2. PWM Comparator (PWM 比较器)
    # ---------------------------------------------------------
    comp_x = 6.2
    comp_y = 2.4
    # Op-Amp symbol for comparator
    comp_pts = np.array([[comp_x - 0.5, comp_y - 0.4], [comp_x - 0.5, comp_y + 0.4], [comp_x + 0.3, comp_y]])
    comp_tri = patches.Polygon(comp_pts, edgecolor='#3B82F6', facecolor='#FFFFFF', lw=1.8)
    ax.add_patch(comp_tri)
    ax.text(comp_x - 0.35, comp_y + 0.18, '+', fontsize=12, color='#3B82F6', ha='center', va='center')
    ax.text(comp_x - 0.35, comp_y - 0.22, '-', fontsize=14, color='#475569', ha='center', va='center')
    ax.text(comp_x - 0.2, comp_y + 0.45, 'PWM 比较器', fontsize=9, fontweight='bold', color='#1E3B8A', ha='center')
    
    # Connection from EA output to Comparator non-inverting input (+)
    plt.plot([ea_x + 0.3, comp_x - 1.2], [ea_y, ea_y], color='#475569', lw=1.5)
    plt.plot([comp_x - 1.2, comp_x - 1.2], [ea_y, comp_y + 0.2], color='#475569', lw=1.5)
    plt.plot([comp_x - 1.2, comp_x - 0.5], [comp_y + 0.2, comp_y + 0.2], color='#475569', lw=1.5)
    ax.text((ea_x + 0.5 + comp_x - 1.2)/2, ea_y + 0.2, '控制电压 v_c(t)', fontsize=9, color='#0284C7', ha='center')
    
    # ---------------------------------------------------------
    # 3. Sawtooth Generator (三角波发生器)
    # ---------------------------------------------------------
    osc_x = 4.2
    osc_y = 0.6
    osc_w = 2.0
    osc_h = 0.8
    rect_osc = patches.Rectangle((osc_x, osc_y), osc_w, osc_h, edgecolor='#475569', facecolor='#F8FAFC', lw=1.5)
    ax.add_patch(rect_osc)
    ax.text(osc_x + osc_w/2, osc_y + osc_h/2, '振荡器 / 三角波发生器\n(OSC)', fontsize=8, color='#475569', ha='center', va='center')
    
    # Connection from OSC output to Comparator inverting input (-)
    plt.plot([osc_x + osc_w, comp_x - 0.8], [osc_y + osc_h/2, osc_y + osc_h/2], color='#475569', lw=1.5)
    plt.plot([comp_x - 0.8, comp_x - 0.8], [osc_y + osc_h/2, comp_y - 0.2], color='#475569', lw=1.5)
    plt.plot([comp_x - 0.8, comp_x - 0.5], [comp_y - 0.2, comp_y - 0.2], color='#475569', lw=1.5)
    ax.text(comp_x - 0.7, osc_y + osc_h/2 + 0.35, '三角载波\nv_ramp(t)', fontsize=8.5, color='#475569', ha='right')
    
    # Draw a mini sawtooth waveform next to connection
    sw_x = osc_x + osc_w + 0.4
    sw_y = osc_y + 0.1
    plt.plot([sw_x, sw_x + 0.2, sw_x + 0.2, sw_x + 0.4, sw_x + 0.4], [sw_y, sw_y + 0.3, sw_y, sw_y + 0.3, sw_y], color='#64748B', lw=1.2)
    # Label VM
    ax.annotate('', xy=(sw_x - 0.1, sw_y + 0.3), xytext=(sw_x - 0.1, sw_y),
                arrowprops=dict(arrowstyle="<->", color='#B45309', lw=1))
    ax.text(sw_x - 0.15, sw_y + 0.15, 'V_M', fontsize=8, color='#B45309', fontweight='bold', ha='right', va='center')
    
    # ---------------------------------------------------------
    # 4. Driver and Switch
    # ---------------------------------------------------------
    driver_x = 7.7
    driver_y = 2.0
    rect_driver = patches.Rectangle((driver_x, driver_y), 1.2, 0.8, edgecolor='#10B981', facecolor='#ECFDF5', lw=1.5)
    ax.add_patch(rect_driver)
    ax.text(driver_x + 0.6, driver_y + 0.4, '驱动电路\n(Driver)', fontsize=8.5, color='#065F46', ha='center', va='center')
    
    # Connection from Comparator output to Driver
    plt.plot([comp_x + 0.3, driver_x], [comp_y, comp_y], color='#3B82F6', lw=1.8)
    
    # Connection from Driver to MOSFET
    plt.plot([driver_x + 1.2, driver_x + 1.6], [driver_y + 0.4, driver_y + 0.4], color='#10B981', lw=1.5)
    ax.text(driver_x + 1.65, driver_y + 0.4, '开关管\nGate', fontsize=8.5, color='#0F172A', ha='left', va='center')
    
    # ---------------------------------------------------------
    # 5. Illustrative Waveforms (Inset at the bottom right)
    # ---------------------------------------------------------
    wave_x = 7.2
    wave_y = 0.3
    # Draw comparator input waveforms (Triangular + VC level)
    # 2 periods of triangle
    tx = np.array([wave_x, wave_x+0.5, wave_x+0.5, wave_x+1.0, wave_x+1.0])
    ty = np.array([wave_y, wave_y+0.6, wave_y, wave_y+0.6, wave_y])
    plt.plot(tx, ty, color='#94A3B8', linestyle=':', label='v_ramp')
    # VC line
    vc_val = wave_y + 0.35
    plt.plot([wave_x - 0.1, wave_x + 1.1], [vc_val, vc_val], color='#0284C7', lw=1.5, label='v_c')
    ax.text(wave_x - 0.15, vc_val, 'v_c', fontsize=8, color='#0284C7', ha='right', va='center')
    ax.text(wave_x + 0.3, wave_y + 0.45, 'v_ramp', fontsize=7.5, color='#64748B')
    
    # Draw resulting PWM output below it
    pwm_y = wave_y - 0.4
    plt.plot([wave_x, wave_x+0.29], [pwm_y, pwm_y], color='#10B981', lw=1.5)
    plt.plot([wave_x+0.29, wave_x+0.29], [pwm_y, pwm_y+0.3], color='#10B981', lw=1.5)
    plt.plot([wave_x+0.29, wave_x+0.5], [pwm_y+0.3, pwm_y+0.3], color='#10B981', lw=1.5)
    plt.plot([wave_x+0.5, wave_x+0.5], [pwm_y+0.3, pwm_y], color='#10B981', lw=1.5)
    plt.plot([wave_x+0.5, wave_x+0.79], [pwm_y, pwm_y], color='#10B981', lw=1.5)
    plt.plot([wave_x+0.79, wave_x+0.79], [pwm_y, pwm_y+0.3], color='#10B981', lw=1.5)
    plt.plot([wave_x+0.79, wave_x+1.0], [pwm_y+0.3, pwm_y+0.3], color='#10B981', lw=1.5)
    plt.plot([wave_x+1.0, wave_x+1.0], [pwm_y+0.3, pwm_y], color='#10B981', lw=1.5)
    
    # Label Ton and Ts
    # Draw double arrow for Ton
    ax.annotate('', xy=(wave_x + 0.29, pwm_y + 0.15), xytext=(wave_x + 0.5, pwm_y + 0.15),
                arrowprops=dict(arrowstyle="<->", color='#065F46', lw=0.8))
    ax.text(wave_x + 0.395, pwm_y + 0.22, 'Ton', fontsize=7, color='#065F46', ha='center')
    # Draw double arrow for Ts
    ax.annotate('', xy=(wave_x, pwm_y - 0.12), xytext=(wave_x + 0.5, pwm_y - 0.12),
                arrowprops=dict(arrowstyle="<->", color='#475569', lw=0.8))
    ax.text(wave_x + 0.25, pwm_y - 0.25, 'Ts (周期)', fontsize=7, color='#475569', ha='center')
    
    # Annotate d = Ton / Ts = Vc / VM
    ax.text(wave_x + 1.25, wave_y, '占空比关系:\n$d = \\frac{T_{on}}{T_s} = \\frac{v_c}{V_M}$', fontsize=8, color='#0F172A', va='center')
    
    plt.savefig("/Users/walter/Downloads/WPSSync/Work/3.Engineering/Ctrl/2PhBuck/DesignDoc/analog_pwm_schematic.png",
                dpi=300, bbox_inches='tight')
    plt.close()
    print("Analog PWM modulator schematic successfully drawn and saved.")

if __name__ == '__main__':
    draw_analog_pwm()
