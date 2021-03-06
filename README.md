# SNV_Stats_Generator
SNV Quality Stats Generator provides summaries of high and low quality SNV calls from the GHRU mapping pipeline

## What is in this repo?
**SNV_Stats_Generator.py** - python script for extracting high (PASS),low (LowQual), and heterozygous SNV calls from bcf files produced by the GHRU mapping pipeline (available at: https://gitlab.com/cgps/ghru/pipelines/snp_phylogeny/).  Output is a tsv file of PASS and LowQual SNVs both inside and outside excluded reigons (e.g. repetitive and prophage reigons normally exlcuded for phylogentic analyses).  &nbsp;

#### Example output:
```
column -t example_snv_qc_summary.tsv

File                      PASS  LowQual  Percent_LowQual  Hets  Percent_Hets   Non-excluded_PASS  Non-excluded_LowQual  Non-excluded_percent_LowQual  Non-excluded_Hets  Non-excluded_percent_Hets
23584_2#44.filtered.bcf   782   202      25.831202046     17    2.17391304348   485                7                     1.44329896907                 2                  0.412371134021
B457_merged.filtered.bcf  533   184      34.521575985     27    5.06566604128   374                44                    11.7647058824                 7                  1.87165775401
```

**CT18_repeats_phages_excluded_regions.tsv** - Phage and repeat regions normally excluded from phylogenetic analysis of S. Typhi (CT18: accession no. AL513382).&nbsp;

**run_ghru_snv_stats_in_batches.sh** - wrapper script for batch submission of jobs via lsf cluster system.&nbsp;

**Plot_Low_Qual_SNV_Distribution.R** - example R plotting script - visualises the distribution of low qual SNV calls throughout the reference sequence both before an after the removal of those falling within repetitive and phage regions (normally excluded for phylogenetic analysis).&nbsp;

**Plot_Het_SNV_Distributions.R** - example R plotting script for iterating over vcf files (converted from bcf - see below) - visualises the distribution of Het SNV calls throughout the reference sequence both before an after the removal of those falling within repetitive and phage regions (normally excluded for phylogenetic analysis).&nbsp;

#### Example plot from above R code
- Note that '--save_high_lowqual True' must be used with the above python script to save compatible vcf files (converted from bcf) for use with the R script. The default is 'False' as the files can be very large (~700Mb).  It may be worth changing the percentage cutoff (10% non-excluded lowqual SNVs) in the code for saving vcfs depending on the QC issue being diagnosed.  A suggested bash one liner is provided at the end of the page for converting bcf files to vcf files manually.  Red points indicate the alternative allele, black points indicate the reference allele.
- For other more sophisticatd vcf visualisation options please see: https://github.com/zadyson/SNV_plotter 

![image](https://user-images.githubusercontent.com/8507671/144291749-873ebfed-dc10-48d6-a525-b9123f62f08c.png)




## Example usage and key information

### Cluster modules (and dependancies) to load before running the script:

```
python2

module load bsub.py/0.42.1

module load bcftools/1.2--h02bfda8_4

module load samtools/0.1.19--h94a8ba4_6
```
- Note bsub.py is only required if submitting batches of jobs to the Sanger lsf cluster system.  


### Example usage (running from command prompt):
```
python2 GHRU_SNV_Stats_Generator.py --bcf *.bcf --excluded_regions CT18_repeats_phages_excluded_regions.tsv  --chromosome_size 4809037 --output_prefix test --save_high_lowqual False
```

### Example useage (batch submission to lsf):
```
run_ghru_snv_stats_in_batches.sh Wong2015_Tanzania
```

#### Suggestions for selecting subsets of a larger dataset to analyse
```
while read file; do ln -s /lustre/scratch118/infgen/team216/jk27/typhinet/*/ghru_mapping/filtered_bcfs/${file}.filtered.bcf ./; done<ids.txt
```
- Where ids.txt is a plain text file (e.g. created with nano) where one lane id is given per line.

#### Suggestions for extracting vcf from bcf for plotting
```
for file in *.filtered.bcf; do bcftools view $file | bcftools view > ${file}.vcf; done
```


#### Funding and acknowledgements
This project has received funding from the European Union's Horizon 2020 research and innovation programme under the Marie Sklodowska-Curie grant agreement No 845681. <img src="https://user-images.githubusercontent.com/8507671/153406979-9462c466-5a65-469e-adb6-14e271fd9e21.jpg" height="30" />
