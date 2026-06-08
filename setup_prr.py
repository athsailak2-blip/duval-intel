import os

# Step 4: Submit PRR for code enforcement data access
# Create PRR template and submission documentation

os.makedirs("docs/prr", exist_ok=True)

# Public Records Request template for code enforcement
prr_template = '''PUBLIC RECORDS REQUEST

Date: June 8, 2026

To: Jacksonville Municipal Code Compliance Division (MCCD)
Public Records Coordinator
214 North Hogan Street, 7th Floor
Jacksonville, FL 32202

RE: Public Records Request - Code Enforcement Case Data

Dear Public Records Coordinator,

Pursuant to Chapter 119, Florida Statutes (the Florida Public Records Act), I hereby request access to and copies of the following public records:

1. ACTIVE CODE ENFORCEMENT CASES
   - All active code enforcement cases as of the date of this request
   - Case ID/Number
   - Property address (including RE# if available)
   - Violation type/category
   - Case status (open, pending hearing, etc.)
   - Date opened
   - Property owner name (if available in public records)

2. CODE ENFORCEMENT LIENS (Past 24 Months)
   - All recorded code enforcement liens
   - Lien amount
   - Recording date
   - Property address
   - Case reference number

3. NUISANCE LIENS (Past 24 Months)
   - All recorded nuisance liens
   - Lien amount
   - Recording date
   - Property address
   - Case reference number

4. ADMINISTRATIVE HEARING RESULTS (Past 12 Months)
   - Hearing dates and outcomes
   - Fines assessed
   - Compliance deadlines
   - Property addresses

REQUEST FORMAT:
- Preferred format: Electronic (CSV, Excel, or JSON)
- If electronic format is not available: PDF or paper copies

SEARCH PARAMETERS:
- Geographic scope: All properties within Duval County/Jacksonville city limits
- Time period: Cases opened or liens recorded within the past 24 months
- Please include both residential and commercial properties

COST:
- I am willing to pay reasonable costs for duplication as authorized by law
- Please notify me if the estimated costs exceed $50.00
- If costs will exceed $50, please provide a detailed cost estimate before proceeding

CONTACT INFORMATION:
Name: [YOUR NAME]
Company: [YOUR COMPANY NAME]
Address: [YOUR ADDRESS]
Phone: [YOUR PHONE]
Email: [YOUR EMAIL]

PREFERRED DELIVERY METHOD:
Email: [YOUR EMAIL]

I understand that under Florida law, you have a reasonable time to respond to this request and to produce the records. I respectfully request that you acknowledge receipt of this request and provide an estimated timeline for production.

If any portion of this request is denied, please cite the specific statutory exemption and provide a written explanation as required by Section 119.07(1)(d), Florida Statutes.

Thank you for your assistance with this public records request.

Respectfully submitted,

[YOUR SIGNATURE]
[YOUR NAME]
[DATE]

---

CC: Duval County Clerk of Courts (for lien verification)
'''

with open("docs/prr/code_enforcement_prr_template.txt", "w") as f:
    f.write(prr_template)

print("Created: docs/prr/code_enforcement_prr_template.txt")

# PRR submission guide
prr_guide = '''# Public Records Request (PRR) Guide - Code Enforcement Data

## Overview
The Jacksonville Municipal Code Compliance Division (MCCD) requires a Public Records Request (PRR) for access to detailed code enforcement case data, liens, and administrative hearing records.

## Where to Submit

### Online Portal (Recommended)
- **URL**: https://jacksonvillefl.govqa.us/WEBAPP/_rs/supporthome.aspx
- **Method**: Create account and submit request online
- **Tracking**: Request ID provided for status checking

### Email
- **Address**: myjax@custhelp.com
- **Subject**: Public Records Request - Code Enforcement Data

### Mail
- **Address**:
  Jacksonville Municipal Code Compliance Division
  Attn: Public Records Coordinator
  214 North Hogan Street, 7th Floor
  Jacksonville, FL 32202

### Phone
- **Number**: (904) 630-CITY (2489)
- **Note**: Phone requests should be followed up in writing

## What to Request

### Essential Data Fields
1. **Case ID** - Unique identifier for each case
2. **Property Address** - Full street address
3. **RE Number** - Duval County Real Estate Number (if available)
4. **Violation Type** - Category of code violation
5. **Case Status** - Open, closed, pending, etc.
6. **Open Date** - When case was initiated
7 **Close Date** - When case was resolved (if applicable)
8. **Lien Amount** - Dollar amount of any recorded liens
9. **Lien Recording Date** - When lien was recorded
10. **Property Owner** - Name from tax records (if public)

### Violation Types to Request
- UNSAFE_STRUCTURE
- OVERGROWTH_VEGETATION
- JUNK_VEHICLE
- ZONING_VIOLATION
- PROPERTY_MAINTENANCE
- NUISANCE
- DEMOLITION_RELATED
- MINIMUM_BUILDING_STANDARDS

### Time Periods
- **Active Cases**: Current open cases
- **Closed Cases**: Past 24 months
- **Liens**: Past 24 months (or since last request)
- **Hearing Results**: Past 12 months

## Cost Considerations

### Florida Public Records Act Fees
- **Inspection**: Free (in person)
- **Copies**: $0.15 per page (paper)
- **Electronic**: Often free or minimal cost
- **Special Service Charge**: May apply for extensive requests
- **Cost Estimate**: Request if total exceeds $50

### Tips to Minimize Costs
1. Request electronic format when possible
2. Be specific about needed fields
3. Request data in batches (quarterly)
4. Offer to pick up rather than mail

## Response Timeline

### Florida Law Requirements
- **Acknowledgment**: Within a reasonable time
- **Production**: As promptly as possible
- **Extensions**: Allowed for voluminous requests
- **Denials**: Must cite specific statutory exemption

### Typical Timeline
- **Simple requests**: 3-5 business days
- **Complex requests**: 10-15 business days
- **Voluminous requests**: 30+ days (with updates)

## Follow-Up Process

### Tracking Your Request
1. Save your request ID/confirmation number
2. Check status via online portal or email
3. Follow up if no response within 10 business days

### If Request is Denied
1. Request written explanation citing specific exemption
2. Consider narrowing the request scope
3. Consult with legal counsel if necessary
4. File complaint with Florida Attorney General if warranted

## Automation Strategy

### Quarterly Refresh
1. Submit new PRR every 3 months
2. Request only "new since [last date]" cases
3. Maintain rolling 24-month dataset

### Data Integration
1. Import PRR response into system
2. Parse and normalize data
3. Match to parcel records
4. Generate new leads from violations
5. Update existing lead signals

## Sample Request Language

### For Initial Request
```
"All active code enforcement cases and all cases closed 
within the past 24 months, including case ID, property 
address, RE number, violation type, status, open date, 
close date, and lien information."
```

### For Follow-Up Request
```
"All code enforcement cases opened or updated since 
[DATE OF LAST REQUEST], including [same fields as initial]."
```

## Important Notes

### Privacy Considerations
- Some owner information may be redacted
- Tenant/occupant names may be confidential
- Medical/disability information is exempt

### Data Quality
- Addresses may need standardization
- RE numbers may not be included (requires matching)
- Case statuses may need interpretation
- Some cases may span multiple properties

### Legal Compliance
- Use data only for lawful purposes
- Do not harass property owners
- Respect privacy protections
- Comply with Fair Housing laws

## Contact Information

### MCCD Office
- **Address**: 214 North Hogan Street, 7th Floor
- **Hours**: 8 a.m. - 5 p.m., Monday through Friday
- **Phone**: (904) 630-CITY (2489)

### Online Resources
- **MCCD Website**: https://www.jacksonville.gov/departments/neighborhoods/municipal-code-compliance
- **PRR Portal**: https://jacksonvillefl.govqa.us/WEBAPP/_rs/supporthome.aspx
- **Property Search**: https://paopropertysearch.coj.net/

## Template Files
- `code_enforcement_prr_template.txt` - Ready-to-use PRR template
- Customize with your contact information before submitting
'''

