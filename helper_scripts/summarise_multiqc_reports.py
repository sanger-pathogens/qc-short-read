import os 
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 


def parse_args():
    parser = argparse.ArgumentParser(description="Summarise the trimmomatic outputs with figures")
    parser.add_argument("-m", "--multiqc-files", type=str, nargs='+',  required=True, help="trimmomatic files") 
    parser.add_argument("-o", "--output", type=str, required=True, help="Path to save files")
    parser.add_argument("-p", "--prefix", type=str, required=True, help="Prefix on any output files")
    args = parser.parse_args()
    return args

def merge_multiqc_tables(multiqc_files):
    merged_multiqc_df = pd.concat([pd.read_csv(x, sep='\t', header=0).assign(batch=os.path.basename(x).replace("multiqc_general_stats.txt","")) for x in multiqc_files])
    return merged_multiqc_df

def plot_read_length(merged_multiqc_df, out, prefix):
    read_length_plot = sns.boxplot(data=merged_multiqc_df, x="read_pair", y="avg_sequence_length")
    plt.xticks(rotation=90)
    plt.tight_layout()
    fig = read_length_plot.get_figure()
    fig.savefig(os.path.join(out, f"{prefix}_avg_sequence_length.png"))
    plt.close()

def plot_read_gc(merged_multiqc_df, out, prefix):
    read_length_plot = sns.boxplot(data=merged_multiqc_df, x="read_pair", y="percent_gc")
    plt.xticks(rotation=90)
    plt.tight_layout()
    fig = read_length_plot.get_figure()
    fig.savefig(os.path.join(out, f"{prefix}_percent_gc.png"))
    plt.close()

def plot_read_total_seqs(merged_multiqc_df, out, prefix):
    read_length_plot = sns.boxplot(data=merged_multiqc_df, x="read_pair", y="total_sequences")
    plt.xticks(rotation=90)
    plt.tight_layout()
    fig = read_length_plot.get_figure()
    fig.savefig(os.path.join(out, f"{prefix}_total_sequences.png"))
    plt.close()

def plot_read_per_dups(merged_multiqc_df, out, prefix):
    read_length_plot = sns.boxplot(data=merged_multiqc_df, x="read_pair", y="percent_duplicates")
    plt.xticks(rotation=90)
    plt.tight_layout()
    fig = read_length_plot.get_figure()
    fig.savefig(os.path.join(out, f"{prefix}_percent_duplicates.png"))
    plt.close()

def main():
    args = parse_args()
    merged_multiqc_df = merge_multiqc_tables(args.multiqc_files)

    merged_multiqc_df["read_pair"] = [x[-1] for x in merged_multiqc_df["Sample"]] 

    plot_read_length(merged_multiqc_df, args.output, args.prefix)
    plot_read_gc(merged_multiqc_df, args.output, args.prefix)
    plot_read_total_seqs(merged_multiqc_df, args.output, args.prefix)
    plot_read_per_dups(merged_multiqc_df, args.output, args.prefix)
    
    # Summarising data stratified by read pair
    fwd_df = merged_multiqc_df[merged_multiqc_df["Sample"].str.endswith("_1")]
    rev_df = merged_multiqc_df[merged_multiqc_df["Sample"].str.endswith("_2")]

    summary_stats_fwd = fwd_df.describe()
    summary_stats_rev = rev_df.describe()

    merged_multiqc_df.to_csv(os.path.join(args.output, f"{args.prefix}_summary.csv"), sep=',')
    merged_multiqc_stats = merged_multiqc_df.describe()
    merged_multiqc_stats.to_csv(os.path.join(args.output, f"{args.prefix}_summary_stats.csv"), sep=',')
    # summary_stats_fwd.to_csv(os.path.join(args.output, f"{args.prefix}_fwd_summary_stats.csv"), sep=',')
    # summary_stats_rev.to_csv(os.path.join(args.output, f"{args.prefix}_rev_summary_stats.csv"), sep=',')


if __name__ == "__main__":
    main()
