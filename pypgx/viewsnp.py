import os
import copy
from typing import List

from .common import get_stardb, VCFFile
from .sglib import vcf2biosamples

def viewsnp(
        vcf_file: str,
        query: List[str],
        **kwargs
    ) -> str:
    """View SNP data for pairs of sample/star allele.

    Returns:
        Summary of SNP data for given pairs of samples and star alleles.

    Args:
        vcf_file: Stargazer VCF file ('finalized.vcf').
        query: List of pairs of sample and star allele separated by '/'
            (e.g. 'SAMPLE1/*4').
    """
    finalized_vcf = VCFFile(vcf_file)
    finalized_vcf.read()

    target_gene = finalized_vcf.search_meta("target_gene")
    genome_build = finalized_vcf.search_meta("genome_build")

    biosamples = vcf2biosamples(finalized_vcf, False)
    stardb = get_stardb(target_gene, genome_build)
    temp = []

    for x in query:
        table = []
        sample_id = x.split("/")[0]
        biosample = [x for x in biosamples if x.name == sample_id][0]
        star = stardb[x.split("/")[1]]
        temp.append(["<sample={},star={}>".format(biosample.name, star.name)])

        header = [
            f"{genome_build}_pos",
            "wt_allele", "var_allele",
            f"{genome_build}_allele",
            "type",
            "so",
            "impact",
            "effect",
            "hap1_allele",
            "hap2_allele",
            "gt",
            "hap1_ad",
            "hap2_ad",
            "hap1_af",
            "hap2_af",
        ]

        temp.append(header)

        def get_fields(snp, type):
            hap1_allele = snp.var if snp in biosample.hap[0].obs else snp.wt
            hap2_allele = snp.var if snp in biosample.hap[1].obs else snp.wt
            hap1_gt = "0" if hap1_allele == snp.wt else "1" if hap1_allele == snp.var else "2"
            hap2_gt = "0" if hap2_allele == snp.wt else "1" if hap2_allele == snp.var else "2"
            hap1_ad = str([x for x in biosample.hap[0].obs if x.pos == snp.pos][0].ad) if snp.pos in [x.pos for x in biosample.hap[0].obs] else "0"
            hap2_ad = str([x for x in biosample.hap[1].obs if x.pos == snp.pos][0].ad) if snp.pos in [x.pos for x in biosample.hap[1].obs] else "0"
            hap1_af = "{:.2f}".format([x for x in biosample.hap[0].obs if x.pos == snp.pos][0].af) if snp.pos in [x.pos for x in biosample.hap[0].obs] else "0"
            hap2_af = "{:.2f}".format([x for x in biosample.hap[1].obs if x.pos == snp.pos][0].af) if snp.pos in [x.pos for x in biosample.hap[1].obs] else "0"
            return [snp.pos, snp.wt, snp.var, snp.data[f"hg19_allele"], type, snp.so, snp.vi, snp.fe, hap1_allele, hap2_allele, "{}|{}".format(hap1_gt, hap2_gt), hap1_ad, hap2_ad, hap1_af, hap2_af]

        for snp in star.core:
            table.append(get_fields(snp, "core"))
        for snp in star.tag:
            table.append(get_fields(snp, "tag"))
        for fields in sorted(table, key = lambda x: int(x[0])):
            temp.append(fields)

    result = ""

    for fields in temp:
        result += "\t".join(fields) + "\n"

    return result
