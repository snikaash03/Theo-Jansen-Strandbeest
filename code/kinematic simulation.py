import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from math import sin, cos, sqrt, radians

class Point:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)

class Mechanism:
    def assemble(self, angle, mirror=False):
        mu = [38, 7.8, 15, 50, 41.5, 39.3, 61.9, 55.8, 40.1, 39.4, 36.7, 65.7, 49]
        mn = [mu[n] for n in range(13)]

        A = Point(0, 0)
        B = Point(-mn[0], -mn[1])
        C = Point(A.x + mn[2] * cos(radians(angle)), A.y + mn[2] * sin(radians(angle)))
        
        def ccw(p1, p2, px):
            return (p2.x - p1.x) * (px.y - p1.y) - (p2.y - p1.y) * (px.x - p1.x) < 0

        def linkage(p1, l1, p2, l2):
            dx, dy = p2.x - p1.x, p2.y - p1.y
            d = sqrt(dx**2 + dy**2)
            a = (l1**2 - l2**2 + d**2) / (2*d)
            Mx, My = p1.x + (dx * a/d), p1.y + (dy * a/d)
            h = sqrt(max(0.0, l1**2 - a**2))
            rx, ry = -dy * (h/d), dx * (h/d)
            R1 = Point(Mx + rx, My + ry)
            R2 = Point(Mx - rx, My - ry)
            return R1 if ccw(p1, p2, R1) else R2

        D = linkage(C, mn[3], B, mn[4])
        E = linkage(B, mn[5], C, mn[6])
        F = linkage(D, mn[7], B, mn[8])
        G = linkage(F, mn[9], E, mn[10])
        H = linkage(G, mn[11], E, mn[12])

        raw_joints = {'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F, 'G': G, 'H': H}
        
        if mirror:
            self.joints = {name: Point(-pt.x, pt.y) for name, pt in raw_joints.items()}
        else:
            self.joints = raw_joints

        self.A, self.B, self.C = self.joints['A'], self.joints['B'], self.joints['C']
        self.D, self.E, self.F = self.joints['D'], self.joints['E'], self.joints['F']
        self.G, self.H = self.joints['G'], self.joints['H']

        self.lines = [
            (self.A, self.C), (self.C, self.D), (self.B, self.D), (self.B, self.E), (self.C, self.E),
            (self.D, self.F), (self.B, self.F), (self.F, self.G), (self.E, self.G), (self.G, self.H), (self.E, self.H)
        ]
        
        return self.H

left_legs = [Mechanism(), Mechanism(), Mechanism()]
right_legs = [Mechanism(), Mechanism(), Mechanism()]

left_curves = [[leg.assemble(angle, mirror=False) for angle in range(360)] for leg in left_legs]
right_curves = [[leg.assemble(angle, mirror=True) for angle in range(360)] for leg in right_legs]

ANIM_STEP, FRAME_MS, current_angle = 2, 16, 0

plt.style.use('default')
fig, ax = plt.subplots(figsize=(13, 8.5))
fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#ffffff')

ax.set_xlim(-160, 160)
ax.set_ylim(-140, 40)
ax.set_aspect('equal')
ax.grid(True, linestyle='-', alpha=0.15, color='#000000')
ax.tick_params(colors='#333333', labelsize=9)

for spine in ax.spines.values():
    spine.set_edgecolor('#111111')
    spine.set_linewidth(1.2)

for curve in left_curves:
    ax.plot([p.x for p in curve], [p.y for p in curve], color='#0055ff', lw=1.0, alpha=0.15)
for curve in right_curves:
    ax.plot([p.x for p in curve], [p.y for p in curve], color='#ff0000', lw=1.0, alpha=0.15)

lines_L1, = ax.plot([], [], color='#0044ff', lw=3.0, zorder=6, label='Left Leg 1 (0°)')
lines_L2, = ax.plot([], [], color='#00aa50', lw=2.2, zorder=4, label='Left Leg 2 (120°)')
lines_L3, = ax.plot([], [], color='#0077aa', lw=2.2, zorder=2, label='Left Leg 3 (240°)')

lines_R1, = ax.plot([], [], color='#cc0000', lw=3.0, zorder=5, label='Right Leg 1 (180°)')
lines_R2, = ax.plot([], [], color='#ff5500', lw=2.2, zorder=3, label='Right Leg 2 (300°)')
lines_R3, = ax.plot([], [], color='#aa00aa', lw=2.2, zorder=1, label='Right Leg 3 (60°)')

dots_L1, = ax.plot([], [], 'o', color='#ffffff', ms=6, markeredgecolor='#000000', markeredgewidth=1.2, zorder=8)
dots_R1, = ax.plot([], [], 'o', color='#ffffff', ms=6, markeredgecolor='#000000', markeredgewidth=1.2, zorder=8)

foot_L1, = ax.plot([], [], 'o', color='#002288', ms=9, markeredgecolor='#000000', zorder=9)
foot_R1, = ax.plot([], [], 'o', color='#880000', ms=9, markeredgecolor='#000000', zorder=9)

quivers_L = None
quivers_R = None

ax.plot([0, -38, 38], [0, -7.8, -7.8], 's', color='#000000', ms=7, zorder=10)

ax.legend(loc='upper right', fontsize=9, facecolor='#ffffff', edgecolor='#111111', labelcolor='black')

info_box = ax.text(0.02, 0.98, '', transform=ax.transAxes, color='#000000',
                   fontfamily='monospace', fontsize=9, va='top', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='#ffffff', edgecolor='#111111', alpha=0.95))

