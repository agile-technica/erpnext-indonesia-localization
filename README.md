<div align="center">

<h1>ERPNext Indonesia Localization</h1>

![logopng](.github/logo.png)

[Website](https://www.agiletechnica.com)
  &nbsp;|&nbsp;
[Demo](https://erpnextindonesia-stg.frappe.cloud/app)


</div>



## Introduction


ERPNext Indonesia Localization is a custom application that helps businesses comply with Indonesian tax regulations through ERPNext.

It's built on [ERPNext](https://github.com/frappe/erpnext) and the [Frappe Framework](https://github.com/frappe/frappe). Check them out!

<br />

## Key Features

### Coretax XML Exporter

The **Coretax XML Exporter** allows users to generate tax-compliant XML files from Sales Invoices in ERPNext. These XML files follow DJP (Indonesia's tax authority) standards and can be uploaded to the Coretax system for e-Faktur approval. The feature supports batch processing and intelligently handles large datasets in the background.

<https://github.com/user-attachments/assets/4d619612-a160-4c3c-b25b-934a7c85af5e>

### Coretax Importer

The **Coretax Importer** enables users to import VAT Output data from DJP (in Excel format) back into ERPNext. Once uploaded, the system validates the data and updates the corresponding Sales Invoices with official tax information such as approval numbers and verification status.

<https://github.com/user-attachments/assets/dafae3d7-7f08-4584-9032-25edf23f3e39>

<br />

## Installation

For detailed instructions, please [refer to the documentation](Installation%20Documentation%20-%20ENG.pdf)

<br />

## Quick Start Guide


### 1. Master Data Setup:
Before starting the eFaktur process, make sure the [following reference data](coretax-reference-master-data) has been imported into your ERPNext system use [data import tools](https://docs.frappe.io/erpnext/user/manual/en/data-import):
- CoreTax Transaction Code Ref
- CoreTax Barang Jasa Ref
- CoreTax Facility Stamp Ref
- CoreTax Additional Info Ref
- CoreTax Unit Ref

### 2. Initial Setup:
| **Doctype**   | **Field**                      | **Description**                                                       |
| ------------- | ------------------------------ | --------------------------------------------------------------------- |
| **Company**   | `Company’s NITKU`              | Business Activity Location Identification Number (NITKU)              |
|               | `Use Company NITKU` (checkbox) | If checked, all reports use the parent company's NITKU                |
| **Branch**    | `Branch’s NITKU`               | Specific NITKU for each branch                                        |
| **Item**      | `Goods/Services Opt`           | A = Goods, B = Services                                               |
|               | `Goods/Services Ref`           | Linked to the “CoreTax Goods and Services Ref”                        |
| **UOM**       | `Unit Ref`                     | Reference code from Coretax, linked to “CoreTax Unit Ref”             |
| **Country**   | `CoreTax Country Ref`          | 3-letter uppercase country code (e.g., IDN for Indonesia)             |
| **Customer**  | `Customer ID Type`             | Options: TIN (NPWP), National ID (NIK), Passport, Other               |
|               | `Customer ID Number`           | Auto-filled based on selected ID type; from Tax ID if TIN is selected |
|               | `Customer Email as per Tax ID` | Must match the email registered with NPWP                             |
|               | `Customer’s NITKU`             | Customer's business location NITKU                                    |
|               | `Country`                      | Customer’s country code                                               |
| **Sales Taxes and Charges Template** | `Transaction Code`             | Coretax transaction code                                             |
|               | `Tax Additional Info`          | Required only for Transaction Code 07 or 08                           |
|               | `Tax Facility Stamp`           | Stamp details if applicable                                           |
|               | `Temporary Rate`               | Custom tax rate when applicable                                       |
|               | `Use Temporary Rate` (checkbox) | If checked, use Temporary rate



### 3. Transaction Setup:
| **Doctype**   | **Field**                      | **Description**                                                       |
| ------------- | ------------------------------ | --------------------------------------------------------------------- |
| **Sales Invoice** | `Tax Custom Document`      | Filled if there are additional documents                                        |
|               | `Tax Custom Document Period:`  | Date of the additional document                                         |
|               | `Luxury Goods Tax Rate`        | Rate for luxury item taxation                                         |



### 4. Sales Taxes and Charges Template Setup:
| **Template Title**    | **Field**                      | **Value**                                                       |
| --------------------  | ------------------------------ | ----------------------------------------------------------------|
| **PPN Penjualan 11%** | `Company`                      | Select company name                                             |
|                       | `Type`                         | Select "On Net Total"                                           |
|                       | `Account Head`                 | Select Account head for VAT (PPN)                               |
|                       | `Cost Center`                  | Select Cost Center head for VAT (PPN)                           |
|                       | `Tax Rate`                     | 12                                                              |
|                       | `Use Temporary Rate`           | uncheck                                                         |
| **PPN Penjualan 12%** | `Company`                      | Select company name                                             |
|                       | `Type`                         | Select "On Net Total"                                           |
|                       | `Account Head`                 | Select Account head for VAT (PPN)                               |
|                       | `Cost Center`                  | Select Cost Center head for VAT (PPN)                           |
|                       | `Tax Rate`                     | 11                                                              |
|                       | `Use Temporary Rate`           | check                                                           |
|                       | `Temporary Rate`               | 12                                                              |


#### Need assistance? Get in [touch with us.](mailto:info@agiletechnica.com)

<br />
<br />
<div align="center" style="padding-top: 0.75rem;">

 <a href="https://www.agiletechnica.com/" target="_blank">
  <img src=".github/logo_v3_light.png" style="height: 100px;">
 </a>
<br />
<br />

</div>
