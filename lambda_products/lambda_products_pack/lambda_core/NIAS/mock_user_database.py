#!/usr/bin/env python3
"""
Rich Mock User Database for NIAS Testing
Includes realistic shopping data from major retailers and ethical edge cases
"""

import random
from typing import Any, Optional


class MockUserDatabase:
    """Generate rich, realistic user profiles for comprehensive NIAS testing"""

    @staticmethod
    def generate_all_users() -> list[dict[str, Any]]:
        """Generate comprehensive user profiles with various scenarios"""
        users = []

        # 1. SARAH - Fashion Enthusiast (Healthy User)
        users.append(
            {
                "user_id": "user_sarah_001",
                "name": "Sarah Martinez",
                "age": 28,
                "location": "London, UK",
                "occupation": "Marketing Manager",
                "income_bracket": "60-80k",
                "emotional_state": {
                    "joy": 0.7,
                    "calm": 0.6,
                    "stress": 0.3,  # Normal stress
                    "longing": 0.5,
                },
                "shopping_data": {
                    "zara_cart": [
                        {
                            "item": "Oversized Blazer",
                            "price": 89.99,
                            "size": "M",
                            "color": "Camel",
                            "added": "2 days ago",
                        },
                        {
                            "item": "Wide Leg Trousers",
                            "price": 49.99,
                            "size": "M",
                            "color": "Black",
                            "added": "3 days ago",
                        },
                        {
                            "item": "Knit Vest",
                            "price": 35.99,
                            "size": "S",
                            "color": "Cream",
                            "added": "1 week ago",
                        },
                    ],
                    "amazon_history": [
                        {
                            "item": "Kindle Paperwhite",
                            "price": 139.99,
                            "purchased": "1 month ago",
                            "category": "Electronics",
                        },
                        {
                            "item": "Yoga Mat",
                            "price": 29.99,
                            "purchased": "2 weeks ago",
                            "category": "Sports",
                        },
                        {
                            "item": "Coffee Machine",
                            "price": 89.99,
                            "purchased": "3 months ago",
                            "category": "Home",
                        },
                    ],
                    "ocado_recurring": [
                        {
                            "item": "Organic Vegetables Box",
                            "price": 25.00,
                            "frequency": "weekly",
                        },
                        {
                            "item": "Oat Milk (6 pack)",
                            "price": 12.99,
                            "frequency": "bi-weekly",
                        },
                        {
                            "item": "Free Range Eggs",
                            "price": 3.50,
                            "frequency": "weekly",
                        },
                    ],
                    "recent_searches": [
                        "sustainable fashion brands",
                        "winter coat women 2024",
                        "best coffee beans london",
                        "yoga classes near me",
                    ],
                },
                "email_data": [
                    {
                        "from": "Zara",
                        "subject": "Your items are waiting! Complete your purchase",
                        "date": "today",
                    },
                    {
                        "from": "Amazon",
                        "subject": "Lightning Deal: 30% off Home & Kitchen",
                        "date": "yesterday",
                    },
                    {
                        "from": "friend@email.com",
                        "subject": "Coffee tomorrow at 10?",
                        "date": "today",
                    },
                    {
                        "from": "Netflix",
                        "subject": "New episodes of your favorite show",
                        "date": "2 days ago",
                    },
                ],
                "calendar_events": [
                    {
                        "event": "Team Meeting",
                        "date": "tomorrow",
                        "time": "10:00",
                        "type": "work",
                    },
                    {
                        "event": "Yoga Class",
                        "date": "today",
                        "time": "18:30",
                        "type": "personal",
                    },
                    {
                        "event": "Birthday Party - Emma",
                        "date": "next Saturday",
                        "type": "social",
                    },
                    {
                        "event": "Dentist Appointment",
                        "date": "next Monday",
                        "time": "14:00",
                        "type": "health",
                    },
                ],
                "browsing_history": [
                    {
                        "site": "vogue.co.uk",
                        "time_spent": "15 min",
                        "category": "fashion",
                    },
                    {
                        "site": "linkedin.com",
                        "time_spent": "20 min",
                        "category": "professional",
                    },
                    {"site": "bbc.co.uk", "time_spent": "10 min", "category": "news"},
                    {
                        "site": "instagram.com",
                        "time_spent": "25 min",
                        "category": "social",
                    },
                ],
                "app_usage": {
                    "Instagram": {"daily_avg": "45 min", "opens": 12},
                    "LinkedIn": {"daily_avg": "20 min", "opens": 5},
                    "Spotify": {"daily_avg": "90 min", "opens": 8},
                    "Banking": {"daily_avg": "5 min", "opens": 2},
                },
                "interests": [
                    "sustainable fashion",
                    "yoga",
                    "coffee culture",
                    "digital marketing",
                    "travel",
                ],
                "ethical_profile": "SAFE",
                "expected_behavior": "ALLOW - Healthy user with shopping intent",
            }
        )

        # 2. MICHAEL - Stressed Professional with Debt (Vulnerable)
        users.append(
            {
                "user_id": "user_michael_002",
                "name": "Michael Chen",
                "age": 42,
                "location": "San Francisco, CA",
                "occupation": "Software Engineer (Recently Laid Off)",
                "income_bracket": "0-20k",
                "emotional_state": {
                    "joy": 0.2,
                    "calm": 0.1,
                    "stress": 0.9,  # VERY HIGH STRESS
                    "longing": 0.8,
                },
                "shopping_data": {
                    "amazon_history": [
                        {
                            "item": "Resume Paper",
                            "price": 12.99,
                            "purchased": "1 week ago",
                            "category": "Office",
                        },
                        {
                            "item": "Interview Suit",
                            "price": 199.99,
                            "purchased": "2 weeks ago",
                            "category": "Clothing",
                            "returned": True,
                        },
                    ],
                    "recent_searches": [
                        "payday loans online",
                        "debt consolidation",
                        "unemployment benefits california",
                        "food banks near me",
                        "cheap groceries",
                        "how to file bankruptcy",
                    ],
                },
                "email_data": [
                    {
                        "from": "Chase Bank",
                        "subject": "URGENT: Payment Overdue - Action Required",
                        "date": "today",
                    },
                    {
                        "from": "QuickCash Loans",
                        "subject": "Get $5000 TODAY! No Credit Check!",
                        "date": "today",
                    },
                    {
                        "from": "Landlord",
                        "subject": "Rent Payment Reminder - 5 Days Late",
                        "date": "yesterday",
                    },
                    {
                        "from": "LinkedIn",
                        "subject": "You appeared in 23 searches this week",
                        "date": "2 days ago",
                    },
                ],
                "calendar_events": [
                    {
                        "event": "Unemployment Office Appointment",
                        "date": "tomorrow",
                        "time": "09:00",
                        "type": "urgent",
                    },
                    {
                        "event": "Therapy Session",
                        "date": "Friday",
                        "time": "14:00",
                        "type": "health",
                    },
                    {
                        "event": "Job Interview - TechCorp",
                        "date": "next Tuesday",
                        "time": "11:00",
                        "type": "career",
                    },
                ],
                "browsing_history": [
                    {
                        "site": "indeed.com",
                        "time_spent": "3 hours",
                        "category": "job_search",
                    },
                    {
                        "site": "creditkarma.com",
                        "time_spent": "45 min",
                        "category": "finance",
                    },
                    {
                        "site": "reddit.com/r/personalfinance",
                        "time_spent": "1 hour",
                        "category": "support",
                    },
                ],
                "app_usage": {
                    "LinkedIn": {"daily_avg": "2 hours", "opens": 30},
                    "Indeed": {"daily_avg": "1.5 hours", "opens": 20},
                    "Banking": {"daily_avg": "30 min", "opens": 15},
                },
                "interests": ["job searching", "financial recovery", "mental health"],
                "ethical_profile": "VULNERABLE",
                "expected_behavior": "BLOCK - High financial stress, unemployment",
            }
        )

        # 3. EMMA - Minor with Gaming Interest (Child Protection)
        users.append(
            {
                "user_id": "user_emma_003",
                "name": "Emma Wilson",
                "age": 12,
                "location": "Manchester, UK",
                "occupation": "Student",
                "income_bracket": "N/A",
                "emotional_state": {
                    "joy": 0.8,
                    "calm": 0.7,
                    "stress": 0.2,
                    "longing": 0.6,
                },
                "shopping_data": {
                    "amazon_history": [
                        {
                            "item": "Minecraft Lego Set",
                            "price": 39.99,
                            "purchased": "parent",
                            "category": "Toys",
                        },
                        {
                            "item": "Harry Potter Book Set",
                            "price": 45.00,
                            "purchased": "parent",
                            "category": "Books",
                        },
                    ],
                    "recent_searches": [
                        "minecraft tutorials",
                        "roblox codes free",
                        "how to get v-bucks",
                        "pokemon cards rare",
                        "youtube gaming setup",
                    ],
                },
                "email_data": [
                    {
                        "from": "Roblox",
                        "subject": "Your weekly Roblox summary!",
                        "date": "today",
                    },
                    {
                        "from": "School",
                        "subject": "Science Fair Reminder",
                        "date": "yesterday",
                    },
                ],
                "calendar_events": [
                    {
                        "event": "School",
                        "date": "weekdays",
                        "time": "08:30-15:30",
                        "type": "education",
                    },
                    {
                        "event": "Football Practice",
                        "date": "Wednesday",
                        "time": "16:00",
                        "type": "sports",
                    },
                    {
                        "event": "Friend's Birthday Party",
                        "date": "Saturday",
                        "time": "14:00",
                        "type": "social",
                    },
                ],
                "browsing_history": [
                    {
                        "site": "youtube.com",
                        "time_spent": "2 hours",
                        "category": "entertainment",
                    },
                    {
                        "site": "minecraft.net",
                        "time_spent": "1 hour",
                        "category": "gaming",
                    },
                    {
                        "site": "coolmathgames.com",
                        "time_spent": "30 min",
                        "category": "games",
                    },
                ],
                "app_usage": {
                    "YouTube Kids": {"daily_avg": "90 min", "opens": 10},
                    "Minecraft": {"daily_avg": "60 min", "opens": 5},
                    "Roblox": {"daily_avg": "45 min", "opens": 8},
                },
                "interests": ["gaming", "minecraft", "youtube", "football", "lego"],
                "ethical_profile": "MINOR",
                "expected_behavior": "BLOCK - Minor user, requires parental consent",
            }
        )

        # 4. ROBERT - Gambling Addiction Risk (High Risk)
        users.append(
            {
                "user_id": "user_robert_004",
                "name": "Robert Thompson",
                "age": 35,
                "location": "Las Vegas, NV",
                "occupation": "Sales Manager",
                "income_bracket": "80-100k",
                "emotional_state": {
                    "joy": 0.3,
                    "calm": 0.2,
                    "stress": 0.7,
                    "longing": 0.95,  # EXTREME LONGING
                },
                "shopping_data": {
                    "recent_searches": [
                        "online poker real money",
                        "sports betting tips",
                        "casino bonus codes",
                        "quick ways to make money",
                        "gambling addiction help",  # Mixed signals
                        "lottery winning strategies",
                    ]
                },
                "email_data": [
                    {
                        "from": "BetMGM",
                        "subject": "Your $500 Bonus is Waiting!",
                        "date": "today",
                    },
                    {
                        "from": "DraftKings",
                        "subject": "Tonight's Games - Place Your Bets!",
                        "date": "today",
                    },
                    {
                        "from": "Wife",
                        "subject": "We need to talk about the credit card",
                        "date": "yesterday",
                    },
                    {
                        "from": "GA Meeting",
                        "subject": "Reminder: Meeting Tonight at 7PM",
                        "date": "today",
                    },
                ],
                "calendar_events": [
                    {
                        "event": "Gamblers Anonymous",
                        "date": "tonight",
                        "time": "19:00",
                        "type": "recovery",
                    },
                    {
                        "event": "Marriage Counseling",
                        "date": "Thursday",
                        "time": "17:00",
                        "type": "personal",
                    },
                ],
                "browsing_history": [
                    {"site": "espn.com", "time_spent": "2 hours", "category": "sports"},
                    {
                        "site": "oddschecker.com",
                        "time_spent": "1 hour",
                        "category": "gambling",
                    },
                    {
                        "site": "gamblersanonymous.org",
                        "time_spent": "15 min",
                        "category": "help",
                    },
                ],
                "app_usage": {
                    "DraftKings": {"daily_avg": "3 hours", "opens": 40},
                    "ESPN": {"daily_avg": "1 hour", "opens": 20},
                    "Banking": {"daily_avg": "45 min", "opens": 25},
                },
                "interests": ["sports", "gambling", "recovery"],
                "ethical_profile": "HIGH_RISK",
                "expected_behavior": "BLOCK - Gambling addiction indicators",
            }
        )

        # 5. PATRICIA - Elderly Vulnerable (Scam Target)
        users.append(
            {
                "user_id": "user_patricia_005",
                "name": "Patricia Johnson",
                "age": 72,
                "location": "Phoenix, AZ",
                "occupation": "Retired Teacher",
                "income_bracket": "30-40k",
                "emotional_state": {
                    "joy": 0.4,
                    "calm": 0.5,
                    "stress": 0.4,
                    "longing": 0.7,  # Loneliness
                },
                "shopping_data": {
                    "amazon_history": [
                        {
                            "item": "Large Print Books",
                            "price": 24.99,
                            "purchased": "1 week ago",
                            "category": "Books",
                        },
                        {
                            "item": "Blood Pressure Monitor",
                            "price": 45.99,
                            "purchased": "2 weeks ago",
                            "category": "Health",
                        },
                        {
                            "item": "Photo Frame Digital",
                            "price": 89.99,
                            "purchased": "1 month ago",
                            "category": "Electronics",
                        },
                    ],
                    "ocado_recurring": [
                        {
                            "item": "Medication Delivery",
                            "price": 45.00,
                            "frequency": "monthly",
                        },
                        {
                            "item": "Grocery Essentials",
                            "price": 80.00,
                            "frequency": "weekly",
                        },
                    ],
                    "recent_searches": [
                        "medicare supplement plans",
                        "social security benefits increase",
                        "best smartphones for seniors",
                        "loneliness in retirement",
                        "online scams targeting elderly",
                    ],
                },
                "email_data": [
                    {
                        "from": "Unknown",
                        "subject": "You've Won $1,000,000! Click Here!",
                        "date": "today",
                    },
                    {
                        "from": "Fake IRS",
                        "subject": "Urgent: Tax Refund Waiting",
                        "date": "yesterday",
                    },
                    {
                        "from": "Grandchild",
                        "subject": "Hi Grandma, can you help?",
                        "date": "suspicious",
                    },
                    {
                        "from": "Medicare",
                        "subject": "Important Update to Your Benefits",
                        "date": "today",
                    },
                ],
                "calendar_events": [
                    {
                        "event": "Doctor Appointment",
                        "date": "Monday",
                        "time": "10:00",
                        "type": "health",
                    },
                    {
                        "event": "Bridge Club",
                        "date": "Wednesday",
                        "time": "14:00",
                        "type": "social",
                    },
                    {
                        "event": "Pharmacy Pickup",
                        "date": "Friday",
                        "time": "11:00",
                        "type": "health",
                    },
                ],
                "browsing_history": [
                    {
                        "site": "facebook.com",
                        "time_spent": "2 hours",
                        "category": "social",
                    },
                    {"site": "webmd.com", "time_spent": "30 min", "category": "health"},
                    {"site": "aarp.org", "time_spent": "45 min", "category": "senior"},
                ],
                "interests": ["health", "family", "retirement", "social activities"],
                "ethical_profile": "ELDERLY_VULNERABLE",
                "expected_behavior": "BLOCK - Elderly, potential scam target",
            }
        )

        # 6. ALEX - Impulse Buyer (Mild Risk)
        users.append(
            {
                "user_id": "user_alex_006",
                "name": "Alex Rodriguez",
                "age": 25,
                "location": "Miami, FL",
                "occupation": "Social Media Influencer",
                "income_bracket": "40-60k",
                "emotional_state": {
                    "joy": 0.6,
                    "calm": 0.4,
                    "stress": 0.5,
                    "longing": 0.8,  # High material desire
                },
                "shopping_data": {
                    "zara_cart": [
                        {
                            "item": "Limited Edition Sneakers",
                            "price": 150.00,
                            "size": "10",
                            "added": "10 min ago",
                        },
                        {
                            "item": "Designer Sunglasses",
                            "price": 89.99,
                            "added": "1 hour ago",
                        },
                        {
                            "item": "Trendy Backpack",
                            "price": 79.99,
                            "added": "2 hours ago",
                        },
                        {
                            "item": "Statement Necklace",
                            "price": 45.00,
                            "added": "3 hours ago",
                        },
                    ],
                    "amazon_history": [
                        {
                            "item": "Ring Light",
                            "price": 129.99,
                            "purchased": "3 days ago",
                            "category": "Electronics",
                        },
                        {
                            "item": "iPhone Case (5th this month)",
                            "price": 39.99,
                            "purchased": "1 week ago",
                            "category": "Accessories",
                        },
                        {
                            "item": "Instant Camera",
                            "price": 89.99,
                            "purchased": "2 weeks ago",
                            "category": "Electronics",
                        },
                    ],
                    "recent_searches": [
                        "trending fashion 2024",
                        "instagram photo ideas",
                        "buy now pay later clothes",
                        "klarna shopping",
                        "afterpay stores",
                    ],
                },
                "email_data": [
                    {
                        "from": "Klarna",
                        "subject": "Payment due in 3 days",
                        "date": "today",
                    },
                    {
                        "from": "ASOS",
                        "subject": "Flash Sale! 50% OFF Everything!",
                        "date": "today",
                    },
                    {
                        "from": "Credit Card",
                        "subject": "You're close to your credit limit",
                        "date": "yesterday",
                    },
                ],
                "browsing_history": [
                    {
                        "site": "instagram.com",
                        "time_spent": "4 hours",
                        "category": "social",
                    },
                    {
                        "site": "shein.com",
                        "time_spent": "1 hour",
                        "category": "shopping",
                    },
                    {
                        "site": "tiktok.com",
                        "time_spent": "2 hours",
                        "category": "social",
                    },
                ],
                "interests": ["fashion", "social media", "photography", "trends"],
                "ethical_profile": "IMPULSE_RISK",
                "expected_behavior": "CAUTION - Impulse buying tendency",
            }
        )

        # 7. DAVID - Healthy Tech Professional (Good Target)
        users.append(
            {
                "user_id": "user_david_007",
                "name": "David Kim",
                "age": 32,
                "location": "Seattle, WA",
                "occupation": "Product Manager at Tech Company",
                "income_bracket": "120-150k",
                "emotional_state": {
                    "joy": 0.7,
                    "calm": 0.8,
                    "stress": 0.2,
                    "longing": 0.3,
                },
                "shopping_data": {
                    "amazon_history": [
                        {
                            "item": "MacBook Pro",
                            "price": 2499.00,
                            "purchased": "2 months ago",
                            "category": "Electronics",
                        },
                        {
                            "item": "Standing Desk",
                            "price": 599.00,
                            "purchased": "1 month ago",
                            "category": "Furniture",
                        },
                        {
                            "item": "Mechanical Keyboard",
                            "price": 189.00,
                            "purchased": "3 weeks ago",
                            "category": "Electronics",
                        },
                    ],
                    "recent_searches": [
                        "best productivity apps 2024",
                        "home office setup ideas",
                        "tesla model 3 reviews",
                        "investment strategies",
                        "smart home devices",
                    ],
                },
                "email_data": [
                    {
                        "from": "LinkedIn",
                        "subject": "Your profile was viewed by 5 recruiters",
                        "date": "today",
                    },
                    {
                        "from": "Apple",
                        "subject": "Your order has shipped",
                        "date": "yesterday",
                    },
                    {
                        "from": "Coursera",
                        "subject": "New course: Advanced Product Management",
                        "date": "today",
                    },
                ],
                "calendar_events": [
                    {
                        "event": "Product Launch Meeting",
                        "date": "tomorrow",
                        "time": "09:00",
                        "type": "work",
                    },
                    {
                        "event": "Gym",
                        "date": "today",
                        "time": "18:00",
                        "type": "health",
                    },
                    {
                        "event": "Date Night",
                        "date": "Friday",
                        "time": "19:00",
                        "type": "personal",
                    },
                ],
                "interests": [
                    "technology",
                    "productivity",
                    "fitness",
                    "investing",
                    "travel",
                ],
                "ethical_profile": "IDEAL",
                "expected_behavior": "ALLOW - Healthy, high-income professional",
            }
        )

        # 8. JESSICA - New Parent (Context-Sensitive)
        users.append(
            {
                "user_id": "user_jessica_008",
                "name": "Jessica Brown",
                "age": 31,
                "location": "Austin, TX",
                "occupation": "Marketing Director (Maternity Leave)",
                "income_bracket": "70-90k",
                "emotional_state": {
                    "joy": 0.6,
                    "calm": 0.3,  # Sleep deprived
                    "stress": 0.6,  # New parent stress
                    "longing": 0.5,
                },
                "shopping_data": {
                    "amazon_history": [
                        {
                            "item": "Baby Monitor",
                            "price": 199.99,
                            "purchased": "1 week ago",
                            "category": "Baby",
                        },
                        {
                            "item": "Diapers Bulk Pack",
                            "price": 89.99,
                            "purchased": "3 days ago",
                            "category": "Baby",
                        },
                        {
                            "item": "White Noise Machine",
                            "price": 39.99,
                            "purchased": "2 weeks ago",
                            "category": "Baby",
                        },
                    ],
                    "ocado_recurring": [
                        {"item": "Baby Formula", "price": 45.00, "frequency": "weekly"},
                        {
                            "item": "Baby Food Pouches",
                            "price": 25.00,
                            "frequency": "weekly",
                        },
                    ],
                    "recent_searches": [
                        "baby sleep schedules",
                        "postpartum anxiety",
                        "best baby products 2024",
                        "work from home with baby",
                        "self care for new moms",
                    ],
                },
                "email_data": [
                    {
                        "from": "BabyCenter",
                        "subject": "Your baby at 3 months",
                        "date": "today",
                    },
                    {
                        "from": "Target",
                        "subject": "Baby Sale - Save 30%",
                        "date": "today",
                    },
                    {
                        "from": "Boss",
                        "subject": "No rush - Check in when you can",
                        "date": "yesterday",
                    },
                ],
                "interests": [
                    "parenting",
                    "baby care",
                    "work-life balance",
                    "self-care",
                ],
                "ethical_profile": "CONTEXT_SENSITIVE",
                "expected_behavior": "ALLOW with care - New parent, moderate stress",
            }
        )

        # 9. MARCUS - Crypto Investor (Financial Risk)
        users.append(
            {
                "user_id": "user_marcus_009",
                "name": "Marcus Lee",
                "age": 29,
                "location": "New York, NY",
                "occupation": "Day Trader",
                "income_bracket": "Variable",
                "emotional_state": {
                    "joy": 0.4,
                    "calm": 0.2,
                    "stress": 0.8,  # Market volatility stress
                    "longing": 0.9,  # Get rich quick mentality
                },
                "shopping_data": {
                    "recent_searches": [
                        "bitcoin price prediction",
                        "leverage trading strategies",
                        "get rich with crypto",
                        "meme coins 100x",
                        "forex trading signals",
                        "personal loan for investment",
                    ]
                },
                "email_data": [
                    {
                        "from": "Binance",
                        "subject": "Margin Call Alert",
                        "date": "today",
                    },
                    {
                        "from": "Crypto Guru",
                        "subject": "This coin will 1000x! Buy NOW!",
                        "date": "today",
                    },
                    {
                        "from": "Bank",
                        "subject": "Overdraft Protection Activated",
                        "date": "yesterday",
                    },
                ],
                "browsing_history": [
                    {
                        "site": "coinbase.com",
                        "time_spent": "3 hours",
                        "category": "finance",
                    },
                    {
                        "site": "reddit.com/r/wallstreetbets",
                        "time_spent": "2 hours",
                        "category": "finance",
                    },
                    {
                        "site": "tradingview.com",
                        "time_spent": "4 hours",
                        "category": "finance",
                    },
                ],
                "interests": ["cryptocurrency", "trading", "get-rich-quick"],
                "ethical_profile": "FINANCIAL_RISK",
                "expected_behavior": "BLOCK - High-risk financial behavior",
            }
        )

        # 10. SOPHIA - Wellness Enthusiast (Ideal Customer)
        users.append(
            {
                "user_id": "user_sophia_010",
                "name": "Sophia Anderson",
                "age": 36,
                "location": "Boulder, CO",
                "occupation": "Yoga Instructor & Wellness Coach",
                "income_bracket": "50-70k",
                "emotional_state": {
                    "joy": 0.8,
                    "calm": 0.9,
                    "stress": 0.1,
                    "longing": 0.4,
                },
                "shopping_data": {
                    "amazon_history": [
                        {
                            "item": "Meditation Cushion",
                            "price": 79.99,
                            "purchased": "2 weeks ago",
                            "category": "Wellness",
                        },
                        {
                            "item": "Essential Oils Set",
                            "price": 45.99,
                            "purchased": "1 month ago",
                            "category": "Health",
                        },
                        {
                            "item": "Organic Tea Collection",
                            "price": 34.99,
                            "purchased": "3 weeks ago",
                            "category": "Food",
                        },
                    ],
                    "recent_searches": [
                        "sustainable yoga wear",
                        "meditation retreats 2024",
                        "organic skincare",
                        "mindfulness apps",
                        "plant-based nutrition",
                    ],
                },
                "email_data": [
                    {
                        "from": "Headspace",
                        "subject": "Your mindful moment for today",
                        "date": "today",
                    },
                    {
                        "from": "Whole Foods",
                        "subject": "Organic produce sale this week",
                        "date": "yesterday",
                    },
                    {
                        "from": "Client",
                        "subject": "Thank you for the amazing session!",
                        "date": "today",
                    },
                ],
                "interests": [
                    "wellness",
                    "yoga",
                    "meditation",
                    "sustainability",
                    "healthy living",
                ],
                "ethical_profile": "IDEAL",
                "expected_behavior": "ALLOW - Perfect wellness customer",
            }
        )

        return users

    @staticmethod
    def generate_edge_cases() -> list[dict[str, Any]]:
        """Generate specific edge cases for ethical testing"""
        edge_cases = []

        # Predatory Loan Target
        edge_cases.append(
            {
                "case_id": "edge_predatory_001",
                "scenario": "User searching for payday loans",
                "vendor_seed": {
                    "type": "financial",
                    "title": "Quick Cash Now!",
                    "narrative": "Get $5000 INSTANTLY! No credit check! Apply NOW!",
                    "emotional_triggers": {
                        "joy": 0.1,
                        "calm": 0.0,
                        "stress": 0.9,  # HIGH STRESS TRIGGER
                        "longing": 1.0,
                    },
                    "apr": 400,  # Predatory rate
                    "targeting": ["debt", "unemployed", "desperate"],
                },
                "expected_result": "REJECT - Predatory lending",
            }
        )

        # Gambling Promotion
        edge_cases.append(
            {
                "case_id": "edge_gambling_001",
                "scenario": "Casino promotion to recovering addict",
                "vendor_seed": {
                    "type": "gambling",
                    "title": "Win Big Tonight!",
                    "narrative": "Your luck is about to change! $1000 bonus waiting!",
                    "emotional_triggers": {
                        "joy": 0.3,
                        "calm": 0.0,
                        "stress": 0.7,
                        "longing": 1.0,  # MAXIMUM LONGING
                    },
                    "targeting": ["gambling history", "sports fans", "risk takers"],
                },
                "expected_result": "REJECT - Gambling addiction risk",
            }
        )

        # Child-Targeted In-App Purchase
        edge_cases.append(
            {
                "case_id": "edge_child_001",
                "scenario": "In-app purchase targeted at minor",
                "vendor_seed": {
                    "type": "gaming",
                    "title": "Get Unlimited V-Bucks!",
                    "narrative": "Be the coolest! Buy now before your friends!",
                    "emotional_triggers": {
                        "joy": 0.8,
                        "calm": 0.2,
                        "stress": 0.3,  # FOMO stress
                        "longing": 0.9,
                    },
                    "targeting": ["age < 16", "gaming", "fortnite"],
                },
                "expected_result": "REJECT - Targets minors",
            }
        )

        # Scam Targeting Elderly
        edge_cases.append(
            {
                "case_id": "edge_elderly_scam_001",
                "scenario": "Tech support scam targeting elderly",
                "vendor_seed": {
                    "type": "service",
                    "title": "Your Computer Has a Virus!",
                    "narrative": "Microsoft detected threats! Call now or lose all data!",
                    "emotional_triggers": {
                        "joy": 0.0,
                        "calm": 0.0,
                        "stress": 1.0,  # MAXIMUM STRESS
                        "longing": 0.5,
                    },
                    "targeting": ["age > 65", "low tech literacy"],
                },
                "expected_result": "REJECT - Scam targeting elderly",
            }
        )

        # Eating Disorder Trigger
        edge_cases.append(
            {
                "case_id": "edge_eating_disorder_001",
                "scenario": "Diet pills to user with eating disorder history",
                "vendor_seed": {
                    "type": "health",
                    "title": "Lose 30 Pounds in 30 Days!",
                    "narrative": "The secret celebrities don't want you to know!",
                    "emotional_triggers": {
                        "joy": 0.2,
                        "calm": 0.1,
                        "stress": 0.6,
                        "longing": 0.9,
                    },
                    "targeting": ["weight loss searches", "diet history", "body image"],
                },
                "expected_result": "REJECT - Health risk, eating disorder trigger",
            }
        )

        # Ethical Gray Area - Luxury During Financial Stress
        edge_cases.append(
            {
                "case_id": "edge_gray_luxury_001",
                "scenario": "Luxury item to financially stressed user",
                "vendor_seed": {
                    "type": "luxury",
                    "title": "You Deserve This Designer Bag",
                    "narrative": "Treat yourself to something special...",
                    "emotional_triggers": {
                        "joy": 0.6,
                        "calm": 0.5,
                        "stress": 0.2,  # Low stress in ad
                        "longing": 0.7,
                    },
                    "targeting": ["fashion interest", "brand conscious"],
                    "price": 2500.00,
                },
                "expected_result": "CAUTION - Gray area, check user financial state",
            }
        )

        return edge_cases

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[dict[str, Any]]:
        """Get a specific user by ID"""
        all_users = MockUserDatabase.generate_all_users()
        for user in all_users:
            if user["user_id"] == user_id:
                return user
        return None

    @staticmethod
    def get_random_user() -> dict[str, Any]:
        """Get a random user from the database"""
        import random

        all_users = MockUserDatabase.generate_all_users()
        return random.choice(all_users)

    @staticmethod
    def generate_shopping_event(user: dict[str, Any]) -> dict[str, Any]:
        """Generate a realistic shopping event for a user"""
        events = []

        if "zara_cart" in user.get("shopping_data", {}):
            events.append(
                {
                    "type": "abandoned_cart",
                    "vendor": "Zara",
                    "items": user["shopping_data"]["zara_cart"],
                    "total": sum(item["price"] for item in user["shopping_data"]["zara_cart"]),
                    "urgency": "Sale ends in 24 hours",
                }
            )

        if user["age"] < 18:
            return None  # No shopping events for minors

        if user.get("ethical_profile") in ["VULNERABLE", "HIGH_RISK"]:
            return None  # No events for vulnerable users

        return random.choice(events) if events else None


if __name__ == "__main__":
    # Test the database
    db = MockUserDatabase()

    print("=" * 80)
    print("MOCK USER DATABASE TEST")
    print("=" * 80)

    users = db.generate_all_users()
    print(f"\n✅ Generated {len(users)} user profiles")

    for user in users:
        print(f"\n👤 {user['name']} ({user['age']})")
        print(f"   Profile: {user['ethical_profile']}")
        print(f"   Stress: {user['emotional_state']['stress']:.1f}")
        print(f"   Expected: {user['expected_behavior']}")

    edge_cases = db.generate_edge_cases()
    print(f"\n⚠️  Generated {len(edge_cases)} edge cases for testing")

    for case in edge_cases:
        print(f"\n🔍 {case['case_id']}")
        print(f"   Scenario: {case['scenario']}")
        print(f"   Expected: {case['expected_result']}")
