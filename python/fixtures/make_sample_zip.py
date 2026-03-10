#!/usr/bin/env python3
"""
Generates python/fixtures/sample_13f.zip – a small but realistic SEC DERA-format
13F dataset zip that can be used for local development and testing without
downloading the multi-GB official quarterly archive.

Column names and formats follow the official SEC DERA specification:
  https://www.sec.gov/dera/data/form-13f-data-sets

Contents
--------
  SUBMISSION.tsv   filing metadata (columns: ACCESSION_NUMBER, FILING_DATE,
                   SUBMISSIONTYPE, CIK, PERIODOFREPORT)
  INFOTABLE.tsv    holdings (columns: ACCESSION_NUMBER, INFOTABLE_SK,
                   NAMEOFISSUER, TITLEOFCLASS, CUSIP, VALUE, SSHPRNAMT,
                   SSHPRNAMTTYPE)

Notes
-----
  * Dates are in DD-MON-YYYY format (e.g. 15-JAN-2026) as per the spec.
  * VALUE is in dollars (not thousands). Starting January 3, 2023 the SEC
    reports market value rounded to the nearest dollar.
  * SUBMISSION has no COMPANYNAME column; company name lives in COVERPAGE.

Scenarios covered
-----------------
  * 8 filers of varying size ($400 M – $80 B) so the top-N ranking works
  * Each filer has an early-January filing (earliest) and a late-February
    filing (latest), enabling net-change / buy / sell computation
  * Several securities shared across filers (aggregation)
  * One ETF holding per filer (to verify ETF exclusion logic)
  * Each filer has at least one closed position (in earliest, gone in latest)
    and at least one new position (in latest, not in earliest)
  * Dollar values ensure several securities exceed the $1 M net-change threshold
  * The SUBMISSION.tsv is written with a UTF-8 BOM to validate BOM-stripping
  * 13F-HR/A amendment rows are included to verify they are filtered out

Usage
-----
  python python/fixtures/make_sample_zip.py
  # produces / overwrites python/fixtures/sample_13f.zip
"""

import io
import os
import zipfile
import pathlib

# ---------------------------------------------------------------------------
# Security universe (CUSIP, name, title)
# ---------------------------------------------------------------------------
SECURITIES = {
    "037833100": ("APPLE INC",                   "COM"),
    "594918104": ("MICROSOFT CORP",               "COM"),
    "67066G104": ("NVIDIA CORP",                  "COM"),
    "02079K305": ("ALPHABET INC CL A",            "COM"),
    "023135106": ("AMAZON COM INC",               "COM"),
    "30303M102": ("META PLATFORMS INC",           "COM"),
    "88160R101": ("TESLA INC",                    "COM"),
    "084670702": ("BERKSHIRE HATHAWAY INC CL B",  "COM"),
    "46625H100": ("JPMORGAN CHASE & CO",           "COM"),
    "92826C839": ("VISA INC CL A",                "COM"),
    "91324P102": ("UNITEDHEALTH GROUP INC",        "COM"),
    "532457108": ("ELI LILLY & CO",               "COM"),
    "30231G102": ("EXXON MOBIL CORP",             "COM"),
    "023608102": ("AMAZON COM INC WARRANTS",      "WT"),   # small obscure position
    "78462F103": ("SPDR S&P 500 ETF TRUST ETF",   "SHS"),  # ETF – should be excluded
    "46090E103": ("INVESCO QQQ TRUST ETF",        "SHS"),  # ETF – should be excluded
}

# ---------------------------------------------------------------------------
# Filer definitions
# ---------------------------------------------------------------------------
# Each filer has:
#   cik, name,
#   early_holdings: {cusip: (value_dollars, shares)}   Jan-15 filing
#   late_holdings:  {cusip: (value_dollars, shares)}   Feb-28 filing
#
# Values are in dollars (as per the SEC spec for filings since Jan 2023).
#
# Design rules applied per filer:
#   - one ETF in each filing (for exclusion test)
#   - one position present only in early (closed)
#   - one position present only in late (new)
#   - changes large enough so aggregate net change for AAPL/MSFT/NVDA
#     exceed the $1 M threshold