def update_plot(angle):
    global quivers_L, quivers_R
    
    a_L1 = angle
    a_L2 = (angle + 120) % 360
    a_L3 = (angle + 240) % 360
    
    a_R1 = (angle + 180) % 360
    a_R2 = (angle + 300) % 360
    a_R3 = (angle + 60) % 360
    
    f_L1 = left_legs[0].assemble(a_L1, mirror=False)
    f_L2 = left_legs[1].assemble(a_L2, mirror=False)
    f_L3 = left_legs[2].assemble(a_L3, mirror=False)
    
    f_R1 = right_legs[0].assemble(a_R1, mirror=True)
    f_R2 = right_legs[1].assemble(a_R2, mirror=True)
    f_R3 = right_legs[2].assemble(a_R3, mirror=True)
    
    m_L_next = Mechanism(); m_L_next.assemble((a_L1 + 1) % 360, mirror=False)
    m_R_next = Mechanism(); m_R_next.assemble((a_R1 + 1) % 360, mirror=True)

    pairs = [
        (lines_L1, left_legs[0]), (lines_L2, left_legs[1]), (lines_L3, left_legs[2]),
        (lines_R1, right_legs[0]), (lines_R2, right_legs[1]), (lines_R3, right_legs[2])
    ]
    for lines_obj, leg in pairs:
        x, y = [], []
        for p1, p2 in leg.lines: x += [p1.x, p2.x, None]; y += [p1.y, p2.y, None]
        lines_obj.set_data(x, y)

    dots_L1.set_data([p.x for p in left_legs[0].joints.values()], [p.y for p in left_legs[0].joints.values()])
    dots_R1.set_data([p.x for p in right_legs[0].joints.values()], [p.y for p in right_legs[0].joints.values()])
    
    foot_L1.set_data([f_L1.x], [f_L1.y])
    foot_R1.set_data([f_R1.x], [f_R1.y])

    if quivers_L: quivers_L.remove()
    if quivers_R: quivers_R.remove()

    nodes = ['C', 'D', 'H']
    v_scale = 4.0
    
    XL = [left_legs[0].joints[n].x for n in nodes]
    YL = [left_legs[0].joints[n].y for n in nodes]
    UL = [(m_L_next.joints[n].x - left_legs[0].joints[n].x) * v_scale for n in nodes]
    VL = [(m_L_next.joints[n].y - left_legs[0].joints[n].y) * v_scale for n in nodes]
    quivers_L = ax.quiver(XL, YL, UL, VL, angles='xy', scale_units='xy', scale=1, 
                           color='#006666', width=0.005, headwidth=4.5, headlength=5.5, zorder=10)

    XR = [right_legs[0].joints[n].x for n in nodes]
    YR = [right_legs[0].joints[n].y for n in nodes]
    UR = [(m_R_next.joints[n].x - right_legs[0].joints[n].x) * v_scale for n in nodes]
    VR = [(m_R_next.joints[n].y - right_legs[0].joints[n].y) * v_scale for n in nodes]
    quivers_R = ax.quiver(XR, YR, UR, VR, angles='xy', scale_units='xy', scale=1, 
                           color='#663300', width=0.005, headwidth=4.5, headlength=5.5, zorder=10)

    vel_L1 = sqrt((UL[2]/v_scale)**2 + (VL[2]/v_scale)**2)
    vel_R1 = sqrt((UR[2]/v_scale)**2 + (VR[2]/v_scale)**2)

    info_box.set_text(
        f"HEXAPOD INTERLEAVED GAIT ENGINE\n"
        f"Master Axle Angle: {a_L1:>3d}°\n\n"
        f"LEFT SYSTEM LEADER (0° phase)\n"
        f" ├── Vector: [{UL[2]/v_scale:.2f}, {VL[2]/v_scale:.2f}] mm/deg\n"
        f" └── Velocity: {vel_L1:.2f} mm/deg\n\n"
        f"RIGHT SYSTEM LEADER (180° phase)\n"
        f" ├── Vector: [{UR[2]/v_scale:.2f}, {VR[2]/v_scale:.2f}] mm/deg\n"
        f" └── Velocity: {vel_R1:.2f} mm/deg"
    )
    canvas.draw_idle()

