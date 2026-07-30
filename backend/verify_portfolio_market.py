"""FinPilot AI – Portfolio & Market Module End-to-End Verification"""
import asyncio
import sys

from httpx import AsyncClient, ASGITransport


async def run_tests():
    from app.main import app as fastapi_app
    from app.database.session import engine
    from app.database.base import Base
    import app.models.user       # noqa
    import app.models.portfolio  # noqa

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=fastapi_app)
    passed = 0

    async with AsyncClient(transport=transport, base_url="http://test") as c:

        # ── Register & Login to get JWT ──────────────────────────────────────
        await c.post("/api/v1/auth/register", json={
            "full_name": "Test User", "email": "t@test.com",
            "password": "TestPass@123", "confirm_password": "TestPass@123",
        })
        r = await c.post("/api/v1/auth/login", json={"email": "t@test.com", "password": "TestPass@123"})
        token = r.json()["data"]["access_token"]
        auth = {"Authorization": f"Bearer {token}"}
        print(f"[PASS] Auth: login OK, token obtained")
        passed += 1

        # ── Portfolio: unauthenticated ────────────────────────────────────────
        r = await c.get("/api/v1/portfolios/")
        assert r.status_code == 401
        print(f"[PASS] Portfolio list (no token): 401")
        passed += 1

        # ── Portfolio: create ────────────────────────────────────────────────
        r = await c.post("/api/v1/portfolios/", headers=auth, json={
            "name": "Growth Fund", "description": "Long-term equity", "currency": "INR"
        })
        assert r.status_code == 201 and r.json()["success"]
        portfolio_id = r.json()["data"]["portfolio"]["id"]
        print(f"[PASS] Create portfolio: 201, id={portfolio_id[:8]}...")
        passed += 1

        # ── Portfolio: duplicate name ────────────────────────────────────────
        r = await c.post("/api/v1/portfolios/", headers=auth, json={"name": "Growth Fund"})
        assert r.status_code == 400
        print(f"[PASS] Duplicate portfolio name: 400")
        passed += 1

        # ── Portfolio: list ──────────────────────────────────────────────────
        r = await c.get("/api/v1/portfolios/", headers=auth)
        assert r.status_code == 200 and r.json()["data"]["total"] == 1
        print(f"[PASS] List portfolios: 200, total=1")
        passed += 1

        # ── Portfolio: add holdings via PATCH ────────────────────────────────
        r = await c.patch(f"/api/v1/portfolios/{portfolio_id}", headers=auth, json={
            "holdings": [
                {"symbol": "TCS", "exchange": "NSE", "quantity": 5, "average_buy_price": 3800.0, "asset_type": "equity"},
                {"symbol": "RELIANCE", "exchange": "NSE", "quantity": 10, "average_buy_price": 2450.0, "asset_type": "equity"},
            ]
        })
        assert r.status_code == 200 and r.json()["data"]["portfolio"]["holdings_count"] == 2
        print(f"[PASS] Add 2 holdings via PATCH: 200, holdings_count=2")
        passed += 1

        # ── Portfolio: get with holdings ─────────────────────────────────────
        r = await c.get(f"/api/v1/portfolios/{portfolio_id}", headers=auth)
        body = r.json()
        assert r.status_code == 200 and len(body["data"]["portfolio"]["holdings"]) == 2
        holding_id = body["data"]["portfolio"]["holdings"][0]["id"]
        print(f"[PASS] Get portfolio with holdings: 200, 2 holdings")
        passed += 1

        # ── Portfolio: summary ────────────────────────────────────────────────
        r = await c.get(f"/api/v1/portfolios/{portfolio_id}/summary?period=1M", headers=auth)
        summary = r.json()["data"]["summary"]
        assert r.status_code == 200 and "total_invested" in summary
        print(f"[PASS] Portfolio summary: 200, total_invested={summary['total_invested']}")
        passed += 1

        # ── Portfolio: invalid period ─────────────────────────────────────────
        r = await c.get(f"/api/v1/portfolios/{portfolio_id}/summary?period=BAD", headers=auth)
        assert r.status_code == 400
        print(f"[PASS] Invalid period: 400")
        passed += 1

        # ── Portfolio: forbidden ──────────────────────────────────────────────
        # Create second user
        await c.post("/api/v1/auth/register", json={
            "full_name": "Other", "email": "other@test.com",
            "password": "TestPass@123", "confirm_password": "TestPass@123",
        })
        r2 = await c.post("/api/v1/auth/login", json={"email": "other@test.com", "password": "TestPass@123"})
        other_token = r2.json()["data"]["access_token"]
        r = await c.get(f"/api/v1/portfolios/{portfolio_id}", headers={"Authorization": f"Bearer {other_token}"})
        assert r.status_code == 403
        print(f"[PASS] Forbidden (other user's portfolio): 403")
        passed += 1

        # ── Portfolio: delete holding ─────────────────────────────────────────
        r = await c.delete(f"/api/v1/portfolios/{portfolio_id}/holdings/{holding_id}", headers=auth)
        assert r.status_code == 200 and r.json()["data"]["remaining_holdings"] == 1
        print(f"[PASS] Delete holding: 200, remaining=1")
        passed += 1

        # ── Market: search (no token) ────────────────────────────────────────
        r = await c.get("/api/v1/market/search?q=TCS")
        assert r.status_code == 401
        print(f"[PASS] Market search (no token): 401")
        passed += 1

        # ── Market: search ────────────────────────────────────────────────────
        r = await c.get("/api/v1/market/search?q=TCS&limit=5", headers=auth)
        assert r.status_code == 200 and r.json()["data"]["total"] >= 1
        print(f"[PASS] Market search 'TCS': 200, results={r.json()['data']['total']}")
        passed += 1

        # ── Market: search query too short ────────────────────────────────────
        r = await c.get("/api/v1/market/search?q=T", headers=auth)
        assert r.status_code == 422, f"Expected 422 for short query, got {r.status_code}"
        print(f"[PASS] Search query too short: 422 (FastAPI validates min_length=2)")
        passed += 1

        # ── Market: stock details ─────────────────────────────────────────────
        r = await c.get("/api/v1/market/stocks/RELIANCE?period=1M", headers=auth)
        stock = r.json()["data"]["stock"]
        assert r.status_code == 200 and stock["symbol"] == "RELIANCE"
        print(f"[PASS] Stock details RELIANCE: 200, price={stock['price']['current']}")
        passed += 1

        # ── Market: unknown symbol ────────────────────────────────────────────
        r = await c.get("/api/v1/market/stocks/UNKNOWN_XYZ", headers=auth)
        assert r.status_code == 404
        print(f"[PASS] Unknown symbol: 404")
        passed += 1

        # ── Market: overview ──────────────────────────────────────────────────
        r = await c.get("/api/v1/market/overview?exchanges=NSE,BSE", headers=auth)
        overview = r.json()["data"]["overview"]
        assert r.status_code == 200 and "indices" in overview
        print(f"[PASS] Market overview: 200, indices={len(overview['indices'])}")
        passed += 1

        # ── Market: trending ─────────────────────────────────────────────────
        r = await c.get("/api/v1/market/trending?exchange=NSE&category=gainers&limit=5", headers=auth)
        assert r.status_code == 200 and r.json()["data"]["category"] == "gainers"
        print(f"[PASS] Trending gainers: 200, stocks={len(r.json()['data']['stocks'])}")
        passed += 1

        # ── Market: invalid category ──────────────────────────────────────────
        r = await c.get("/api/v1/market/trending?category=INVALID", headers=auth)
        assert r.status_code == 400
        print(f"[PASS] Invalid trending category: 400")
        passed += 1

    print()
    print("=" * 55)
    print(f"  Results: {passed} passed, 0 failed out of {passed} tests")
    print("=" * 55)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_tests())