FILERS = [
    {
        "cik": "0000102909",
        "name": "VANGUARD GROUP INC",
        # ~$80 B filer
        "early": {
            "037833100": (15_000_000, 80_000_000),   # AAPL
            "594918104": (12_000_000, 35_000_000),   # MSFT
            "67066G104": (11_000_000, 12_000_000),   # NVDA
            "02079K305":  (9_000_000, 32_000_000),   # GOOGL
            "023135106":  (8_500_000, 45_000_000),   # AMZN
            "78462F103":    (500_000,    900_000),   # SPY ETF
            "084670702":  (4_000_000, 12_000_000),   # BRK.B (closed)
        },
        "late": {
            "037833100": (16_500_000, 82_000_000),   # AAPL ↑
            "594918104": (13_000_000, 35_000_000),   # MSFT ↑
            "67066G104": (12_500_000, 12_500_000),   # NVDA ↑
            "02079K305":  (8_500_000, 30_000_000),   # GOOGL ↓
            "023135106":  (9_000_000, 46_000_000),   # AMZN ↑
            "78462F103":    (600_000,  1_000_000),   # SPY ETF
            "30303M102":  (5_000_000, 10_000_000),   # META (new)
        },
    },
    {
        "cik": "0000093751",
        "name": "BLACKROCK INC",
        # ~$60 B
        "early": {
            "037833100": (11_000_000, 60_000_000),
            "594918104":  (9_000_000, 26_000_000),
            "67066G104":  (8_000_000,  8_500_000),
            "30303M102":  (4_000_000,  8_000_000),
            "88160R101":  (2_500_000,  9_000_000),
            "46090E103":    (400_000,    700_000),   # QQQ ETF
            "92826C839":  (3_000_000,  9_500_000),  # V (closed)
        },
        "late": {
            "037833100": (12_500_000, 62_000_000),
            "594918104": (10_000_000, 27_000_000),
            "67066G104":  (9_500_000,  9_000_000),
            "30303M102":  (5_000_000,  9_000_000),
            "88160R101":  (2_000_000,  8_000_000),   # TSLA ↓
            "46090E103":    (450_000,    750_000),   # QQQ ETF
            "023135106":  (4_500_000, 24_000_000),  # AMZN (new)
        },
    },
    {
        "cik": "0000891482",
        "name": "STATE STREET CORP",
        # ~$45 B
        "early": {
            "037833100":  (9_000_000, 48_000_000),
            "594918104":  (7_500_000, 22_000_000),
            "67066G104":  (6_000_000,  6_400_000),
            "02079K305":  (5_000_000, 18_000_000),
            "91324P102":  (2_800_000,  5_000_000),
            "78462F103":    (300_000,    550_000),   # SPY ETF
            "532457108":  (1_500_000,  2_000_000),   # LLY (closed)
        },
        "late": {
            "037833100": (10_000_000, 50_000_000),
            "594918104":  (8_000_000, 22_500_000),
            "67066G104":  (7_500_000,  7_000_000),
            "02079K305":  (4_500_000, 16_000_000),
            "91324P102":  (3_200_000,  5_500_000),
            "78462F103":    (350_000,    600_000),   # SPY ETF
            "30231G102":  (2_000_000,  7_500_000),  # XOM (new)
        },
    },
    {
        "cik": "0000202798",
        "name": "FIDELITY INVESTMENTS",
        # ~$30 B
        "early": {
            "037833100":  (7_000_000, 37_000_000),
            "67066G104":  (5_500_000,  5_800_000),
            "30303M102":  (3_500_000,  7_000_000),
            "023135106":  (4_000_000, 21_000_000),
            "46090E103":    (250_000,    430_000),   # QQQ ETF
            "46625H100":  (1_200_000,  6_000_000),   # JPM (closed)
        },
        "late": {
            "037833100":  (8_000_000, 38_500_000),
            "67066G104":  (7_000_000,  6_500_000),
            "30303M102":  (4_500_000,  8_500_000),
            "023135106":  (4_800_000, 23_000_000),
            "46090E103":    (280_000,    470_000),   # QQQ ETF
            "594918104":  (3_000_000,  8_500_000),  # MSFT (new)
        },
    },
    {
        "cik": "0000315066",
        "name": "T ROWE PRICE GROUP INC",
        # ~$20 B
        "early": {
            "037833100":  (4_500_000, 24_000_000),
            "594918104":  (3_800_000, 11_000_000),
            "02079K305":  (3_000_000, 10_800_000),
            "88160R101":  (1_800_000,  6_500_000),
            "78462F103":    (150_000,    270_000),   # SPY ETF
            "30231G102":    (800_000,  3_000_000),   # XOM (closed)
        },
        "late": {
            "037833100":  (5_500_000, 25_000_000),
            "594918104":  (4_200_000, 11_500_000),
            "02079K305":  (2_800_000, 10_000_000),
            "88160R101":  (1_500_000,  5_500_000),
            "78462F103":    (200_000,    340_000),   # SPY ETF
            "67066G104":  (2_500_000,  2_400_000),  # NVDA (new)
        },
    },
    {
        "cik": "0000093506",
        "name": "CAPITAL RESEARCH AND MANAGEMENT CO",
        # ~$15 B
        "early": {
            "037833100":  (3_200_000, 17_000_000),
            "023135106":  (2_800_000, 15_000_000),
            "30303M102":  (2_000_000,  4_000_000),
            "91324P102":  (1_500_000,  2_700_000),
            "46090E103":    (100_000,    175_000),   # QQQ ETF
            "88160R101":  (1_000_000,  3_600_000),   # TSLA (closed)
        },
        "late": {
            "037833100":  (3_800_000, 18_000_000),
            "023135106":  (3_200_000, 16_500_000),
            "30303M102":  (2_500_000,  4_800_000),
            "91324P102":  (1_800_000,  3_100_000),
            "46090E103":    (110_000,    185_000),   # QQQ ETF
            "532457108":    (900_000,  1_200_000),  # LLY (new)
        },
    },
    {
        "cik": "0000036270",
        "name": "JPMORGAN CHASE BANK NA",
        # ~$10 B
        "early": {
            "037833100":  (2_000_000, 10_700_000),
            "594918104":  (1_800_000,  5_200_000),
            "67066G104":  (1_500_000,  1_600_000),
            "78462F103":     (80_000,    145_000),  # SPY ETF
            "023608102":     (50_000,    200_000),  # AMZN WT (small, closed)
        },
        "late": {
            "037833100":  (2_300_000, 11_000_000),
            "594918104":  (2_100_000,  5_700_000),
            "67066G104":  (1_900_000,  1_800_000),
            "78462F103":     (90_000,    160_000),  # SPY ETF
            "30231G102":    (500_000,  1_900_000),  # XOM (new)
        },
    },
    {
        "cik": "0000913144",
        "name": "CITADEL ADVISORS LLC",
        # ~$5 B
        "early": {
            "037833100":    (900_000,  4_800_000),
            "67066G104":    (800_000,    850_000),
            "30303M102":    (600_000,  1_200_000),
            "46090E103":     (40_000,     70_000),  # QQQ ETF
            "88160R101":    (500_000,  1_800_000),  # TSLA (closed)
        },
        "late": {
            "037833100":  (1_100_000,  5_200_000),
            "67066G104":    (950_000,    900_000),
            "30303M102":    (700_000,  1_350_000),
            "46090E103":     (45_000,     75_000),  # QQQ ETF
            "92826C839":    (400_000,  1_300_000),  # VISA (new)
        },
    },
]

