
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests
from itertools import combinations
import pandas as pd
from generate_charts import assign_pairs
import seaborn as sns
import matplotlib.pyplot as plt

def pairwise(df, id, id_list, vs_list, stats_list, p_value_list, adj_p_list, sig_list):
    
    
    tools = ['GATK HaplotypeCaller', 'FreeBayes', 'BCFtools']
    results = []

    
    for t1, t2 in combinations(tools, 2):
        x = df[df['Tool'] == t1]['F-measure'].to_numpy()
        y = df[df['Tool'] == t2]['F-measure'].to_numpy()

        stat, p = wilcoxon(x, y)

        results.append((t1, t2, stat, p))

    # Holm correction
    p_values = [r[3] for r in results]
    reject, corrected_p, _, _ = multipletests(
        p_values, method='holm'
    )


    for (t1, t2, stat, p), p_adj, sig in zip(
        results, corrected_p, reject):

        id_list.append(id)
        vs_list.append(f'{t1}x{t2}')
        stats_list.append(f'{stat}')
        p_value_list.append(f'{p}')
        adj_p_list.append(f'{p_adj}')
        sig_list.append(f'{sig}')


def perform_pairwise(df, col1, col2):

    vs_list = []
    id_list = []
    stats_list = []
    p_value_list = []
    adj_p_list = []
    sig_list = []

    col1_values = df.loc[:, col1].unique()
    col2_values = df.loc[:, col2].unique()

    for cov in col1_values:
        for quality in col2_values:
            subset = df[(df[col1] == cov) & (df[col2] == quality)]
            pairwise(subset, f'{cov}x{quality}', id_list, vs_list, stats_list, p_value_list, adj_p_list, sig_list)

    return pd.DataFrame({'id': id_list,
                         'comp': vs_list, 
                         'W': stats_list,
                         'p-value': p_value_list,
                         'adj-p': adj_p_list,
                         'sig': sig_list})


def main():
    df = pd.read_csv('results.csv')
    error_pairs = [[0.0005, 0.001], [0.0008, 0.0025] , [0.0015, 0.005], [0.003, 0.01], [0.006, 0.02]]
    df['Error_Group'] = df.apply(
        lambda row: assign_pairs(row['Min_err'], row['Max_err'], error_pairs),
        axis=1
    )

    sig_df = perform_pairwise(df, 'Coverage', 'Error_Group')

    sig_df["adj-p"] = pd.to_numeric(sig_df["adj-p"])

    sig_df["bucket"] = pd.cut(
        sig_df["adj-p"],
        bins=[float("-inf"), 0.001, 0.01, 0.05, float("inf")],
        labels=["***", "**", "*", "ns"],
    )

    levels = {"ns": 0, "*": 1, "**": 2, "***": 3}
    sig_df["level"] = sig_df["bucket"].map(levels).astype(int)

    heatmap_data = sig_df.pivot(
        index="id", columns="comp", values="level"
    )
    annotations = (
        sig_df.pivot(index="id", columns="comp", values="bucket")
        .astype(object)
        .fillna("")
    )

    ax = sns.heatmap(
        heatmap_data,
        annot=annotations,
        fmt="",
        cmap=sns.color_palette("YlOrRd", n_colors=4, as_cmap=True),
        vmin=-0.5,
        vmax=3.5,
        cbar_kws={"ticks": [0, 1, 2, 3], "label": "Significance"},
    )

    ax.collections[0].colorbar.set_ticklabels(["ns", "*", "**", "***"])
    plt.savefig('Heatmap.png')
    plt.show()

    


    
if __name__ == '__main__':
    main()