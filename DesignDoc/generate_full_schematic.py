import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def draw_schematic():
    # Set up matplotlib font for Chinese
    plt.rcParams['font.sans-serif'] = ['STHeiti', 'PingFang SC', 'Heiti TC', 'Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
    
    # Widen figure to 12x4.5 to completely avoid any text collisions
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 4.2)
    ax.axis('off')
    
    # ---------------------------------------------------------
    # 1. Main Power Stage Rails (y = 3.2 is top, y = 1.8 is bottom)
    # ---------------------------------------------------------
    y_top = 3.2
    y_bot = 1.8
    
    # Bottom rail (Ground)
    plt.plot([0.8, 10.6], [y_bot, y_bot], color='#475569', lw=1.5)
    # Top rail sections
    plt.plot([0.8, 2.55], [y_top, y_top], color='#475569', lw=1.5)
    plt.plot([3.05, 3.6], [y_top, y_top], color='#475569', lw=1.5)
    plt.plot([4.0, 4.5], [y_top, y_top], color='#475569', lw=1.5)
    plt.plot([5.5, 5.7], [y_top, y_top], color='#475569', lw=1.5)
    plt.plot([6.3, 10.6], [y_top, y_top], color='#475569', lw=1.5)
    
    # ---------------------------------------------------------
    # 2. Components
    # ---------------------------------------------------------
    # (a) Input voltage source v_in(s)
    src_x = 0.8
    circle_in = patches.Circle((src_x, (y_top+y_bot)/2), 0.25, edgecolor='#475569', facecolor='#FFFFFF', lw=1.5)
    ax.add_patch(circle_in)
    ax.text(src_x, (y_top+y_bot)/2 + 0.05, '+', fontsize=12, color='#475569', ha='center', va='center')
    ax.text(src_x, (y_top+y_bot)/2 - 0.12, '-', fontsize=12, color='#475569', ha='center', va='center')
    plt.plot([src_x, src_x], [y_bot, (y_top+y_bot)/2 - 0.25], color='#475569', lw=1.5)
    plt.plot([src_x, src_x], [y_top, (y_top+y_bot)/2 + 0.25], color='#475569', lw=1.5)
    ax.text(src_x - 0.35, (y_top+y_bot)/2, 'v̂_in(s)', fontsize=9.5, fontweight='bold', color='#1E293B', ha='right', va='center')
    
    # (b) Dependent Current Source 98.4A * d(s)
    cs_x = 1.8
    circle_cs = patches.Circle((cs_x, (y_top+y_bot)/2), 0.25, edgecolor='#475569', facecolor='#FFFFFF', lw=1.5)
    ax.add_patch(circle_cs)
    # arrow inside
    ax.annotate('', xy=(cs_x, (y_top+y_bot)/2 - 0.15), xytext=(cs_x, (y_top+y_bot)/2 + 0.15),
                arrowprops=dict(arrowstyle="->", color='#475569', lw=1.5))
    plt.plot([cs_x, cs_x], [y_bot, (y_top+y_bot)/2 - 0.25], color='#475569', lw=1.5)
    plt.plot([cs_x, cs_x], [y_top, (y_top+y_bot)/2 + 0.25], color='#475569', lw=1.5)
    ax.text(cs_x, y_top + 0.15, '98.4A * d̂(s)', fontsize=8.5, color='#475569', ha='center')
    
    # (c) Dependent Voltage Source 239.0V * d(s)
    vs_x = 2.8
    circle_vs = patches.Circle((vs_x, y_top), 0.25, edgecolor='#475569', facecolor='#FFFFFF', lw=1.5)
    ax.add_patch(circle_vs)
    ax.text(vs_x - 0.1, y_top, '-', fontsize=11, color='#475569', ha='center', va='center')
    ax.text(vs_x + 0.1, y_top, '+', fontsize=11, color='#475569', ha='center', va='center')
    ax.text(vs_x, y_top + 0.35, '239.0V * d̂(s)', fontsize=8.5, color='#475569', ha='center')
    
    # (d) Transformer (1 : 0.226)
    tx_x = 3.8
    # primary winding
    plt.plot([tx_x - 0.1, tx_x - 0.1], [y_bot, y_top], color='#475569', lw=2)
    # secondary winding
    plt.plot([tx_x + 0.1, tx_x + 0.1], [y_bot, y_top], color='#475569', lw=2)
    # core line
    plt.plot([tx_x, tx_x], [y_bot+0.2, y_top-0.2], color='#94A3B8', lw=1.5)
    ax.text(tx_x, y_top + 0.3, '1 : 0.226', fontsize=9, fontweight='bold', color='#1E293B', ha='center')
    
    # (e) Inductor Leq = 0.23 uH
    lx_start = 4.5
    lx_end = 5.4
    l_t = np.linspace(0, 4*np.pi, 200)
    l_x = lx_start + (lx_end - lx_start) * (l_t / (4*np.pi))
    l_y = y_top + 0.08 * np.abs(np.sin(l_t))
    plt.plot(l_x, l_y, color='#D97706', lw=2)
    ax.text((lx_start+lx_end)/2, y_top + 0.25, 'Leq = 0.23 μH', fontsize=9, fontweight='bold', color='#B45309', ha='center')
    
    # (f) Resistor Rdcr_eq = 0.2 mOhm
    rx_start = 5.7
    rx_end = 6.3
    rect_r = patches.Rectangle((rx_start, y_top - 0.08), rx_end - rx_start, 0.16,
                               edgecolor='#475569', facecolor='#FFFFFF', lw=1.5)
    ax.add_patch(rect_r)
    ax.text((rx_start+rx_end)/2, y_top + 0.25, 'Rdcr_eq = 0.2 mΩ', fontsize=8.5, color='#475569', ha='center')
    
    # (g) Capacitor C1 = 5000 uF
    c1_x = 7.0
    plt.plot([c1_x, c1_x], [y_top, y_top - 0.35], color='#475569', lw=1.5)
    plt.plot([c1_x - 0.2, c1_x + 0.2], [y_top - 0.35, y_top - 0.35], color='#475569', lw=2)
    plt.plot([c1_x - 0.2, c1_x + 0.2], [y_top - 0.45, y_top - 0.45], color='#475569', lw=2)
    # Resr1 resistor
    rect_rc1 = patches.Rectangle((c1_x - 0.08, y_bot + 0.35), 0.16, 0.3,
                                 edgecolor='#475569', facecolor='#FFFFFF', lw=1.5)
    ax.add_patch(rect_rc1)
    plt.plot([c1_x, c1_x], [y_bot + 0.35, y_bot], color='#475569', lw=1.5)
    plt.plot([c1_x, c1_x], [y_top - 0.45, y_bot + 0.65], color='#475569', lw=1.5)
    ax.text(c1_x + 0.22, y_top - 0.25, 'C1 = 5000 μF', fontsize=8, color='#475569')
    ax.text(c1_x + 0.22, y_bot + 0.45, 'Resr1 = 1.0 mΩ', fontsize=8, color='#475569')
    
    # (h) Capacitor C2 = 100 uF
    c2_x = 8.1
    plt.plot([c2_x, c2_x], [y_top, y_top - 0.35], color='#475569', lw=1.5)
    plt.plot([c2_x - 0.2, c2_x + 0.2], [y_top - 0.35, y_top - 0.35], color='#475569', lw=2)
    plt.plot([c2_x - 0.2, c2_x + 0.2], [y_top - 0.45, y_top - 0.45], color='#475569', lw=2)
    # Resr2 resistor
    rect_rc2 = patches.Rectangle((c2_x - 0.08, y_bot + 0.35), 0.16, 0.3,
                                 edgecolor='#475569', facecolor='#FFFFFF', lw=1.5)
    ax.add_patch(rect_rc2)
    plt.plot([c2_x, c2_x], [y_bot + 0.35, y_bot], color='#475569', lw=1.5)
    plt.plot([c2_x, c2_x], [y_top - 0.45, y_bot + 0.65], color='#475569', lw=1.5)
    ax.text(c2_x + 0.22, y_top - 0.25, 'C2 = 100 μF', fontsize=8, color='#475569')
    ax.text(c2_x + 0.22, y_bot + 0.45, 'Resr2 = 0.3 mΩ', fontsize=8, color='#475569')
    
    # (i) Load Resistor R_load = 0.124
    rl_x = 9.1
    rect_rl = patches.Rectangle((rl_x - 0.08, (y_top+y_bot)/2 - 0.25), 0.16, 0.5,
                                edgecolor='#475569', facecolor='#FFFFFF', lw=1.5)
    ax.add_patch(rect_rl)
    # Arrow for load step
    ax.annotate('', xy=(rl_x + 0.2, (y_top+y_bot)/2 + 0.3), xytext=(rl_x - 0.2, (y_top+y_bot)/2 - 0.3),
                arrowprops=dict(arrowstyle="->", color='#475569', lw=1.2))
    plt.plot([rl_x, rl_x], [y_bot, (y_top+y_bot)/2 - 0.25], color='#475569', lw=1.5)
    plt.plot([rl_x, rl_x], [y_top, (y_top+y_bot)/2 + 0.25], color='#475569', lw=1.5)
    ax.text(rl_x + 0.22, (y_top+y_bot)/2, 'R_load = 0.124 Ω', fontsize=8.5, color='#1E293B')
    
    # (j) Dependent Current Source i_load(s)
    il_x = 10.0
    circle_il = patches.Circle((il_x, (y_top+y_bot)/2), 0.2, edgecolor='#475569', facecolor='#FFFFFF', lw=1.2)
    ax.add_patch(circle_il)
    ax.annotate('', xy=(il_x, (y_top+y_bot)/2 - 0.12), xytext=(il_x, (y_top+y_bot)/2 + 0.12),
                arrowprops=dict(arrowstyle="->", color='#475569', lw=1.2))
    plt.plot([il_x, il_x], [y_bot, (y_top+y_bot)/2 - 0.2], color='#475569', lw=1.5)
    plt.plot([il_x, il_x], [y_top, (y_top+y_bot)/2 + 0.2], color='#475569', lw=1.5)
    ax.text(il_x + 0.2, (y_top+y_bot)/2, 'î_load(s) 扰动', fontsize=8, color='#EF4444')
    
    # Output Voltage node
    plt.plot([10.0, 10.8], [y_top, y_top], color='#475569', lw=1.5)
    plt.plot([10.0, 10.8], [y_bot, y_bot], color='#475569', lw=1.5)
    ax.text(10.8, y_top + 0.15, 'v̂(s) 输出', fontsize=9.5, fontweight='bold', color='#1E293B', ha='right')
    
    # ---------------------------------------------------------
    # 3. Control Feedback Loop (y = 0.7 is loop rail)
    # ---------------------------------------------------------
    y_loop = 0.7
    
    # Node to Summing Junction
    plt.plot([10.5, 10.5], [y_top, y_loop], color='#94A3B8', lw=1.5)
    plt.plot([10.5, 8.6], [y_loop, y_loop], color='#94A3B8', lw=1.5)
    
    # (a) Summing Junction (Circle)
    sum_x = 8.2
    circle_sum = patches.Circle((sum_x, y_loop), 0.22, edgecolor='#64748B', facecolor='#FFFFFF', lw=1.5)
    ax.add_patch(circle_sum)
    ax.text(sum_x, y_loop, '+', fontsize=12, fontweight='bold', color='#64748B', ha='center', va='center')
    ax.text(sum_x + 0.18, y_loop + 0.18, '-', fontsize=11, fontweight='bold', color='#B91C1C', ha='center', va='center')
    
    # Arrow into summing junction from right
    ax.annotate('', xy=(sum_x - 0.22, y_loop), xytext=(sum_x - 0.05, y_loop),
                arrowprops=dict(arrowstyle="<-", color='#94A3B8', lw=1.5))
    
    # Reference input from bottom
    plt.plot([sum_x, sum_x], [0.15, y_loop - 0.22], color='#94A3B8', lw=1.5)
    ax.text(sum_x, 0.02, 'v̂_ref(s) (=0)', fontsize=8.5, color='#475569', ha='center')
    ax.text(sum_x - 0.18, y_loop - 0.18, '+', fontsize=11, color='#64748B', ha='center', va='center')
    
    # (b) Feedback Controller H(s) Block - Centered at 5.3 (goes from 3.8 to 6.8)
    ctrl_x = 3.8
    ctrl_w = 3.0
    rect_c = patches.Rectangle((ctrl_x, y_loop - 0.35), ctrl_w, 0.7,
                              edgecolor='#3B82F6', facecolor='#EFF6FF', lw=1.8)
    ax.add_patch(rect_c)
    ax.text(ctrl_x + ctrl_w/2, y_loop + 0.12, '反馈控制器 H(s)', fontsize=9, fontweight='bold', color='#1E3A8A', ha='center')
    ax.text(ctrl_x + ctrl_w/2, y_loop - 0.1, 'Kp=0.05, Ki=0.0002, 1/VM=1', fontsize=7.5, color='#1E3A8A', ha='center')
    ax.text(ctrl_x + ctrl_w/2, y_loop - 0.25, '延时=1.5 Tsw, fsam=100kHz', fontsize=7.5, color='#4B5563', ha='center')
    
    # Error signal line (sum_x - 0.22 = 7.98 to ctrl_x + ctrl_w = 6.8)
    ax.annotate('', xy=(ctrl_x + ctrl_w, y_loop), xytext=(sum_x - 0.22, y_loop),
                arrowprops=dict(arrowstyle="<-", color='#94A3B8', lw=1.5))
    ax.text((sum_x - 0.22 + ctrl_x + ctrl_w)/2, y_loop + 0.15, 'v̂_e(s)', fontsize=8.5, color='#475569', ha='center')
    
    # Output of controller: d(s)
    # line from ctrl output (3.8) to x=2.0
    plt.plot([ctrl_x, 2.0], [y_loop, y_loop], color='#94A3B8', lw=1.5)
    # line up to y = y_top - 0.6
    plt.plot([2.0, 2.0], [y_loop, y_top - 0.6], color='#94A3B8', lw=1.5)
    # arrow pointing to the dependent source control node
    ax.annotate('', xy=(1.9, y_top - 0.45), xytext=(2.0, y_top - 0.6),
                arrowprops=dict(arrowstyle="->", color='#94A3B8', lw=1.5))
    # horizontal branch to dependent voltage source control input
    plt.plot([2.0, 2.5], [y_top - 0.6, y_top - 0.6], color='#94A3B8', lw=1.5)
    plt.plot([2.5, 2.5], [y_top - 0.6, y_top - 0.25], color='#94A3B8', lw=1.5)
    
    ax.text(2.15, y_loop + 0.2, 'd̂(s)', fontsize=9.5, fontweight='bold', color='#64748B')
    
    # T(s) label indicator in the middle
    ax.text(5.3, y_bot - 0.2, '环路增益 T(s)', fontsize=9, color='#64748B', style='italic', ha='center')
    
    plt.savefig("/Users/walter/Downloads/WPSSync/Work/3.Engineering/Ctrl/2PhBuck/DesignDoc/coupled_buck_schematic.png",
                dpi=300, bbox_inches='tight')
    plt.close()
    print("Full circuit schematic successfully updated and saved.")

if __name__ == '__main__':
    draw_schematic()