# Filing dates in DD-MON-YYYY format (as required by the SEC DERA spec)
EARLY_DATE     = "15-JAN-2026"
LATE_DATE      = "28-FEB-2026"
PERIOD_OF_RPT  = "31-DEC-2025"   # Q4 2025 holdings period


def _submission_rows():
    """Generate tab-separated rows for SUBMISSION.tsv.

    Columns match the SEC DERA spec exactly:
      ACCESSION_NUMBER, FILING_DATE, SUBMISSIONTYPE, CIK, PERIODOFREPORT
    Note: COMPANYNAME is NOT in SUBMISSION; it lives in COVERPAGE.
    """
    header = "ACCESSION_NUMBER\tFILING_DATE\tSUBMISSIONTYPE\tCIK\tPERIODOFREPORT"
    rows = [header]
    for i, f in enumerate(FILERS):
        early_acc = f"0001{i:06d}-26-000001"
        late_acc  = f"0001{i:06d}-26-000002"
        rows.append(f"{early_acc}\t{EARLY_DATE}\t13F-HR\t{f['cik']}\t{PERIOD_OF_RPT}")
        rows.append(f"{late_acc}\t{LATE_DATE}\t13F-HR\t{f['cik']}\t{PERIOD_OF_RPT}")
        # Amendment row – code must filter these out (only 13F-HR, not 13F-HR/A)
        rows.append(f"0001{i:06d}-26-000003\t{LATE_DATE}\t13F-HR/A\t{f['cik']}\t{PERIOD_OF_RPT}")
    return "\n".join(rows)


