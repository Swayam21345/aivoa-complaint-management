import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_kpis_and_trends(async_client: AsyncClient) -> None:
    # 1. Initially dashboard should return 0 for total complaints
    kpi_res = await async_client.get("/api/dashboard")
    assert kpi_res.status_code == 200
    kpi_data = kpi_res.json()
    assert kpi_data["total_complaints"] == 0
    assert kpi_data["new_count"] == 0

    trends_res = await async_client.get("/api/dashboard/trends")
    assert trends_res.status_code == 200
    trends_data = trends_res.json()
    assert "by_status" in trends_data
    assert "by_category" in trends_data
    assert "by_risk_level" in trends_data
    assert "by_priority" in trends_data
    assert "monthly_trend" in trends_data

    # 2. Seed test complaints
    c1 = {
        "product_name": "Paracetamol 500mg",
        "customer_name": "City Pharmacy",
        "category": "Packaging Defect",
        "risk_level": "High",
        "priority": "Critical",
        "status": "NEW",
        "complaint_text": "Leaking bottle seal",
    }
    c2 = {
        "product_name": "Amoxicillin 250mg",
        "customer_name": "General Hospital",
        "category": "Quality Defect",
        "risk_level": "Medium",
        "priority": "Medium",
        "status": "UNDER_REVIEW",
        "complaint_text": "Color variation",
    }
    await async_client.post("/api/complaints", json=c1)
    await async_client.post("/api/complaints", json=c2)

    # 3. Verify KPIs updated
    kpi_res2 = await async_client.get("/api/dashboard")
    assert kpi_res2.status_code == 200
    kpi2 = kpi_res2.json()
    assert kpi2["total_complaints"] == 2
    assert kpi2["new_count"] == 1
    assert kpi2["under_review_count"] == 1
    assert kpi2["critical_priority_count"] == 1
    assert kpi2["high_risk_count"] == 1
    assert kpi2["created_today_count"] == 2
    assert kpi2["created_this_month_count"] == 2

    # 4. Verify trends updated
    trends_res2 = await async_client.get("/api/dashboard/trends")
    assert trends_res2.status_code == 200
    t2 = trends_res2.json()
    assert len(t2["by_status"]) >= 2
    assert len(t2["monthly_trend"]) >= 1
