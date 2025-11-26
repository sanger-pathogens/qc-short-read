import os 
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 


def parse_args():
    parser = argparse.ArgumentParser(description="Summarise the trimmomatic outputs with figures")
    parser.add_argument("-t", "--trimmomatic-files", type=str, nargs='+',  required=True, help="trimmomatic files e.g. *_trimmomatic_statistics.csv") 
    parser.add_argument("-o", "--output", type=str, required=True, help="Path to save files")
    parser.add_argument("-p", "--prefix", type=str, required=True, help="Prefix on any output files")
    args = parser.parse_args()
    return args

def merge_trims(trims):
    merged_trims_df = pd.concat([pd.read_csv(x, sep=',', header=0).assign(batch=os.path.basename(x).replace("_trimmomatic_statistics.csv","")) for x in trims])
    return merged_trims_df

def plot_column(merged_trims, out, prefix, column_name):
    in_plot = sns.boxplot(data=merged_trims, y=column_name)
    plt.xticks(rotation=90)
    plt.tight_layout()
    fig = in_plot.get_figure()
    fig.savefig(os.path.join(out, f"{prefix}_{column_name}.png"))
    plt.close()

def main():

    args = parse_args()
    merged_trims_df = merge_trims(args.trimmomatic_files)
    merged_trims_df = merged_trims_df.reset_index(drop=True)

    plot_column(merged_trims_df, args.output, args.prefix, "Input_read_pairs")
    plot_column(merged_trims_df, args.output, args.prefix, "Both_surviving_read_percent")
    plot_column(merged_trims_df, args.output, args.prefix, "Dropped_reads")
    plot_column(merged_trims_df, args.output, args.prefix, "Dropped_read_percent")
    plot_column(merged_trims_df, args.output, args.prefix, "Both_surviving_reads")
    plot_column(merged_trims_df, args.output, args.prefix, "Forward_only_surviving_reads")
    plot_column(merged_trims_df, args.output, args.prefix, "Forward_only_surviving_read_percent")
    plot_column(merged_trims_df, args.output, args.prefix, "Reverse_only_surviving_reads")
    plot_column(merged_trims_df, args.output, args.prefix, "Reverse_only_surviving_read_percent")

    summary_stats = merged_trims_df.describe()
    merged_trims_df.to_csv(os.path.join(args.output, f"{args.prefix}_summary.csv"), sep=',', index=None)
    summary_stats.to_csv(os.path.join(args.output, f"{args.prefix}_summary_stats.csv"), sep=',')


if __name__ == "__main__":
    main()
