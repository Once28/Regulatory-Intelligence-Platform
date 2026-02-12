# RIP Test Data: this data directory will contain the documents that were used to test the RIP

the directory will contain samples that are 1) compliant and 2) non-compliant examples of real-cases of protocols.

## protocol examples

These are real, publicly available clinical trial protocols you can paste into RIP to test the audit pipeline. To limit the current scope of the project, we opted to filter studies on the following criterias:
- Condition/Disease: Oncology
- Study Phase: Early Phase 1
- Funder Type: NIH

To download the pdf files, run the following script: 

```
python data/documents/compliant/download.py --limit 5
```
modify limit to up to 29 potential documents. 

This will download the protocols from previous cases. 

### Generating Non-Compliant (Negative) Examples

To create fake/negative examples from the compliant protocols by redacting crucial information, run:

```
python data/documents/non_compliant/generate_negative_examples.py --limit 5
```

This script will:
- Read PDFs from `compliant/protocols/`
- Redact crucial information such as:
  - Protocol IDs (NCT numbers)
  - Dates (approval dates, study dates)
  - Signatures and investigator names
  - Version numbers and amendments
  - Contact information (emails, phone numbers)
  - IRB identifiers
- Save redacted PDFs to `non_compliant/protocols/`

You can customize which types of information to redact using the `--types` flag:
```
python data/documents/non_compliant/generate_negative_examples.py --types DATE SIGNATURE PROTOCOL_ID
```

#### REMAINING TO DO IS TO 
- HAVE THE DATABASE OF ALL THE REGULATIONS ()
- HAVE A WAY TO EVALUATE AGAINST THOSE BASELINES AND PRODUCE REPORTS
- DOCUMENT HOW OUR MODEL PERFORMS ON THESE 29 SAMPLES