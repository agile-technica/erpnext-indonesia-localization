## Indonesia Taxes and Charges

### ITC Settings:
single doctype to config some feature about Indonesian Tax and Charges APP (frappe app / extension)

### Tax Invoice Number Importer:
single doctype as tools for populate / create Tax Invoice Number document

    example :
    tax invoice number start = 0001100000000
    tax invoice number end = 0001100000009

    create 10 Tax Invoice Number document

### Tax Invoice Number:
doctype to maintain Tax Invoice Number document and information about tax invoice number

### Tax Invoice Exporter
doctype to export elligible Sales Invoice with Efaktur format

    flow :
    1. collect Sales Invoice document on specific posting date and specific company
    2. mapping elligible Sales Invoice with available Tax Invoice Number inside Tax Invoice Exporter child table
    3. when button "Export as CSV" clicked, create new csv file and mapping Sales Invoice data and selected Tax Invoice Number into Efaktur format
    4. Tax Invoice Number will added prefix from "Tax Prefix Codes" in ITC Settings with same "Sales Tax and Charges template"
    please add all posible "Sales Tax and Charges template" in Sales Invoice into "Tax Prefix Codes" in ITC Settings
    5. CSV file will attached to Tax Invoice Exporter document

#### if "Use Amended From as TIN Revision Flag" in ITC Settins enabled:
every Sales Invoice which has "amended_from" will acknowledge as Sales Invoice revision
for this case, "Tax Prefix Codes" latest character changes from 0 to 1 ( from 010 into 011 )

#### if "Invoice Name In eFaktur Template" in ITC Settings filled:
when mapping Sales Invoice data into Efaktur format, specific field name in "Invoice Name In eFaktur Template" will used as invoice number Efaktur format

## License

MIT