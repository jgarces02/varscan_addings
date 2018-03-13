#!/bin/python

#######################################################################################################################
## varscan2vcf.py -> convert varscan output to VCF format (13/08/2018).
#######################################################################################################################
## kindly taken and fixed from https://goo.gl/2Af9RK

import argparse, math, re

parser = argparse.ArgumentParser(
    description="Converts VarScan2 somatic vcf to native format and vice-versa.\nInput is automatically detected")

parser.add_argument('input', help='Input file generated by VarScan2 somatic')
# parser.add_argument('output', help='output file name')

args = parser.parse_args()

# Function to print header line
def printNativeHeader():
    """
    :rtype : Null
    """
    print(
        "chrom\tposition\tref\tvar\tnormal_reads1\tnormal_reads2\tnormal_var_freq\tnormal_gt\ttumor_reads1\ttumor_reads\ttumor_var_freq\ttumor_gt\tsomatic_status\tvariant_p_value\tsomatic_p_value\ttumor_reads1_plus\ttumor_reads1_minus\ttumor_reads2_plus\ttumor_reads2_minus\tnormal_reads1_plus\tnormal_reads1_minus\tnormal_reads2_plus\tnormal_reads2_minus")


# Function to print vcf header
def printVcfHeader():
    print("##fileformat=VCFv4.1\n"
          "##source=VarScan2\n"
          "##INFO=<ID=AF,Number=A,Type=Float,Description=\"Allele Frequency\">\n"
          "##INFO=<ID=DP,Number=1,Type=Integer,Description=\"Total depth of quality bases\">\n"
          "##INFO=<ID=SOMATIC,Number=0,Type=Flag,Description=\"Indicates if record is a somatic mutation\">\n"
          "##INFO=<ID=SS,Number=1,Type=String,Description=\"Somatic status of variant (0=Reference,1=Germline,2=Somatic,3=LOH, or 5=Unknown)\">\n"
          "##INFO=<ID=SSC,Number=1,Type=String,Description=\"Somatic score in Phred scale (0-255) derived from somatic p-value\">\n"
          "##INFO=<ID=GPV,Number=1,Type=Float,Description=\"Fisher's Exact Test P-value of tumor+normal versus no variant for Germline calls\">\n"
          "##INFO=<ID=SPV,Number=1,Type=Float,Description=\"Fisher's Exact Test P-value of tumor versus normal for Somatic/LOH calls\">\n"
          "##FILTER=<ID=str10,Description=\"Less than 10% or more than 90% of variant supporting reads on one strand\">\n"
          "##FILTER=<ID=indelError,Description=\"Likely artifact due to indel reads at this position\">\n"
          "##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">\n"
          "##FORMAT=<ID=GQ,Number=1,Type=Integer,Description=\"Genotype Quality\">\n"
          "##FORMAT=<ID=DP,Number=1,Type=Integer,Description=\"Read Depth\">\n"
          "##FORMAT=<ID=RD,Number=1,Type=Integer,Description=\"Depth of reference-supporting bases (reads1)\">\n"
          "##FORMAT=<ID=AD,Number=1,Type=Integer,Description=\"Depth of variant-supporting bases (reads2)\">\n"
          "##FORMAT=<ID=FREQ,Number=1,Type=String,Description=\"Variant allele frequency\">\n"
          "##FORMAT=<ID=DP4,Number=1,Type=String,Description=\"Strand read counts: ref/fwd, ref/rev, var/fwd, var/rev\">\n"
          "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO")

# Function to convert vcf record to NativeFormat record
def makeNativeRec(vcfIp):
    """
    :rtype : Null
    :type nativeIp: basestring
    """
    nativeLine = vcfIp.split("\t")

    somaticDict = {'0': 'Reference', '1': 'Germline', '2': 'Somatic', '3': 'LOH', '5': 'Unknown'}

    chrom = nativeLine[0]
    position = nativeLine[1]
    ref = nativeLine[3]
    var = nativeLine[4]

    normalInfo = nativeLine[9]
    tumorInfo = nativeLine[10]

    normal_reads1 = normalInfo.split(":")[3]
    normal_reads2 = normalInfo.split(":")[4]
    normal_var_freq = normalInfo.split(":")[5]
    normal_gt = normalInfo.split(":")[0]
    normal_dp4 = normalInfo.split(":")[6]
    normal_reads1_plus = normal_dp4.split(",")[0]
    normal_reads1_minus = normal_dp4.split(",")[1]
    normal_reads2_plus = normal_dp4.split(",")[2]
    normal_reads2_minus = normal_dp4.split(",")[3]

    tumor_reads1 = tumorInfo.split(":")[3]
    tumor_reads2 = tumorInfo.split(":")[4]
    tumor_var_freq = tumorInfo.split(":")[5]
    tumor_gt = tumorInfo.split(":")[0]
    tumor_dp4 = tumorInfo.split(":")[6]
    tumor_reads1_plus = tumor_dp4.split(",")[0]
    tumor_reads1_minus = tumor_dp4.split(",")[1]
    tumor_reads2_plus = tumor_dp4.split(",")[2]
    tumor_reads2_minus = tumor_dp4.split(",")[3]

    info = nativeLine[7]
    infoDict = {}
    infoSpl = info.split(";")

    for rec in infoSpl:
        recSpl = rec.split("=")
        if not len(recSpl) == 1:
            infoDict[recSpl[0]] = recSpl[1]

    somatic_status = somaticDict[infoDict['SS']]
    variant_p_value = infoDict['GPV']
    somatic_p_value = infoDict['SPV']

    print("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t" %
          (chrom, position, ref, var, normal_reads1, normal_reads2, normal_var_freq, normal_gt, tumor_reads1,
           tumor_reads2, tumor_var_freq, tumor_gt, somatic_status, variant_p_value, somatic_p_value, tumor_reads1_plus,
           tumor_reads1_minus, tumor_reads2_plus, tumor_reads2_minus, normal_reads1_plus, normal_reads1_minus,
           normal_reads2_plus, normal_reads2_minus))

