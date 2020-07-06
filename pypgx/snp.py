import os
import copy

from typing import List
from .common import VCFFile

from .peek import vcf2samples
from .liftover import SNP, _read_star_table, _read_snp_table, get_codes_key, get_codes_value, Star

def snp(tg: str, vcf: str, pair: List[str]) -> str:
    """
    View variant data for sample/star allele pairs.

    Returns:
        str: SDF file.

    Args:
        tg (str): Target gene.
        vcf (str): VCF file.
        pair (list[str]): sample/star allele pair.
    """

    finalized_vcf = VCFFile(vcf)
    finalized_vcf.read()

    samples = vcf2samples(finalized_vcf, False)

    finalized_vcf.close()

    star_table = _read_star_table(f"{os.path.dirname(__file__)}/resources/sg/star_table.txt")
    snp_table = _read_snp_table(f"{os.path.dirname(__file__)}/resources/sg/snp_table.txt")

    snp_db = []
    for k, v in snp_table[tg].items():
        snp = SNP()
        snp.n = k
        snp.id = v["rs_id"]
        snp.pos = v[f"hg19_pos"]
        snp.hg = v[f"hg19_allele"]
        snp.var = v["var_allele"]
        snp.wt = v["wt_allele"]
        snp.fe = get_codes_key(v["functional_effect"])
        snp.so = get_codes_key(v["sequence_ontology"])
        snp.vi = get_codes_key(v["variant_impact"])
        snp.rv = get_codes_key(v[f"hg19_revertant"])
        snp.data = v
        snp_db.append(snp)

    # Build the star database for the target gene.
    star_db = {}
    for k, v in star_table[tg].items():
        if not v[f"hg19_has"]:
            continue
        star = Star()
        star.name = k
        star.score = float(v["score"])
        star.core = [] if v["hg19_core"] in ["ref", "."] else copy.deepcopy([x for x in snp_db if f"{x.pos}:{x.wt}>{x.var}" in v[f"hg19_core"].split(",")])
        star.tag = [] if v["hg19_tag"] == "." else copy.deepcopy([x for x in snp_db if f"{x.pos}:{x.wt}>{x.var}" in v[f"hg19_tag"].split(",")])
        star.sv = "" if v["sv"] == "." else v["sv"]
        star_db[k] = star

    temp = []

    for x in pair:
        table = []
        sample = samples[x.split("/")[0]]
        star = star_db[x.split("/")[1]]
        temp.append(["<sample={},star={}>".format(sample.name, star.name)])
        header = [f"hg19_pos", "wt_allele", "var_allele", f"hg19_allele", "type", "so", "impact", "effect", "hap1_allele", "hap2_allele", "gt", "hap1_ad", "hap2_ad", "hap1_af", "hap2_af"]
        temp.append(header)

        def get_fields(snp, type):
            hap1_allele = snp.var if snp in sample.hap[0].obs else snp.wt
            hap2_allele = snp.var if snp in sample.hap[1].obs else snp.wt
            hap1_gt = "0" if hap1_allele == snp.wt else "1" if hap1_allele == snp.var else "2"
            hap2_gt = "0" if hap2_allele == snp.wt else "1" if hap2_allele == snp.var else "2"
            hap1_ad = str([x for x in sample.hap[0].obs if x.pos == snp.pos][0].ad) if snp.pos in [x.pos for x in sample.hap[0].obs] else "0"
            hap2_ad = str([x for x in sample.hap[1].obs if x.pos == snp.pos][0].ad) if snp.pos in [x.pos for x in sample.hap[1].obs] else "0"
            hap1_af = "{:.2f}".format([x for x in sample.hap[0].obs if x.pos == snp.pos][0].af) if snp.pos in [x.pos for x in sample.hap[0].obs] else "0"
            hap2_af = "{:.2f}".format([x for x in sample.hap[1].obs if x.pos == snp.pos][0].af) if snp.pos in [x.pos for x in sample.hap[1].obs] else "0"
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