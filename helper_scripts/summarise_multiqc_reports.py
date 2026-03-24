import os 
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 


def parse_args():
    parser = argparse.ArgumentParser(description="Summarise the multiqc outputs with figures. The tar.gz files will need to be unzipped first. \
    The script is supposed to be able to handle several multiqc_general_stats.txt")
    parser.add_argument("-m", "--multiqc-files", type=str, nargs='+',  required=True, help="multiqc general stats files. e.g. *.multiqc_general_stats.txt") 
    parser.add_argument("-o", "--output", type=str, required=True, help="Path to save files")
    parser.add_argument("-p", "--prefix", type=str, required=True, help="Prefix on any output files")
    args = parser.parse_args()
    return args

def merge_multiqc_tables(multiqc_files):
    merged_multiqc_df = pd.concat([pd.read_csv(x, sep='\t', header=0).assign(batch=os.path.basename(x).replace("multiqc_general_stats.txt","")) for x in multiqc_files])
    return merged_multiqc_df

def plot_column(merged_multiqc_df, out, prefix, column_name):
    plot = sns.boxplot(data=merged_multiqc_df, x="read_pair", y=column_name)
    plt.xticks(rotation=90)
    plt.tight_layout()
    fig = plot.get_figure()
    fig.savefig(os.path.join(out, f"{prefix}_{column_name}.png"))
    plt.close()


def main():
    args = parse_args()
    merged_multiqc_df = merge_multiqc_tables(args.multiqc_files)

    merged_multiqc_df["read_pair"] = [x[-1] for x in merged_multiqc_df["Sample"]] 
    
    plot_column(merged_multiqc_df, args.output, args.prefix, "avg_sequence_length")
    plot_column(merged_multiqc_df, args.output, args.prefix, "percent_gc")
    plot_column(merged_multiqc_df, args.output, args.prefix, "total_sequences")
    plot_column(merged_multiqc_df, args.output, args.prefix, "percent_duplicates")

    # Summarising data stratified by read pair
    fwd_df = merged_multiqc_df[merged_multiqc_df["Sample"].str.endswith("_1")]
    rev_df = merged_multiqc_df[merged_multiqc_df["Sample"].str.endswith("_2")]

    merged_multiqc_df.to_csv(os.path.join(args.output, f"{args.prefix}_summary.csv"), sep=',', index=None)
    merged_multiqc_stats = merged_multiqc_df.describe()
    merged_multiqc_stats.to_csv(os.path.join(args.output, f"{args.prefix}_summary_stats.csv"), sep=',')


if __name__ == "__main__":
    main()