# Function to convert Native to VCF record
def makeVcfRecord(nativeIp):
    """
    :rtype : Null
    """
    somaticDict = {'Reference': '0', 'Germline': '1', 'Somatic': '2', 'LOH': '3', 'Unknown': '5'}
    nIp = nativeIp.split("\t")
    chrom = nIp[0]
    pos = nIp[1]
    id = '.'
    ref = nIp[2]
    qual = '.'
    filter = 'PASS'
    dp = int(nIp[4]) + int(nIp[5]) + int(nIp[8]) + int(nIp[9])
    ss = somaticDict[nIp[12]]

    try:
        ssc = -10 * math.log10(float(nIp[14]))
    except Exception:
        ssc = 0

    gpv = nIp[13]
    spv = nIp[14]

    tumorAF = float(nIp[10].replace('%', '').replace(",", ".")) / 100

    if ss == '2':
        info = "AF=" + str(tumorAF) + ";DP=" + str(dp) + ";SOMATIC;" + "SS=" + ss + ";" + "SSC=" + str(
            int(ssc)) + ";" + "GPV=" + gpv + ";" + "SPV=" + spv
    else:
        info = "AF=" + str(tumorAF) + ";DP=" + str(dp) + ";SS=" + ss + ";" + "SSC=" + str(
            int(ssc)) + ";" + "GPV=" + gpv + ";" + "SPV=" + spv

    vcf_format = "GT:GQ:DP:RD:AD:FREQ:DP4"

    normal_var_freq = float(re.sub('%', '', nIp[6]).replace(",", "."))
    if normal_var_freq > 10 and normal_var_freq < 75:
        gt = '0/1'
    elif normal_var_freq > 75:
        gt = '1/1'
    else:
        gt = "0/0"

    tumor_var_freq = float(re.sub('%', '', nIp[10]).replace(",", "."))
    if tumor_var_freq > 10 and tumor_var_freq < 75:
        gt2 = '0/1'
    elif tumor_var_freq > 75:
        gt2 = '1/1'
    else:
        gt2 = "0/0"

    gq = '.'
    dp2 = int(nIp[4]) + int(nIp[5])
    rd = nIp[4]
    ad = nIp[5]
    freq = nIp[6]
    dp4 = nIp[19] + ',' + nIp[20] + ',' + nIp[21] + ',' + nIp[22]
    normal_format = gt + ':' + gq + ":" + str(dp2) + ':' + rd + ':' + ad + ':' + freq + ':' + dp4

    dp3 = int(nIp[8]) + int(nIp[9])
    rd2 = nIp[8]
    ad2 = nIp[9]
    freq2 = nIp[10]
    dp42 = nIp[15] + ',' + nIp[16] + ',' + nIp[17] + ',' + nIp[19]
    tumor_format = gt2 + ':' + gq + ":" + str(dp3) + ':' + rd2 + ':' + ad2 + ':' + freq2 + ':' + dp42

    alt = nIp[3]

    #
    # VarScan has tricky output format for indels (why would they do that in the first place?)
    #

    if alt[0] == '-':
        alt = alt.replace('-', '')
    elif alt[0] == '+':
        alt = ref + alt.replace('+', '')

    print("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (chrom, pos, id, ref, alt, qual, filter, info))

####
def NativeToVcf(inputFile):
    printVcfHeader()
    vs = open(inputFile, 'r')
    for line in vs.readlines():
        if not line.startswith("chrom"):
            makeVcfRecord(line.strip())
    vs.close()


###
def vcfToNative(inputFile):
    vs = open(inputFile, 'r')
    printNativeHeader()
    for line in vs.readlines():
        if not line.startswith("#"):
            makeNativeRec(line.strip())
    vs.close()

####
vsIp = open(args.input, 'r')

firstLine = vsIp.readline().strip()

if firstLine.startswith("##fileformat="):
    vcfToNative(args.input)
else:
    NativeToVcf(args.input)
    vsIp.close()