root = tk.Tk()
root.title("Theo Jansen 6-Leg Hexapod Structural Kinematics Panel")
root.configure(bg='#ffffff')
root.geometry("1300x900")

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

ctrl = tk.Frame(root, bg='#eeeeee', pady=8)
ctrl.pack(side=tk.BOTTOM, fill=tk.X)

angle_var = tk.IntVar(value=0)
def on_slider(val):
    global current_angle
    current_angle = int(angle_var.get())
    update_plot(current_angle)

tk.Label(ctrl, text="Central Axle Control Drive:", bg='#eeeeee', fg='#222222', font=('Courier', 9, 'bold')).pack(side=tk.LEFT, padx=(16, 4))
slider = ttk.Scale(ctrl, from_=0, to=359, variable=angle_var, command=on_slider, orient=tk.HORIZONTAL)
slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)

paused = [False]
def toggle_pause():
    paused[0] = not paused[0]
    pause_btn.config(text="▶  Run Hexapod Engine" if paused[0] else "⏸  Halt Drive System")

pause_btn = tk.Button(ctrl, text="⏸  Halt Drive System", command=toggle_pause, bg='#dddddd', fg='#000000', relief='groove', font=('Courier', 9, 'bold'), padx=12, cursor='hand2')
pause_btn.pack(side=tk.LEFT, padx=(0, 16))

anim_id = None

def animate():
    global current_angle, anim_id
    try:
        if not paused[0]:
            current_angle = (current_angle + ANIM_STEP) % 360
            angle_var.set(current_angle)
            update_plot(current_angle)
        
        anim_id = root.after(FRAME_MS, animate)
    except (tk.TclError, NameError):
        pass

def on_close():
    global anim_id
    if anim_id:
        root.after_cancel(anim_id)
    root.quit()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

update_plot(current_angle)
animate()
root.mainloop()