with open("docs/prr/PRR_GUIDE.md", "w") as f:
    f.write(prr_guide)

print("Created: docs/prr/PRR_GUIDE.md")

# Create a tracking spreadsheet template
tracking_template = '''Case ID,Property Address,RE Number,Violation Type,Status,Open Date,Lien Amount,Notes,Lead Generated,Lead ID
CE-2026-0001,123 Main St,01-01-01-001-001,UNSAFE_STRUCTURE,OPEN,2026-01-15,5000,Structure condemned,Y,LEAD-XXX
CE-2026-0002,456 Oak Ave,01-01-01-001-002,OVERGROWTH,OPEN,2026-02-20,250,Grass over 12 inches,N,
CE-2026-0003,789 Pine Rd,01-01-01-001-003,JUNK_VEHICLE,CLOSED,2026-03-10,0,Resolved - vehicle removed,N,
'''

with open("docs/prr/code_enforcement_tracking_template.csv", "w") as f:
    f.write(tracking_template)

print("Created: docs/prr/code_enforcement_tracking_template.csv")

# Create a submission checklist
checklist = '''# PRR Submission Checklist

## Before Submitting
- [ ] Customize PRR template with your contact information
- [ ] Determine specific data fields needed
- [ ] Decide on time period (recommend 24 months)
- [ ] Choose submission method (online portal preferred)
- [ ] Prepare payment method if costs exceed $50

## Submission
- [ ] Submit PRR via chosen method
- [ ] Save confirmation/tracking number
- [ ] Note submission date
- [ ] Set calendar reminder for follow-up (10 business days)

## Follow-Up
- [ ] Check status after 5 business days
- [ ] Follow up if no acknowledgment after 10 business days
- [ ] Review received data for completeness
- [ ] Request clarification if data is incomplete
- [ ] Process data into lead system

## Integration
- [ ] Import data into system
- [ ] Normalize addresses and match to parcels
- [ ] Generate new leads from violations
- [ ] Update existing leads with new signals
- [ ] Mark source as "healthy" in dashboard

## Ongoing
- [ ] Schedule next PRR (quarterly recommended)
- [ ] Update tracking spreadsheet
- [ ] Monitor for new cases between PRRs
- [ ] Maintain relationship with MCCD records staff
'''

with open("docs/prr/SUBMISSION_CHECKLIST.md", "w") as f:
    f.write(checklist)

print("Created: docs/prr/SUBMISSION_CHECKLIST.md")

print("\n✓ Step 4 Complete: PRR documentation prepared")
print("  - PRR template: docs/prr/code_enforcement_prr_template.txt")
print("  - PRR guide: docs/prr/PRR_GUIDE.md")
print("  - Tracking template: docs/prr/code_enforcement_tracking_template.csv")
print("  - Submission checklist: docs/prr/SUBMISSION_CHECKLIST.md")
print("\n  Ready to submit PRR to:")
print("  - Online: https://jacksonvillefl.govqa.us/WEBAPP/_rs/supporthome.aspx")
print("  - Email: myjax@custhelp.com")
print("  - Mail: 214 North Hogan Street, 7th Floor, Jacksonville, FL 32202")
