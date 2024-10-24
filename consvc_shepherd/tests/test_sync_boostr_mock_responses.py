"""A few useful mock response to help test the interactions with the Boostr API"""

MOCK_PRODUCTS_RESPONSE = [
    {
        "id": 212592,
        "name": "CA (CPM)",
        "full_name": "Firefox 2nd Tile CA (CPM)",
        "parent_id": 193700,
        "top_parent_id": 193700,
        "active": True,
        "rate_type_id": 124,
        "level": 1,
        "revenue_type": "Display",
        "margin": None,
        "show_in_forecast": True,
        "pg_enabled": False,
        "created_at": "2024-05-17T14:07:30.170Z",
        "updated_at": "2024-07-04T09:14:22.354Z",
        "custom_field": None,
        "created_by": "Kay Sales",
        "updated_by": "Kay Sales",
        "product_type": None,
        "product_family": {"id": 718, "name": "Direct"},
    },
    {
        "id": 28256,
        "name": "US (CPC)",
        "full_name": "Firefox New Tab US (CPC)",
        "parent_id": 28249,
        "top_parent_id": 28249,
        "active": True,
        "rate_type_id": 125,
        "level": 1,
        "revenue_type": "Display",
        "margin": None,
        "show_in_forecast": True,
        "pg_enabled": False,
        "created_at": "2020-02-25T23:30:47.054Z",
        "updated_at": "2024-04-10T16:07:24.399Z",
        "custom_field": None,
        "created_by": None,
        "updated_by": "Kay Sales",
        "product_type": None,
        "product_family": {"id": 718, "name": "Direct"},
    },
]

MOCK_DEALS_RESPONSE = [
    {
        "id": 1482241,
        "start_date": "2024-05-01",
        "end_date": "2024-05-31",
        "name": "HiProduce: CA Tiles May 2024",
        "stage_name": "Closed Won",
        "stage_id": 1087,
        "type": None,
        "source": None,
        "next_steps": "",
        "advertiser_id": 303109,
        "advertiser_name": "HiProduce",
        "agency_id": 303027,
        "agency_name": "GeistM",
        "created_at": "2024-05-16T20:16:02.704Z",
        "updated_at": "2024-05-31T12:48:17.896Z",
        "created_by": "Jay Sales",
        "updated_by": "Jay Sales",
        "deleted_at": None,
        "closed_at": "2024-05-17T16:06:33.539Z",
        "closed_reason": "Audience Fit",
        "closed_comments": "audience fit",
        "currency": "$",
        "budget": "10000.0",
        "budget_loc": "10000.0",
        "lead_id": None,
        "deal_members": [
            {
                "id": 4470961,
                "user_id": 17968,
                "email": "jsales@mozilla.com",
                "share": 100,
                "type": "Seller",
                "seller_type": "direct",
                "role": None,
                "product": None,
            }
        ],
        "custom_fields": {
            "Forecast Close Date": None,
            "Confidence": None,
            "Notes": None,
            "Timing": None,
            "Need": None,
            "Access": None,
            "Budget": None,
        },
        "integrations": [],
        "deal_contacts": [],
    },
    {
        "id": 1498421,
        "start_date": "2024-04-01",
        "end_date": "2024-06-30",
        "name": "Neutron: Neutron US, DE, FR",
        "stage_name": "Verbal",
        "stage_id": 1087,
        "type": None,
        "source": "Proactive to Client",
        "next_steps": "Sign IO",
        "advertiser_id": 1145175,
        "advertiser_name": "Neutron",
        "agency_id": None,
        "agency_name": None,
        "created_at": "2024-06-05T11:38:37.941Z",
        "updated_at": "2024-06-05T11:45:43.377Z",
        "created_by": "Kay Sales",
        "updated_by": "Kay Sales",
        "deleted_at": None,
        "closed_at": "2024-06-05T11:45:43.296Z",
        "closed_reason": "Performance",
        "closed_comments": "KPI's are in line with Client goals",
        "currency": "$",
        "budget": "50000.0",
        "budget_loc": "50000.0",
        "lead_id": None,
        "deal_members": [
            {
                "id": 4525424,
                "user_id": 21626,
                "email": "ksales@mozilla.com",
                "share": 100,
                "type": "Seller",
                "seller_type": "direct",
                "role": None,
                "product": None,
            },
            {
                "id": 4525425,
                "user_id": 21625,
                "email": "lsales@mozilla.com",
                "share": 100,
                "type": "Seller",
                "seller_type": "direct",
                "role": None,
                "product": None,
            },
        ],
        "custom_fields": {
            "Forecast Close Date": None,
            "Confidence": None,
            "Notes": None,
            "Timing": None,
            "Need": None,
            "Access": None,
            "Budget": None,
        },
        "integrations": [],
        "deal_contacts": [],
    },
]

MOCK_DEAL_PRODUCTS_RESPONSE = [
    {
        "id": 4599379,
        "deal_id": 1498421,
        "budget": 10000.0,
        "budget_loc": 10000.0,
        "custom_fields": {},
        "start_date": None,
        "end_date": None,
        "term": None,
        "period": None,
        "created_at": "2024-06-05T11:45:10.861Z",
        "updated_at": "2024-06-05T11:45:10.861Z",
        "deal_product_budgets": [
            {
                "id": 44736446,
                "month": "2024-04",
                "budget_loc": 10000.0,
                "budget": 10000.0,
            },
            {
                "id": 44736447,
                "month": "2024-05",
                "budget_loc": 0.0,
                "budget": 0.0,
            },
            {
                "id": 44736448,
                "month": "2024-06",
                "budget_loc": 0.0,
                "budget": 0.0,
            },
        ],
        "product": {
            "id": 204410,
            "name": "FR (CPM)",
            "full_name": "Firefox New Tab FR (CPM)",
            "level": 1,
            "parent": {"id": 28249, "name": "Firefox New Tab", "level": 0},
            "top_parent": {
                "id": 28249,
                "name": "Firefox New Tab",
                "level": 0,
            },
        },
        "territory": None,
    },
    {
        "id": 4599381,
        "deal_id": 1498421,
        "budget": 30000.0,
        "budget_loc": 30000.0,
        "custom_fields": {},
        "start_date": None,
        "end_date": None,
        "term": None,
        "period": None,
        "created_at": "2024-06-05T11:45:11.047Z",
        "updated_at": "2024-06-05T11:45:11.047Z",
        "deal_product_budgets": [
            {
                "id": 44736452,
                "month": "2024-04",
                "budget_loc": 10000.0,
                "budget": 10000.0,
            },
            {
                "id": 44736453,
                "month": "2024-05",
                "budget_loc": 10000.0,
                "budget": 10000.0,
            },
            {
                "id": 44736454,
                "month": "2024-06",
                "budget_loc": 10000.0,
                "budget": 10000.0,
            },
        ],
        "product": {
            "id": 28256,
            "name": "US (CPC)",
            "full_name": "Firefox New Tab US (CPC)",
            "level": 1,
            "parent": {"id": 28249, "name": "Firefox New Tab", "level": 0},
            "top_parent": {
                "id": 28249,
                "name": "Firefox New Tab",
                "level": 0,
            },
        },
        "territory": None,
    },
]
