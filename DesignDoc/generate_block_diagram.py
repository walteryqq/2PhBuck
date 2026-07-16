import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_diagram():
    plt.rcParams['font.sans-serif'] = ['STHeiti', 'PingFang SC', 'Heiti TC', 'Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')
    
    # 1. Summing junction (Circle)
    sum_cx, sum_cy = 2.0, 2.0
    sum_r = 0.3
    circle = patches.Circle((sum_cx, sum_cy), sum_r, edgecolor='#64748B', facecolor='#FFFFFF', linewidth=2)
    ax.add_patch(circle)
    # Add + and - signs
    ax.text(sum_cx - 0.15, sum_cy, '+', fontsize=16, fontweight='bold', color='#1E293B', ha='center', va='center')
    ax.text(sum_cx, sum_cy - 0.18, '-', fontsize=16, fontweight='bold', color='#B91C1C', ha='center', va='center')
    
    # 2. Feedback Controller H(s) Block
    ctrl_x, ctrl_y = 3.2, 1.3
    ctrl_w, ctrl_h = 2.4, 1.4
    rect_ctrl = patches.Rectangle((ctrl_x, ctrl_y), ctrl_w, ctrl_h,
                                  edgecolor='#3B82F6', facecolor='#EFF6FF', linewidth=2)
    ax.add_patch(rect_ctrl)
    ax.text(ctrl_x + ctrl_w/2, ctrl_y + 1.0, '反馈控制器 H(s)', fontsize=10, fontweight='bold', color='#1E3A8A', ha='center')
    ax.text(ctrl_x + ctrl_w/2, ctrl_y + 0.6, 'PID 增益与延时', fontsize=8.5, color='#1E3A8A', ha='center')
    ax.text(ctrl_x + ctrl_w/2, ctrl_y + 0.25, '含 1/V_M 调制增益', fontsize=8.5, color='#4B5563', ha='center')
    
    # 3. Power Stage G_vd(s) Block
    plant_x, plant_y = 6.4, 1.3
    plant_w, plant_h = 2.2, 1.4
    rect_plant = patches.Rectangle((plant_x, plant_y), plant_w, plant_h,
                                   edgecolor='#10B981', facecolor='#ECFDF5', linewidth=2)
    ax.add_patch(rect_plant)
    ax.text(plant_x + plant_w/2, plant_y + 1.0, '主电路 Gvd(s)', fontsize=10, fontweight='bold', color='#065F46', ha='center')
    ax.text(plant_x + plant_w/2, plant_y + 0.6, '双相并联等效', fontsize=8.5, color='#065F46', ha='center')
    ax.text(plant_x + plant_w/2, plant_y + 0.25, '稳态变比 D = Vref/Vin', fontsize=8.5, color='#374151', ha='center')
    
    # 4. Arrows and Connections
    # Reference input v_ref(s)
    ax.annotate('', xy=(sum_cx - sum_r, sum_cy), xytext=(0.5, sum_cy),
                arrowprops=dict(arrowstyle="->", color='#94A3B8', lw=1.8))
    ax.text(0.6, sum_cy + 0.25, 'v̂_ref(s) (=0)', fontsize=9.5, fontweight='bold', color='#0F172A')
    
    # Error signal v_e(s)
    ax.annotate('', xy=(ctrl_x, sum_cy), xytext=(sum_cx + sum_r, sum_cy),
                arrowprops=dict(arrowstyle="->", color='#94A3B8', lw=1.8))
    ax.text((sum_cx + sum_r + ctrl_x)/2, sum_cy + 0.2, 'v̂_e(s)', fontsize=9.5, fontweight='bold', color='#64748B', ha='center')
    
    # Duty cycle d(s)
    ax.annotate('', xy=(plant_x, sum_cy), xytext=(ctrl_x + ctrl_w, sum_cy),
                arrowprops=dict(arrowstyle="->", color='#94A3B8', lw=1.8))
    ax.text((ctrl_x + ctrl_w + plant_x)/2, sum_cy + 0.2, 'd̂(s)', fontsize=9.5, fontweight='bold', color='#64748B', ha='center')
    
    # Output v(s)
    ax.annotate('', xy=(9.5, sum_cy), xytext=(plant_x + plant_w, sum_cy),
                arrowprops=dict(arrowstyle="->", color='#94A3B8', lw=1.8))
    ax.text(9.4, sum_cy + 0.25, 'v̂(s)', fontsize=10, fontweight='bold', color='#0F172A', ha='right')
    
    # Feedback loop (v(s) back to Summing Junction)
    fb_y = 0.5
    # line down from output
    plt.plot([9.0, 9.0], [sum_cy, fb_y], color='#94A3B8', lw=1.8)
    # line left to summing junction x
    plt.plot([9.0, sum_cx], [fb_y, fb_y], color='#94A3B8', lw=1.8)
    # line up to summing junction
    ax.annotate('', xy=(sum_cx, sum_cy - sum_r), xytext=(sum_cx, fb_y),
                arrowprops=dict(arrowstyle="->", color='#94A3B8', lw=1.8))
    
    plt.savefig("/Users/walter/Downloads/WPSSync/Work/3.Engineering/Ctrl/2PhBuck/DesignDoc/small_signal_diagram.png",
                dpi=300, bbox_inches='tight')
    plt.close()
    print("Small-signal diagram image successfully drawn and saved.")

if __name__ == '__main__':
    draw_diagram()
