import os 
import re
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 


def parse_args():
    parser = argparse.ArgumentParser(description="Summarise the sylphmpa file outputs with figures")
    parser.add_argument("-s", "--sylph-files", type=str, nargs='+',  required=True, help="sylph .sylphmpa files e.g. *_sylphtax_profile.sylphmpa") 
    parser.add_argument("-o", "--output", type=str, required=True, help="Path to save files")
    parser.add_argument("-p", "--prefix", type=str, required=True, help="Prefix on any output files")
    parser.add_argument("-t", "--taxon-level", type=str, required=False, default="g", choices=["d", "p", "c", "o", "f", "g", "s", "t"], help="taxonomic level (default=g)")
    args = parser.parse_args()
    return args

def merge_sylph_tables(sylph_files):
    merged_sylph_df = pd.concat([pd.read_csv(x, sep='\t', header=0).assign(batch=os.path.basename(x).replace("multiqc_general_stats.txt","")) for x in sylph_files])
    return merged_multiqc_df

def get_taxo_level_names(sylph_dataframes, taxo_l):
    # find the taxonomic level supplied in the command
    pattern = re.compile(r'{}__([^|]+)$'.format(taxo_l))

    sylph_out_df = {"sample":[],
                    "clade_name":[],
                    "taxon":[],
                    "relative_abundance":[], 
                    "sequence_abundance":[],
                    "ani":[],
                    "coverage":[]}

    for pos, sylph in enumerate(sylph_dataframes):
        sylph_df = pd.read_csv(sylph, sep='\t', header=0, comment='#').assign(sample=sylph.replace("_sylphtax_profile.sylphmpa",""))

        f_genus = sylph_df[sylph_df['clade_name'].str.contains(r'\|{}__[^|]+$'.format(taxo_l), regex=True)]

        for idx, row in f_genus.iterrows():
            sylph_out_df["clade_name"].append(row['clade_name'])
            sylph_out_df["relative_abundance"].append(row['relative_abundance'])
            sylph_out_df["sequence_abundance"].append(row['sequence_abundance'])
            sylph_out_df["ani"].append(row["ANI (if strain-level)"])
            sylph_out_df["coverage"].append(row["Coverage (if strain-level)"])
            sylph_out_df['sample'].append(row["sample"])
            taxo = pattern.search(row['clade_name'])
            match = taxo.group(1)
            sylph_out_df["taxon"].append(match)

    sylph_out_df = pd.DataFrame(sylph_out_df)
    
    return sylph_out_df

def plot_abundance(top_r_abund_df, out, prefix, taxon_l, column_name):
    top_r_abund_plot = sns.boxplot(data=top_r_abund_df, x="taxon", y=column_name)

    # Count number of samples per taxon
    counts = top_r_abund_df.groupby("taxon").size()

    # Add n labels above each box
    y_max = top_r_abund_df[column_name].max()
    group_max = top_r_abund_df.groupby("taxon")[column_name].max()

    xticklabels = [t.get_text() for t in top_r_abund_plot.get_xticklabels()]
    font_size = 9 if  not taxon_l in ["s", "t"] else 4
    for i, taxon in enumerate(xticklabels):
        n = int(counts.get(taxon, 0))
        # fallback: use overall max if this taxon somehow not in group_max
        base = group_max.get(taxon, top_r_abund_df[column_name].max())
        # if base is zero, use a small absolute offset so label is visible
        if base == 0:
            y = base + 0.01
        else:
            y = base * (1 + 0.02)

        top_r_abund_plot.text(
            i,
            y,
            f"n=\n{n}",
            ha="center",
            va="bottom",
            fontsize=font_size,
            weight="semibold"
        )

    plt.xticks(rotation=90, fontsize=9)
    plt.tight_layout()
    fig = top_r_abund_plot.get_figure()
    fig.savefig(os.path.join(out, f"{prefix}_{column_name}_{taxon_l}.png"))
    plt.close()

def main():
    args = parse_args()

    sylph_out_df = get_taxo_level_names(args.sylph_files, args.taxon_level)

    top_r_abund_df = sylph_out_df.loc[sylph_out_df.groupby('sample')['relative_abundance'].idxmax()]

    plot_abundance(top_r_abund_df, args.output, args.prefix, args.taxon_level, "sequence_abundance")
    plot_abundance(top_r_abund_df, args.output, args.prefix, args.taxon_level, "relative_abundance")

    sylph_out_df.to_csv(os.path.join(args.output, f"{args.prefix}_summary_{args.taxon_level}.csv"), sep=',', index=None)
    top_r_abund_df.to_csv(os.path.join(args.output, f"{args.prefix}_top_hit_{args.taxon_level}.csv"), sep=',', index=None)

if __name__ == '__main__':
    main()

