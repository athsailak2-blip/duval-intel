# Public Records Request (PRR) Guide - Code Enforcement Data

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
