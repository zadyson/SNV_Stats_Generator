#!/usr/bin/env python
#
# GHRU SNV Quality Stats Generator
# Dr Zoe A. Dyson (zoe.dyson@lshtm.ac.uk)
#
# Documentation - https://github.com/zadyson/GHRU_SNV_Stats_Generator
#
# Dependencies:
#	 Python2, SAMtools and bcftools are required.
#
# Last modified - November 15th, 2021
#

# Import required packages
from argparse import (ArgumentParser, FileType)
import os, sys, re, collections, operator

# Version number
__version__='0.0.6'

# Set up argument parser 
def parse_args():
	"Parse the input arguments, use '-h' for help"
	parser = ArgumentParser(description='Quality stats for SNVs called by GHRU mapping pipeline')
	parser.add_argument('--version', action='version', version='GHRU SNV Quality Stats Generator v' + __version__,
		help="Show version number and exit")
	parser.add_argument('--bcf', nargs='+', type=str, required=True,
		help='File path to bcf(s) to be analysed')
	parser.add_argument('--excluded_regions', type=str, required=True,
		help='Path to tsv file of regions to exclude (i.e. phages and repeats). Should not include a header line.')
	parser.add_argument('--chromosome_size', type=int, required=True,
		help='Size of reference chromsome')
	parser.add_argument('--output_prefix', type=str, required=True,
		help='Output file prefix')
	parser.add_argument('--save_high_lowqual', type=bool, required=False, default=False,
		help='Save vcf data for sequences with >=10% low quality SNVs in non-excluded regions')

	return parser.parse_args()


# main function
def main():
	args = parse_args()

	# Get location of script
	pwd = os.getcwd()

	# Build list of SNVs to exclude
	excluded_regions = open(args.excluded_regions , "r")
	positions_to_exclude = []
	for region in excluded_regions:
		region_coords = region.rstrip().split()
		region_bases = range(int(region_coords[0]),int(region_coords[1]))
		positions_to_exclude = positions_to_exclude + [int(region_coords[0])] + region_bases + [int(region_coords[1])]

	# Output summary file with header
	output_snv_summary = open(args.output_prefix  + "_snv_qc_summary.tsv", "w")
	output_snv_summary.write(
		"File \t PASS \t LowQual \t Percent_LowQual \t Hets \t Percent_Hets \t Non-excluded_PASS \t Non-excluded_LowQual \t" + 
		"Non-excluded_percent_LowQual \t Non-excluded_Hets\t Non-excluded_percent_Hets \n")

	# Open bcf file
	for bcf in args.bcf:
		
		# Convert bcf to vcf and make temp vcf file in script directory
		os.system("bcftools view " + bcf + " | bcftools view > " + pwd + "/" + os.path.basename(bcf) + ".vcf")

		# initiate counter variables to zero
		pass_snv_count = 0
		lowqual_snv_count = 0
		het_snv_count = 0
		lowqual_percent = 0
		het_percent = 0

		# initalise percent variables to 0
		non_excluded_pass_snv_count = 0
		non_excluded_lowqual_snv_count = 0
		non_excluded_het_snv_count = 0
		non_excluded_lowqual_percent = 0
		non_excluded_het_percent = 0

		# Open created vcf file
		bcf_file = open(pwd + "/" + os.path.basename(bcf) + ".vcf", 'r')

		# Extract PASS/LowQual SNV calls & ratio
		for line in bcf_file:
			
			# Ignore header lines
			if not line.startswith('#'):
				
				# Ignore indels
				if "INDEL" not in line:
					x = line.rstrip().split()
					
					# Ignore reference alleles
					if x[4]!=".":
						
						# Ingore concatenated sequences (e.g. plasmids)
						if int(x[1]) <= args.chromosome_size:
							
							# Count PASS and LowQual SNVs
							if (x[6]=="PASS"):
								pass_snv_count = pass_snv_count + 1
								
								if int(x[1]) not in positions_to_exclude:
									non_excluded_pass_snv_count = non_excluded_pass_snv_count + 1
							
							if (x[6]=="LowQual"):
								
								# Save AD values for het SNV counts
								info = x[7].split(";")
								AD = info[3].split(",")
								AD1 = re.sub('[AD=]', '', AD[0])
								AD2 = AD[1]
								AD_max = 0

								# Save DP4 values for het SNV counts
								DP4 = re.search("DP4=(\d+),(\d+),(\d+),(\d+)", x[7])
								DP4_total_reads = int(DP4.group(1)) + int(DP4.group(2)) + int(DP4.group(3)) + int(DP4.group(4))
								
								# Save AD max for het SNV counts
								if (int(AD1) == int(AD2)):
									AD_max = AD1
								elif (int(AD1) > int(AD2)):
									AD_max = AD1
								else:
									AD_max = AD2
								
								# Get SNV AD_max/DP4 ratio
								ratio = float(AD_max)/float(DP4_total_reads)
								
								# Increment counters for LowQual and Het SNVs
								lowqual_snv_count = lowqual_snv_count + 1
								if int(x[1]) not in positions_to_exclude:
									non_excluded_lowqual_snv_count = non_excluded_lowqual_snv_count + 1
								if (ratio < 0.9):
									het_snv_count = het_snv_count + 1
									if int(x[1]) not in positions_to_exclude:
										non_excluded_het_snv_count = non_excluded_het_snv_count + 1
		
		# Get percentage of low quality & het SNVs
		if pass_snv_count != 0: 
			lowqual_percent = (float(lowqual_snv_count)/float(pass_snv_count))*100
			het_percent = (float(het_snv_count)/float(pass_snv_count))*100
		else: 
			lowqual_percent = 0
			het_percent = 0
		if non_excluded_pass_snv_count != 0: 
			non_excluded_lowqual_percent = (float(non_excluded_lowqual_snv_count)/float(non_excluded_pass_snv_count))*100
			non_excluded_het_percent = (float(non_excluded_het_snv_count)/float(non_excluded_pass_snv_count))*100
		else: 
			non_excluded_lowqual_percent = 0
			non_excluded_het_percent = 0

		# Close file for buffering
		bcf_file.close()

		# delete temp vcf file if sequence data OK
		if args.save_high_lowqual==False or (args.save_high_lowqual==True and non_excluded_lowqual_percent < 10):
			os.system("rm " + pwd + "/" + os.path.basename(bcf) + ".vcf")

		# Output summary data
		output_snv_summary.write(os.path.basename(bcf) + '\t' + 
			str(pass_snv_count) + '\t' + str(lowqual_snv_count) + '\t' + str(lowqual_percent) + '\t' +  
			str(het_snv_count) + "\t" + str(het_percent) + "\t" + 
			str(non_excluded_pass_snv_count) + '\t' + str(non_excluded_lowqual_snv_count) + '\t' + str(non_excluded_lowqual_percent) + '\t' +
			str(non_excluded_het_snv_count) + '\t' + str(non_excluded_het_percent) + 
			'\n')

	# Close output file for buffering
	output_snv_summary.close()

# call main function
if __name__ == '__main__':
	main()