def _infotable_rows():
    """Generate tab-separated rows for INFOTABLE.tsv.

    Columns match the SEC DERA spec:
      ACCESSION_NUMBER, INFOTABLE_SK, NAMEOFISSUER, TITLEOFCLASS, CUSIP,
      VALUE, SSHPRNAMT, SSHPRNAMTTYPE
    VALUE is in dollars (not thousands) as per the spec for post-2023 filings.
    """
    header = (
        "ACCESSION_NUMBER\tINFOTABLE_SK\tNAMEOFISSUER\tTITLEOFCLASS"
        "\tCUSIP\tVALUE\tSSHPRNAMT\tSSHPRNAMTTYPE"
    )
    rows = [header]
    for i, f in enumerate(FILERS):
        early_acc = f"0001{i:06d}-26-000001"
        late_acc  = f"0001{i:06d}-26-000002"
        sk = 1
        for acc, holdings in ((early_acc, f["early"]), (late_acc, f["late"])):
            for cusip, (value, shares) in holdings.items():
                name, title = SECURITIES[cusip]
                rows.append(
                    f"{acc}\t{sk}\t{name}\t{title}\t{cusip}\t{value}\t{shares}\tSH"
                )
                sk += 1
    return "\n".join(rows)


def build_combined_quarter_zip(dest_path: pathlib.Path):
    """Build the combined fixture zip (two filing dates per filer, single-zip mode)."""
    submission = _submission_rows()
    infotable  = _infotable_rows()

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Write SUBMISSION with UTF-8 BOM to exercise BOM-stripping logic
        zf.writestr("SUBMISSION.tsv", "\ufeff" + submission)
        zf.writestr("INFOTABLE.tsv",  infotable)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(buf.getvalue())
    print(f"Written {dest_path}  ({dest_path.stat().st_size:,} bytes)")
    print(f"  SUBMISSION rows : {submission.count(chr(10))}")
    print(f"  INFOTABLE rows  : {infotable.count(chr(10))}")


def _single_quarter_rows(filing_date: str, holdings_key: str):
    """
    Generate SUBMISSION and INFOTABLE TSV text for a single-quarter fixture.

    Parameters
    ----------
    filing_date  : str   e.g. "15-JAN-2026"
    holdings_key : str   "early" or "late" – which holdings dict to use
    """
    sub_header = "ACCESSION_NUMBER\tFILING_DATE\tSUBMISSIONTYPE\tCIK\tPERIODOFREPORT"
    info_header = (
        "ACCESSION_NUMBER\tINFOTABLE_SK\tNAMEOFISSUER\tTITLEOFCLASS"
        "\tCUSIP\tVALUE\tSSHPRNAMT\tSSHPRNAMTTYPE"
    )
    sub_rows  = [sub_header]
    info_rows = [info_header]
    for i, f in enumerate(FILERS):
        acc = f"0001{i:06d}-26-{1 if holdings_key == 'early' else 2:06d}"
        sub_rows.append(
            f"{acc}\t{filing_date}\t13F-HR\t{f['cik']}\t{PERIOD_OF_RPT}"
        )
        sk = 1
        for cusip, (value, shares) in f[holdings_key].items():
            name, title = SECURITIES[cusip]
            info_rows.append(
                f"{acc}\t{sk}\t{name}\t{title}\t{cusip}\t{value}\t{shares}\tSH"
            )
            sk += 1
    return "\n".join(sub_rows), "\n".join(info_rows)


def build_single_quarter_zip(dest_path: pathlib.Path, filing_date: str, holdings_key: str):
    """Build a single-quarter fixture zip (one filing per filer) for two-zip mode."""
    submission, infotable = _single_quarter_rows(filing_date, holdings_key)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("SUBMISSION.tsv", "\ufeff" + submission)
        zf.writestr("INFOTABLE.tsv",  infotable)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(buf.getvalue())
    print(f"Written {dest_path}  ({dest_path.stat().st_size:,} bytes)")
    print(f"  SUBMISSION rows : {submission.count(chr(10))}")
    print(f"  INFOTABLE rows  : {infotable.count(chr(10))}")


if __name__ == "__main__":
    script_dir = pathlib.Path(__file__).parent

    # Combined fixture (two filing dates per filer) – for single-zip mode
    build_combined_quarter_zip(script_dir / "sample_13f.zip")

    # Two single-quarter fixtures – for two-zip mode (--prior-zip / --zip)
    build_single_quarter_zip(
        script_dir / "sample_13f_prior.zip",
        EARLY_DATE,
        "early",
    )
    build_single_quarter_zip(
        script_dir / "sample_13f_current.zip",
        LATE_DATE,
        "late",
    )
