import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def save_results(script, columns, rows, metrics=None, stem="results", bars=False):
    folder = Path(script).resolve().parent
    with (folder / f"{stem}.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(columns)
        writer.writerows(rows)
    groups = list(dict.fromkeys(row[0] for row in rows))
    for metric in metrics or range(3, len(columns)):
        width = min(3, len(groups))
        height = (len(groups) + width - 1) // width
        fig, axes = plt.subplots(height, width, figsize=(5 * width, 4.3 * height),
                                 squeeze=False, constrained_layout=True)
        for ax, group in zip(axes.flat, groups):
            subset = [row for row in rows if row[0] == group]
            for i, name in enumerate(dict.fromkeys(row[1] for row in subset)):
                series = [row for row in subset if row[1] == name]
                xs = [row[2] for row in series]
                ys = [row[metric] for row in series]
                if bars:
                    ax.bar([x + (i - 0.5) * 0.4 for x in xs], ys, width=0.4, label=name)
                else:
                    ax.loglog(xs, ys, "o-", label=name)
            ax.set(title=group, xlabel=columns[2], ylabel=columns[metric])
            ax.legend(fontsize=8)
            ax.grid(alpha=0.2)
        for ax in list(axes.flat)[len(groups):]:
            ax.set_visible(False)
        fig.savefig(folder / f"{stem}_{metric}.png", dpi=130)
        plt.close(fig)
