# GHRU_SNV_Stats_Generator
GHRU SNV Quality Stats Generator provides summaries of high and low quality SNV calls from the GHRU mapping pipeline


Example usage:

python2 GHRU_SNV_Stats_Generator.py --bcf ./bcfs/*.bcf --excluded_regions CT18_repeats_phages_excluded_regions.tsv  --chromosome_size 4809037 --output_prefix Collection_Name


Notes for selecting subsets to analyse:

while read file; do ln -s /lustre/scratch118/infgen/team216/jk27/typhinet/*/ghru_mapping/filtered_bcfs/${file}.filtered.bcf ./; done<ids.txt
