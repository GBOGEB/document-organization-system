README_NAMING_CONVENTION.txt
ALX folder 98684416 - MINERVA Applicable Documents ([AD_##])
Contract version 1.0.0  |  Source of truth: GBOGEB/document-organization-system,
contracts/master_transmittal/

PURPOSE
This folder holds the SCK CEN authoritative copies of the MINERVA Applicable
Documents that are issued to the Contractor as [AD_##] approved PDFs. This note
fixes how files here are named so the internal ALX record and the Contractor
tender package always point at the same document.

1. FILE NAMES ARE FUNCTIONAL, NEVER PERSONAL
   - Name every file after what it is, not who wrote or uploaded it.
   - Do NOT use personal names, initials or "<name> <number>" patterns in any
     file name, title or ALX description field. Authorship is recorded in the
     ALX metadata, not in the file name.
   - Existing author-based names are legacy. Rename them; do not re-create them.

2. LOCKED FUNCTIONAL NAMES
   Prefix    Locked functional name
   [AD_03]   AD_03_MINERVA_3D_Coordination_Model
   [AD_06]   AD_06_MIT_Interface_Catalogue
   [AD_11]   AD_11_MCS_Primary_Interface_Catalogue
   [AD_13]   AD_13_MCS_Secondary_Interface_Catalogue
   A new prefix is added to the "registry" block of the transmittal
   (examples/transmittal_current.json) before its first file is filed here.

3. CONTRACTOR-FACING PDF NAME
   [AD_##]_<Locked_Functional_Name>_vNN.pdf
   Example: [AD_13]_AD_13_MCS_Secondary_Interface_Catalogue_v01.pdf
   - The [AD_##] prefix and the AD_## inside the name must be the same number.
   - vNN is a two-digit issue number (v01, v02, ...).

4. AUTHORITY: LATEST ALX NUMBER + DATE PREVAILS
   - The ALX document number and its release date are the authority.
   - When a single document changes (for example a Detailed Design P&ID
     revision, or the monthly [AD_03] 3D model update), re-export ONLY that
     document, bump its vNN, and add one new row to the Master Document
     Transmittal List with the new ALX number and date.
   - Never overwrite an issued PDF in place.

5. DISTINCT DOCUMENTS, NOT DUPLICATES
   [AD_06] MIT Interface Catalogue, [AD_11] MCS Primary Interface Catalogue and
   [AD_13] MCS Secondary Interface Catalogue are three separate documents.
   A DBE duplicate flag between them is false and should be cleared.

6. TRANSMITTAL ROW FIELDS
   Prefix | Functional_Name | MIN | ALX_ID | Date | Version | Approved_PDF_Flag
   - Leave MIN / ALX_ID / Date empty (null) until the real value is known.
     Placeholders such as "TBD" are rejected.
   - Approved_PDF_Flag may only be set when MIN, ALX_ID and Date are filled in.

7. HOW THIS IS CHECKED
   python contracts/master_transmittal/validate_transmittal.py \
       contracts/master_transmittal/examples/transmittal_current.json \
       [--filenames exported_names.txt] [--require-gate5]
   It rejects non-functional names, prefix/number mismatches, placeholder
   values, duplicate issues, a newer issue dated earlier than an older one,
   and approved rows without ALX authority. It reports Release Gate 5 as
   COMPLETE only when every current row has MIN, ALX_ID and Date.
