import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def draw_open_loop_schematic():
    # Set up matplotlib font for Chinese
    plt.rcParams['font.sans-serif'] = ['STHeiti', 'PingFang SC', 'Heiti TC', 'Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
    
    # Canvas size: spacious 14.5x3.2 layout
    fig, ax = plt.subplots(figsize=(14.5, 3.2))
    ax.set_xlim(0, 14.5)
    ax.set_ylim(1.2, 4.2)
    ax.axis('off')
    
    # Title
    ax.text(7.25, 4.0, '两相交错并联 Buck 固定比例 (Fixed 4:1 Ratio) 开环等效小信号电路模型', fontsize=11, fontweight='bold', color='#1E3A8A', ha='center')
    
    # ---------------------------------------------------------
    # 1. Main Power Stage Rails (y = 3.2 is top, y = 1.8 is bottom)
    # ---------------------------------------------------------
    y_top = 3.2
    y_bot = 1.8
    
    # Bottom rail (Ground)
    plt.plot([0.8, 14.0], [y_bot, y_bot], color='#475569', lw=1.5)
    # Top rail sections
    plt.plot([0.8, 3.6], [y_top, y_top], color='#475569', lw=1.5)
    plt.plot([4.0, 4.2], [y_top, y_top], color='#475569', lw=1.5)
    plt.plot([4.8, 5.2], [y_top, y_top], color='#475569', lw=1.5)
    plt.plot([6.0, 6.4], [y_top, y_top], color='#475569', lw=1.5)
    plt.plot([7.0, 14.0], [y_top, y_top], color='#475569', lw=1.5)
    
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
    
    # (b) Transformer (1 : 0.25 - Fixed 4:1 Ratio)
    tx_x = 3.8
    # primary winding
    plt.plot([tx_x - 0.1, tx_x - 0.1], [y_bot, y_top], color='#475569', lw=2)
    # secondary winding
    plt.plot([tx_x + 0.1, tx_x + 0.1], [y_bot, y_top], color='#475569', lw=2)
    # core line
    plt.plot([tx_x, tx_x], [y_bot+0.2, y_top-0.2], color='#94A3B8', lw=1.5)
    ax.text(tx_x, y_top + 0.3, '1 : 0.25', fontsize=9, fontweight='bold', color='#1E293B', ha='center')
    ax.text(tx_x, y_bot - 0.3, '固定占空比 D = 25%', fontsize=8, color='#475569', ha='center')
    
    # (c) Switch Equivalent Resistor Rds_eq = 0.6 mOhm (NEW - reflected GaN switch resistance)
    rsw_start = 4.2
    rsw_end = 4.8
    rect_rsw = patches.Rectangle((rsw_start, y_top - 0.08), rsw_end - rsw_start, 0.16,
                                 edgecolor='#3B82F6', facecolor='#EFF6FF', lw=1.5)
    ax.add_patch(rect_rsw)
    ax.text((rsw_start+rsw_end)/2, y_top + 0.25, 'Rds_eq = 0.6 mΩ', fontsize=8.5, fontweight='bold', color='#1D4ED8', ha='center')
    ax.text((rsw_start+rsw_end)/2, y_top - 0.25, '(GaN 导通电阻折算)', fontsize=7, color='#1E3A8A', ha='center')
    
    # (d) Inductor Leq = 0.23 uH
    lx_start = 5.2
    lx_end = 6.0
    l_t = np.linspace(0, 4*np.pi, 200)
    l_x = lx_start + (lx_end - lx_start) * (l_t / (4*np.pi))
    l_y = y_top + 0.08 * np.abs(np.sin(l_t))
    plt.plot(l_x, l_y, color='#D97706', lw=2)
    ax.text((lx_start+lx_end)/2, y_top + 0.25, 'Leq = 0.23 μH', fontsize=9, fontweight='bold', color='#B45309', ha='center')
    
    # (e) Resistor Rdcr_eq = 0.2 mOhm
    rx_start = 6.4
    rx_end = 7.0
    rect_r = patches.Rectangle((rx_start, y_top - 0.08), rx_end - rx_start, 0.16,
                               edgecolor='#475569', facecolor='#FFFFFF', lw=1.5)
    ax.add_patch(rect_r)
    ax.text((rx_start+rx_end)/2, y_top + 0.25, 'Rdcr_eq = 0.2 mΩ', fontsize=8.5, color='#475569', ha='center')
    
    # (f) Capacitor C1 = 5000 uF
    c1_x = 8.2
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
    
    # (g) Capacitor C2 = 100 uF
    c2_x = 9.6
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
    
    # (h) Load Resistor R_load = 0.124
    rl_x = 11.0
    rect_rl = patches.Rectangle((rl_x - 0.08, (y_top+y_bot)/2 - 0.25), 0.16, 0.5,
                                edgecolor='#475569', facecolor='#FFFFFF', lw=1.5)
    ax.add_patch(rect_rl)
    # Arrow for load step
    ax.annotate('', xy=(rl_x + 0.2, (y_top+y_bot)/2 + 0.3), xytext=(rl_x - 0.2, (y_top+y_bot)/2 - 0.3),
                arrowprops=dict(arrowstyle="->", color='#475569', lw=1.2))
    plt.plot([rl_x, rl_x], [y_bot, (y_top+y_bot)/2 - 0.25], color='#475569', lw=1.5)
    plt.plot([rl_x, rl_x], [y_top, (y_top+y_bot)/2 + 0.25], color='#475569', lw=1.5)
    ax.text(rl_x + 0.22, (y_top+y_bot)/2, 'R_load', fontsize=9.5, color='#1E293B')
    
    # (i) Dependent Current Source i_load(s)
    il_x = 12.4
    circle_il = patches.Circle((il_x, (y_top+y_bot)/2), 0.2, edgecolor='#475569', facecolor='#FFFFFF', lw=1.2)
    ax.add_patch(circle_il)
    ax.annotate('', xy=(il_x, (y_top+y_bot)/2 - 0.12), xytext=(il_x, (y_top+y_bot)/2 + 0.12),
                arrowprops=dict(arrowstyle="->", color='#EF4444', lw=1.2))
    plt.plot([il_x, il_x], [y_bot, (y_top+y_bot)/2 - 0.2], color='#475569', lw=1.5)
    plt.plot([il_x, il_x], [y_top, (y_top+y_bot)/2 + 0.2], color='#475569', lw=1.5)
    ax.text(il_x + 0.22, (y_top+y_bot)/2, 'î_load(s) 扰动', fontsize=8, color='#EF4444')
    
    # Output Voltage node
    plt.plot([12.4, 13.6], [y_top, y_top], color='#475569', lw=1.5)
    plt.plot([12.4, 13.6], [y_bot, y_bot], color='#475569', lw=1.5)
    ax.text(13.6, y_top + 0.15, 'v̂(s) 输出', fontsize=9.5, fontweight='bold', color='#1E293B', ha='right')
    
    plt.savefig("/Users/walter/Downloads/WPSSync/Work/3.Engineering/Ctrl/2PhBuck/DesignDoc/open_loop_schematic.png",
                dpi=300, bbox_inches='tight')
    plt.close()
    print("Fixed ratio open-loop schematic with GaN switch resistance successfully drawn.")

if __name__ == '__main__':
    draw_open_loop_schematic()
