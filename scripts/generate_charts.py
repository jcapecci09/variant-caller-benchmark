import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import os

def to_minutes(time: str) -> float:
    time_split = time.split(':')

    if len(time_split) == 2:
        minutes, seconds = time_split
        return (int(minutes) + float(seconds) / 60) 

    elif len(time_split) == 3:
        hours, minutes, seconds = time_split
        return ((int(hours) * 60) + int(minutes) + (float(seconds) / 60))

    raise ValueError(f"Unexpected time format: {time}")


def sanitize_filename(name: str) -> str:
  return (
      name.replace(" ", "_")
      .replace("(", "")
      .replace(")", "")
      .replace("/", "_")
  )

def macro_boxplots(df):
    rate_metrics = [
        "Precision",
        "Sensitivity",
        "F-measure",
        "Indel-Precision",
        "Indel-Sensitivity",
        "Indel-F-measure",
        "Non-Indel-Precision",
        "Non-Indel-Sensitivity",
        "Non-Indel-F-measure",
    ]
    resource_metrics = ["Time_in_Minutes", "Max RSS (gb)"]
    TOOL_PALETTE = {
    "BCFtools": "#4477AA",  # Deep navy / HTSlib-inspired blue
    "FreeBayes": "#EE6677",  # Warm amber-orange
    "GATK HaplotypeCaller": "#228833",  # Deep forest/emerald green
    }

    sns.set_theme(style="ticks")

    for stat in rate_metrics:
        fig, ax = plt.subplots(figsize=(8, 5))

        sns.boxplot(
            data=df,
            x="Coverage",
            y=stat,
            hue="Tool",
            palette=TOOL_PALETTE,
            ax=ax
        )

        # ax.set_xticks(cov_ticks)
        ax.set_xlabel("Coverage")
        ax.set_ylabel(f"{stat.replace('-', ' ')}")
        ax.set_title(f"{stat.replace('_', ' ')} across Coverage")
        ax.minorticks_on()
        ax.tick_params(which="minor", axis='y', length=3, width=0.8, color="gray", direction='in')
        ax.tick_params(axis='x', which='minor', bottom=False, top=False)
        ax.tick_params(which="major", length=5, width=1.0, direction='in')


        ax.set_ylim(0.8, 1.0)
 

        ax.legend(
            title="Tool",
            loc="upper left",
            bbox_to_anchor=(1.02, 1),
            frameon=True
        )
        sns.despine(ax=ax)

        out_name = sanitize_filename(stat)
        fig.savefig(f"Figures/{out_name}.png", dpi=300, bbox_inches="tight")
        plt.close(fig)

def assign_pairs(min, max, error_list):

    for i, pair in enumerate(error_list):
        if min == pair[0] and max == pair[1]:
            return f'Q{i + 1}'

    return None


def main():
    df = pd.read_csv("results.csv")
    os.makedirs("Figures", exist_ok=True)

    error_pairs = [[0.0005, 0.001], [0.0008, 0.0025] , [0.0015, 0.005], [0.003, 0.01], [0.006, 0.02]]

    df["Time_in_Minutes"] = df["Time"].apply(to_minutes)
    df["Max RSS (gb)"] = df["Memory"] / 1024 / 1024
    df['Error_Group'] = df.apply(
        lambda row: assign_pairs(row['Min_err'], row['Max_err'], error_pairs),
        axis=1
    )
    macro_boxplots(df)

    # # Sort coverage so lines connect cleanly in order
    # df = df.sort_values("Coverage")

    # Define the grouping columns
    group_cols = ["Chromosome", "Coverage", "Seed", "Min_err", "Max_err"]

    # Extract BCFtools F-measure per group and subtract it
    baseline = (
        df[df["Tool"] == "BCFtools"]
        .set_index(group_cols)["F-measure"]
        .rename("Baseline_F")
    )

    df = df.merge(baseline, on=group_cols, how="left")
    df["Delta_F-measure"] = df["F-measure"] - df["Baseline_F"]

    # Drop helper column and save
    df.drop(columns=["Baseline_F"]).to_csv("results_with_delta.tsv", sep="\t", index=False)

    df2 = pd.read_csv('results_with_delta.tsv', sep='\t')

    df2_grouped = (
    df2.groupby(["Coverage", "Error_Group", "Tool"])["Delta_F-measure"]
    .mean()
    .reset_index()
    )

    markers = ["o", "s", "^", "D", "P", "X"]
    coverages = sorted(df2_grouped["Coverage"].unique())

    fig, ax = plt.subplots()

    for cov, marker in zip(coverages, markers):
        sns.stripplot(
            data=df2_grouped[df2_grouped["Coverage"] == cov],
            x="Error_Group",
            y="Delta_F-measure",
            hue="Tool",
            marker=marker,
            dodge=True,
            legend=(cov == coverages[0]),  # keep one Tool legend
            ax=ax,
        )
    # Add a baseline reference line at Delta_F-measure = 0 (BCFtools)
    ax.axhline(
        0,
        color="black",
        linestyle="--",
        linewidth=1.2,
        zorder=0,  # keeps the line behind your data markers
        label="BCFtools baseline (0)",
    )
    # Simple shape legend for Coverage
    cov_handles = [
        plt.Line2D([], [], marker=m, color="gray", linestyle="None", label=str(c))
        for c, m in zip(coverages, markers)
    ]
    ax.legend(
        handles=ax.get_legend_handles_labels()[0] + cov_handles,
        labels=ax.get_legend_handles_labels()[1] + [str(c) for c in coverages],
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
    )

    plt.tight_layout()
    plt.show()
    plt.savefig('Test.png')



    

if __name__ == '__main__':
    main()
