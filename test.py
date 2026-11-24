

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def assign_pairs(min, max, error_list):

    for i, pair in enumerate(error_list):
        if min == pair[0] and max == pair[1]:
            return f'Q{i + 1}'

    return None


def main():

    df = pd.read_csv('results.csv')
    error_pairs = [[0.0005, 0.001], [0.0008, 0.0025] , [0.0015, 0.005], [0.003, 0.01], [0.006, 0.02]]

    df['Error_Group'] = df.apply(
        lambda row: assign_pairs(row['Min_err'], row['Max_err'], error_pairs),
        axis=1
    )



    col = df.loc[:, ['Tool', 'Coverage', 'Sensitivity', 'Error_Group']]




    baseline = df[df['Tool'] == 'BCFtools'][[
        'Coverage', 'Error_Group', "Seed", 'Sensitivity'
    ]].rename(columns={'Sensitivity': 'BCF_Sensitivity'})

    df = df.merge(baseline, on=['Coverage', 'Error_Group', "Seed"])

    df['Sensitivity_Difference'] = df['Sensitivity'] - df['BCF_Sensitivity']


    for coverage in df['Coverage'].unique():
        for error_group in df['Error_Group'].unique():

            subset = df[
                (df['Coverage'] == coverage) &
                (df['Error_Group'] == error_group) &
                (df['Tool'] != 'BCFtools')
            ]

            sns.scatterplot(data=subset, x='Tool', y='Sensitivity_Difference')

            plt.axhline(0, linestyle='--', color='black')
            plt.title(f'Coverage: {coverage} | Error Group: {error_group}')
            plt.ylabel('Sensitivity Difference vs. BCFtools')
            plt.show()
            plt.savefig(f'Figures/{coverage}_{error_group}')
            plt.close()
     


if __name__ == '__main__':
    main()