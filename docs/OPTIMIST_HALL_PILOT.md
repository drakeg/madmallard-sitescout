# Optimist Hall directory pilot

Reference: https://www.optimisthall.com/tenants (public tenant directory).

## Why this is useful
The page lists numerous independent food, beverage, and retail tenants, with outbound links labeled **VIEW WEBSITE** or **ORDER ONLINE**. These links can lead to a merchant's own site **or** to an ordering platform (e.g., Toast, ChowNow). They are not interchangeable. Do not interpret a directory listing as evidence that a business has a bad website or wants a redesign.

## Pilot workflow
1. Inspect the public directory manually; save a page only when permitted. Do not commit its copyrighted HTML, photos, logos, or other assets.
2. Run `python3 -m app.directory saved.html --url https://www.optimisthall.com/tenants`.
3. Review candidate links. Separate official merchant websites, ordering providers, social profiles, and other destinations; confirm merchant ownership and the correct homepage manually.
4. Audit a small, approved sample with screenshot, performance, accessibility, and functional requirements checks. Preserve existing ordering/booking integrations.
5. Create original, clearly marked unofficial redesign concepts with synthetic or properly licensed assets.
6. Require human approval before publication or outreach; do not claim a business has consented or is a customer.

## Next implementation work
- Better DOM-level tenant-to-link association, classification, and evidence tracking.
- Playwright screenshot capture and link verification with explicit per-host limits.
- Design brief and three visual concepts for a synthetic restaurant.
- Builder comparison against commercial license, mandatory paid services, quality and functional completeness.

## Safety
This pilot is not permission to scrape the directory at scale, copy brand assets, or send unsolicited email. External links are **unverified candidates**, not qualified leads.
