#!/usr/bin/env python3

"""
LUKHAS Revenue Tracker - Monitor monetization across all domains
Real-time tracking of MRR, usage, and growth metrics
"""

from datetime import datetime, timezone


class LukhasRevenueTracker:
    """Track revenue across the LUKHAS ecosystem"""

    def __init__(self):
        self.domains = {
            "ai": {
                "name": "Main AI Platform",
                "products": ["NIΛS", "ΛBAS", "DΛST"],
                "pricing": {"starter": 0, "pro": 299, "enterprise": 5000},
                "subscribers": {"starter": 0, "pro": 0, "enterprise": 0},
                "api_calls": 0,
                "api_revenue": 0,
            },
            "id": {
                "name": "Identity Service",
                "products": ["ΛiD"],
                "pricing": {"verification": 0.50, "individual": 9.99, "business": 99},
                "verifications": 0,
                "subscribers": {"individual": 0, "business": 0},
            },
            "dev": {
                "name": "Developer Platform",
                "products": ["SDK", "API", "Tools"],
                "pricing": {"free": 0, "pro": 99, "team": 499},
                "subscribers": {"free": 0, "pro": 0, "team": 0},
            },
            "store": {
                "name": "App Marketplace",
                "products": ["Agents", "Templates", "Plugins"],
                "sales": [],
                "commission_rate": 0.30,
                "total_sales": 0,
                "commission_earned": 0,
            },
            "cloud": {
                "name": "Cloud Services",
                "products": ["Hosting", "Scaling", "Analytics"],
                "pricing": {"starter": 99, "business": 999, "enterprise": 10000},
                "subscribers": {"starter": 0, "business": 0, "enterprise": 0},
            },
            "team": {
                "name": "Team Collaboration",
                "products": ["Workspace", "Admin", "Analytics"],
                "pricing": {"small": 299, "medium": 999, "large": 2999},
                "teams": {"small": 0, "medium": 0, "large": 0},
            },
        }

        self.metrics = {
            "total_mrr": 0,
            "total_arr": 0,
            "total_customers": 0,
            "growth_rate": 0,
            "churn_rate": 0,
            "ltv": 0,
            "cac": 0,
            "runway_months": 0,
        }

    def add_subscriber(self, domain: str, tier: str):
        """Add a new subscriber"""
        if domain in self.domains:
            if "subscribers" in self.domains[domain]:
                self.domains[domain]["subscribers"][tier] += 1
            elif "teams" in self.domains[domain]:
                self.domains[domain]["teams"][tier] += 1

    def add_api_usage(self, domain: str, calls: int):
        """Track API usage"""
        if domain == "ai":
            self.domains[domain]["api_calls"] += calls
            # $0.01 per call after free tier
            revenue = max(0, (calls - 1000)) * 0.01
            self.domains[domain]["api_revenue"] += revenue

    def add_marketplace_sale(self, amount: float):
        """Record marketplace sale"""
        domain = "store"
        self.domains[domain]["sales"].append(
            {
                "amount": amount,
                "date": datetime.now(timezone.utc).isoformat(),
                "commission": amount * self.domains[domain]["commission_rate"],
            }
        )
        self.domains[domain]["total_sales"] += amount
        self.domains[domain]["commission_earned"] += amount * self.domains[domain]["commission_rate"]

    def add_verification(self, count: int):
        """Track identity verifications"""
        domain = "id"
        self.domains[domain]["verifications"] += count

    def calculate_mrr(self) -> float:
        """Calculate total Monthly Recurring Revenue"""
        total_mrr = 0

        # ai
        ai = self.domains["ai"]
        total_mrr += (
            ai["subscribers"]["pro"] * ai["pricing"]["pro"]
            + ai["subscribers"]["enterprise"] * ai["pricing"]["enterprise"]
            + ai["api_revenue"]
        )

        # id
        id_domain = self.domains["id"]
        total_mrr += (
            id_domain["subscribers"]["individual"] * id_domain["pricing"]["individual"]
            + id_domain["subscribers"]["business"] * id_domain["pricing"]["business"]
            + (id_domain["verifications"] * id_domain["pricing"]["verification"]) / 30  # Daily to monthly
        )

        # dev
        dev = self.domains["dev"]
        total_mrr += (
            dev["subscribers"]["pro"] * dev["pricing"]["pro"] + dev["subscribers"]["team"] * dev["pricing"]["team"]
        )

        # store (marketplace commission)
        total_mrr += self.domains["store"]["commission_earned"]

        # cloud
        cloud = self.domains["cloud"]
        total_mrr += (
            cloud["subscribers"]["starter"] * cloud["pricing"]["starter"]
            + cloud["subscribers"]["business"] * cloud["pricing"]["business"]
        )

        # team
        team = self.domains["team"]
        total_mrr += (
            team["teams"]["small"] * team["pricing"]["small"]
            + team["teams"]["medium"] * team["pricing"]["medium"]
            + team["teams"]["large"] * team["pricing"]["large"]
        )

        self.metrics["total_mrr"] = total_mrr
        self.metrics["total_arr"] = total_mrr * 12

        return total_mrr

    def generate_dashboard(self) -> str:
        """Generate revenue dashboard"""
        mrr = self.calculate_mrr()

        dashboard = f"""
# 📊 LUKHAS Revenue Dashboard
Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")}

## 💰 Key Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **MRR** | ${mrr:,.2f} | $50,000 | {"🟢" if mrr >= 50000 else "🟡" if mrr >= 10000 else "🔴"} |
| **ARR** | ${mrr * 12:,.2f} | $600,000 | {"🟢" if mrr * 12 >= 600000 else "🟡"} |
| **Customers** | {self.get_total_customers()} | 1,000 | {"🟢" if self.get_total_customers() >= 1000 else "🟡"} |

## 🌐 Revenue by Domain

| Domain | Product | MRR | Customers | Growth |
|--------|---------|-----|-----------|--------|
"""

        for domain, data in self.domains.items():
            domain_mrr = self.calculate_domain_mrr(domain)
            customers = self.get_domain_customers(domain)
            dashboard += f"| **{domain}** | {data['name']} | ${domain_mrr:,.2f} | {customers} | +0% |\n"

        dashboard += f"""

## 📈 Growth Trajectory

### Current Run Rate
- Daily: ${mrr / 30:,.2f}
- Weekly: ${mrr / 4:,.2f}
- Monthly: ${mrr:,.2f}
- Annual: ${mrr * 12:,.2f}

### Path to $1M ARR
- Current ARR: ${mrr * 12:,.2f}
- Needed: ${1000000 - mrr * 12:,.2f}
- Required MRR: $83,333
- Gap: ${83333 - mrr:,.2f}/month

### Growth Requirements
- Add {int((83333 - mrr) / 299)} Pro subscribers OR
- Add {int((83333 - mrr) / 5000)} Enterprise customers OR
- Generate {int((83333 - mrr) / 0.01)} API calls/month

## 🎯 Revenue Breakdown

### Subscription Revenue (70%)
- Pro Tier: ${self.get_subscription_revenue("pro"):,.2f}
- Enterprise: ${self.get_subscription_revenue("enterprise"):,.2f}
- Teams: ${self.get_subscription_revenue("team"):,.2f}

### Usage Revenue (20%)
- API Calls: ${self.domains["ai"]["api_revenue"]:,.2f}
- Verifications: ${self.domains["id"]["verifications"] * 0.5:,.2f}
- Cloud Usage: $0.00

### Marketplace Revenue (10%)
- Total Sales: ${self.domains["store"]["total_sales"]:,.2f}
- Commission (30%): ${self.domains["store"]["commission_earned"]:,.2f}
- Active Vendors: 0

## 🚀 Quick Wins to Increase Revenue

1. **Launch Free Tier** (ai)
   - Target: 10,000 users
   - Conversion: 5% to Pro
   - Impact: +$150K MRR

2. **Developer Program** (dev)
   - Target: 1,000 developers
   - Conversion: 10% to paid
   - Impact: +$10K MRR

3. **Marketplace Launch** (store)
   - List 50 agents
   - Average price: $199
   - Impact: +$3K MRR commission

4. **Identity API** (id)
   - Target: 100K verifications/month
   - Price: $0.50 each
   - Impact: +$50K MRR

## 📅 30-Day Action Plan

Week 1:
- [ ] Deploy landing pages to all domains
- [ ] Set up payment processing (Stripe)
- [ ] Launch free tier

Week 2:
- [ ] Enable API billing
- [ ] Launch developer portal
- [ ] Start content marketing

Week 3:
- [ ] Open marketplace for vendors
- [ ] Launch affiliate program
- [ ] Begin paid advertising

Week 4:
- [ ] Enterprise sales outreach
- [ ] Partner channel development
- [ ] Optimize conversion funnels

## 🎯 Target Metrics (90 Days)

| Metric | Current | Target | Strategy |
|--------|---------|--------|----------|
| Free Users | 0 | 10,000 | Content marketing, SEO |
| Paid Users | 0 | 500 | Free trial conversion |
| Enterprise | 0 | 10 | Direct sales |
| MRR | ${mrr:,.2f} | $50,000 | Product-led growth |
| API Calls | 0 | 10M/month | Developer adoption |
"""

        return dashboard

    def calculate_domain_mrr(self, domain: str) -> float:
        """Calculate MRR for specific domain"""
        if domain == "ai":
            d = self.domains[domain]
            return d["subscribers"]["pro"] * 299 + d["subscribers"]["enterprise"] * 5000 + d["api_revenue"]
        elif domain == "id":
            d = self.domains[domain]
            return (
                d["subscribers"]["individual"] * 9.99
                + d["subscribers"]["business"] * 99
                + (d["verifications"] * 0.5) / 30
            )
        elif domain == "dev":
            d = self.domains[domain]
            return d["subscribers"]["pro"] * 99 + d["subscribers"]["team"] * 499
        elif domain == "store":
            return self.domains[domain]["commission_earned"]
        elif domain == "cloud":
            d = self.domains[domain]
            return d["subscribers"]["starter"] * 99 + d["subscribers"]["business"] * 999
        elif domain == "team":
            d = self.domains[domain]
            return d["teams"]["small"] * 299 + d["teams"]["medium"] * 999 + d["teams"]["large"] * 2999
        return 0

    def get_domain_customers(self, domain: str) -> int:
        """Get customer count for domain"""
        if "subscribers" in self.domains[domain]:
            return sum(self.domains[domain]["subscribers"].values())
        elif "teams" in self.domains[domain]:
            return sum(self.domains[domain]["teams"].values())
        elif domain == "id":
            return self.domains[domain]["verifications"]
        elif domain == "store":
            return len(self.domains[domain]["sales"])
        return 0

    def get_total_customers(self) -> int:
        """Get total customer count"""
        return sum(self.get_domain_customers(d) for d in self.domains)

    def get_subscription_revenue(self, tier: str) -> float:
        """Get revenue from specific tier"""
        revenue = 0
        for data in self.domains.values():
            if "subscribers" in data and tier in data["subscribers"]:
                if "pricing" in data and tier in data["pricing"]:
                    revenue += data["subscribers"][tier] * data["pricing"][tier]
        return revenue

    def simulate_growth(self, months: int = 12):
        """Simulate revenue growth"""
        print(f"\n📈 Growth Simulation ({months} months)")
        print("=" * 50)

        # Growth assumptions

        for month in range(1, months + 1):
            # Add subscribers with growth
            self.add_subscriber("ai", "pro")
            self.add_subscriber("dev", "pro")

            if month % 3 == 0:  # Enterprise every 3 months
                self.add_subscriber("ai", "enterprise")

            # Add API usage
            self.add_api_usage("ai", 10000 * month)

            # Add marketplace sales
            for _ in range(month * 2):
                self.add_marketplace_sale(199)

            # Add verifications
            self.add_verification(1000 * month)

            mrr = self.calculate_mrr()
            print(f"Month {month:2d}: ${mrr:>10,.2f} MRR | ${mrr * 12:>12,.2f} ARR")

            if mrr >= 83333:
                print(f"\n🎉 Reached $1M ARR in month {month}!")
                break


# Example usage
if __name__ == "__main__":
    tracker = LukhasRevenueTracker()

    # Simulate some initial traction
    tracker.add_subscriber("ai", "pro")
    tracker.add_subscriber("ai", "pro")
    tracker.add_subscriber("dev", "pro")
    tracker.add_api_usage("ai", 50000)
    tracker.add_marketplace_sale(499)
    tracker.add_marketplace_sale(199)
    tracker.add_verification(1000)

    # Generate dashboard
    dashboard = tracker.generate_dashboard()
    print(dashboard)

    # Save to file
    with open("revenue_dashboard.md", "w") as f:
        f.write(dashboard)

    # Run growth simulation
    tracker.simulate_growth(12)
