# Duval County Lead Intelligence Dashboard

## Overview
This dashboard displays real estate distress signals and lead intelligence for Duval County, Florida (Jacksonville & Beaches area).

## Data Sources
- **Official Records** (or.duvalclerk.com) - Recorded documents since 1988
- **Court Records (CORE)** (core.duvalclerk.com) - Court cases and dockets
- **Foreclosure Sales** (duval.realforeclose.com) - Online foreclosure auctions
- **Tax Deed Sales** (duval.realtaxdeed.com) - Tax deed auctions
- **Property Appraiser** (paopropertysearch.coj.net) - Parcel and assessment data
- **Tax Collector** (tclieninfo.coj.net) - Tax lien information
- **GIS Mapping** (maps.coj.net/duvalproperty) - Property maps and layers
- **Code Enforcement** (jacksonville.gov) - Municipal code compliance

## Lead Scoring
Leads are scored 0-100 based on:
- Signal stack depth (number of distress signals)
- Signal recency
- Signal confidence
- Property equity estimate
- Deal path viability

## Deal Paths
- **Wholesale** - Quick flip to investor buyers
- **Sub-To** - Subject-to existing financing
- **Seller Finance** - Owner financing arrangement
- **Flip** - Renovation and resale
- **Rental Acquisition** - Buy and hold strategy
- **Probate** - Estate property acquisition
- **REO** - Bank-owned property
- **Creative Finance** - Non-traditional financing
- **Commercial** - Commercial property deals

## Refresh Schedule
- P0 Sources (Official Records, Court, Foreclosure, Tax Deed): Daily
- P1 Sources (Tax Collector, Code Enforcement): Weekly
- P2 Sources (Property Appraiser, GIS): Monthly

## Framework Version
v5.3.1 - Xcerebro County Intelligence Framework

## Deployment
This dashboard is hosted on GitHub Pages from the `duval-intel` repository.
