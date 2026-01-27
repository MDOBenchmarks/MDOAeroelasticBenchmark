import matplotlib.pyplot as plt
import niceplots

plt.style.use(niceplots.get_style())
niceColours = niceplots.get_colors()

cruiseMach = 0.77
machOffset = 0.02

fig, ax = plt.subplots()
ax.set_ylabel(r"$M$", rotation="horizontal", ha="right")
ax.set_xlabel(r"$\alpha$ [deg]")

machNumbers = [cruiseMach - machOffset, cruiseMach, cruiseMach + machOffset]
alphas = [-1, 0, 1]

for mach in machNumbers:
    for alpha in alphas:
        ax.plot(alpha, mach, "o", c=niceColours["Yellow"], markersize=10, clip_on=False)

ax.set_yticks(machNumbers)
ax.set_xticks(alphas)
ax.set_xticklabels([r"$\alpha_\text{cruise} - 1$", r"$\alpha_\text{cruise}$", r"$\alpha_\text{cruise} + 1$"])
niceplots.adjust_spines(ax, outward=True)

niceplots.save_figs(fig, "PostOptimalityPolarStencil", formats=["png", "svg", "pdf"])
