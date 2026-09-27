# PIREVO Phase 2B — Monetization Layer
Date: 2026-09-27
Market: Amazon.com / United States
Affiliate mode at implementation: OFF

## Amazon application readiness
Amazon's current application-review guidance requires at least 3 qualifying sales within the first 180 days after signup. Personal orders do not qualify. Amazon also says a good rule of thumb is at least 10 robust original public posts. PIREVO now has 10 public original guides.

## Current standard commission signals checked
- Kitchen: 4.5%
- Luggage: 4.0%
- Home: 3.0%
- Desk/electronics: rate depends on Amazon's product-category classification; do not assume one rate for all desk-tech items.

Do not hard-code an expected commission per product. Amazon controls category assignment and can change rates.

## Phase 2B implementation
Three buying-intent guides now have a researched named-product shortlist:
1. Small Apartment Organization
2. Home Office Desk Upgrades
3. Carry-On Travel Essentials

Each candidate contains:
- exact product/brand search phrase
- use-case fit
- buyer verification checks
- research signal
- Amazon.com outbound search link

No live price, star rating, availability, or fabricated hands-on-testing claims are stored.

## Activation model
public/pirevo/config.js remains:
affiliateEnabled: false
amazonAssociateTag: ""

When an Associate tag is issued:
1. set amazonAssociateTag
2. set affiliateEnabled=true
3. outbound Amazon search URLs automatically receive tag=<AssociateTag>
4. existing affiliate disclosure changes automatically
5. click events continue through GA4 if ga4Id is configured

## Why search links
Amazon confirms qualifying links may point to individual products or search-results pages. Search links reduce breakage when variants/ASINs move and let shoppers verify the current seller, price, stock and specification.

## Current candidate set
### Home
- Simple Houseware 24-Pocket Over-the-Door Organizer
- DELAMU 6-Tier Over-the-Door Basket Rack
- JARLINK 5-Shelf Over-the-Door Organizer

### Desk & Tech
- Amazon Basics Aluminum Portable Foldable Laptop Support Stand
- Spigen 65W USB-C GaN Dual-Port Charger
- MOUNTUP Dual Monitor Desk Mount

### Travel
- BAGAIL Compression Packing Cubes
- INIU 10,000mAh USB-C Portable Charger
- Omnpak 20L Personal Item Travel Bag

## Next execution gate
Apply to Amazon.com Associates only after confirming the account/business/tax details to be used. Once signup is complete, insert the issued Associate tag immediately and start the first-sale traffic sprint.
