# RIP Test Data: this data directory will contain the documents that were used to test the RIP

the directory will contain samples that are 1) compliant and 2) non-compliant examples of real-cases of protocols.

## protocol examples

These are real, publicly available clinical trial protocols you can paste into RIP to test the audit pipeline. To limit the current scope of the project, we opted to filter studies on the following criterias:
- Condition/Disease: Ontology
- Study Phase: Early Phase 1
- Funder Type: NIH

To download the pdf files, run the following script: 

```
python data/documents/compliant/download.py --limit 5
```
modify limit to up to 29 potential documents. 

This will download the protocols from previous cases. Negative samples will be designed from these protocols by redacting crucial information in the documents and adding classifying across the following defined regulations:

P11) electronic signature...

##### NEED HELP WITH THIS PART
#### REMAINING TO DO IS TO 
- CREATE THE "FAKE" VERSIONS
- HAVE THE DATABASE OF ALL THE REGULATIONS
- HAVE A WAY TO EVALUATE AGAINST THOSE BASELINES AND PRODUCE REPORTS
- DOCUMENT HOW OUR MODEL PERFORMS ON THESE 29 SAMPLES