import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import os

def to_seconds(time: str) -> float:
    time_split = time.split(':')

    if len(time_split) == 2:
        minutes, seconds = time_split
        return (int(minutes) + float(seconds) / 60) 

    elif len(time_split) == 3:
        hours, minutes, seconds = time_split
        return ((int(hours) * 60) + int(minutes) + (float(seconds) / 60))

    raise ValueError(f"Unexpected time format: {time}")


def generate_chart(name, df):
    chromosomes = ['chr1', 'chr7', 'chr13', 'chr16', 'chr19', 'chr20']

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for i, chromosome in enumerate(chromosomes):

        chrom_df = df[df['Chromosome'] == chromosome]

        sns.lineplot(
            data=chrom_df,
            x='Coverage',
            y=name,
            hue='Tool',
            ax=axes[i],
            style='Tool',
            markers=True,
            dashes=False,
            errorbar='sd',
            err_style='bars',
            err_kws={'capsize': 5, 'elinewidth': 1.5})
        

        axes[i].set_xticks([10, 20, 30, 40])
        axes[i].set_yticks([0.85, 0.90, 0.95, 1.0])
        axes[i].set_title(chromosome)

        # Remove individual legends
        if axes[i].get_legend():
            axes[i].get_legend().remove()

    # Get legend information
    handles, labels = axes[0].get_legend_handles_labels()

    fig.legend(
        handles, labels,
        title='Tool',
        loc='center',
        bbox_to_anchor=(0.90, 0.10),  # Was 0.15
        fontsize=14,
        title_fontsize=16,
        markerscale=1.5,
        frameon=True
    )

    sns.despine(fig=fig)

    # Reserve space on the bottom and right
    fig.subplots_adjust(
        left=0.08,
        right=0.82,  # Reserve 18% of figure width for legend
        top=0.93,
        bottom=0.08,
        wspace=0.25,
        hspace=0.30
    )

    # Save Figure
    fig.savefig('Figures/' + name + '.png', dpi=300, bbox_inches='tight')
    plt.show()


def main():
    df = pd.read_csv('results.csv')
    os.mkdir('Figures')
    generate_chart('Precision', df)
    generate_chart('Sensitivity', df)
    generate_chart('F-measure', df)






#     chr20 = df[df['Chromosome'] == 'chr20'].copy()

#     chr20['Coverage'] = pd.to_numeric(chr20['Coverage'])

#     sns.lineplot(
#         data=chr20,
#         x='Coverage',
#         y='Sensitivity',
#         hue='Tool',
#         style='Tool',
#         markers=True,
#         dashes=False,
#         errorbar='sd',
#         err_style='bars',
#         err_kws={'capsize': 5, 'elinewidth': 1.5}
#     )

#     sns.despine()
#     plt.title('Variant Caller sensitivity by Coverage (chr1)')
#     plt.xlabel('Sequencing Coverage')
#     plt.ylabel('sensitivity')
#     plt.xticks([10, 20, 30, 40])
#     plt.ylim(0.85, 1.00)
#     plt.grid(alpha=0.3)
#     plt.tight_layout()
#     plt.savefig('Sensitivity.png', dpi=300)
#     plt.show()
#     plt.close()


#     # sns.lineplot(
#     #         data=chr20,
#     #         x='Coverage',
#     #         y='Memory',
#     #         hue='Tool',
#     #         style='Tool',
#     #         markers=True,
#     #         dashes=False,
#     #         errorbar='sd',
#     #         err_style='bars',
#     #         err_kws={'capsize': 5, 'elinewidth': 1.5}
#     #     )
    
#     # sns.despine()
#     # plt.title('Variant Caller Memory Usage by Coverage (chr20)')
#     # plt.xlabel('Sequencing Coverage')
#     # plt.ylabel('Memory')
#     # plt.xticks([10, 20, 30, 40])
#     # plt.grid(alpha=0.3)
#     # plt.tight_layout()
#     # plt.savefig('memory.png', dpi=300)
#     # plt.show()
#     # plt.close()

#     chr20['Time_in_Seconds'] = chr20['Time'].apply(lambda x: to_seconds(x)) 
#     sns.lineplot(
#             data=chr20,
#             x='Coverage',
#             y='Time_in_Seconds',
#             hue='Tool',
#             style='Tool',
#             markers=True,
#             dashes=False,
#             errorbar='sd',
#             err_style='bars',
#             err_kws={'capsize': 5, 'elinewidth': 1.5}
#         )
    
#     sns.despine()
#     plt.title('Variant Caller Time by Coverage (chr20)')
#     plt.xlabel('Sequencing Coverage')
#     plt.ylabel('Time (minutes)')
#     plt.xticks([10, 20, 30, 40])
#     plt.tight_layout()
#     plt.savefig('time.png', dpi=300)
#     plt.show()
#     plt.close()

    

if __name__ == '__main__':
    main()
