"""FinPilot AI – Auth Module End-to-End Verification Script"""
import asyncio
import sys

from httpx import AsyncClient, ASGITransport


async def run_tests():
    from app.main import app as fastapi_app
    from app.database.session import engine
    from app.database.base import Base
    import app.models.user  # noqa: F401

    # Bootstrap tables fresh for every test run
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=fastapi_app)
    passed = 0
    failed = 0

    async with AsyncClient(transport=transport, base_url="http://test") as client:

        # ── Test 1: Health Check ──────────────────────────────────
        r = await client.get("/health")
        assert r.status_code == 200 and r.json()["status"] == "healthy"
        print(f"[PASS] T1  Health Check: {r.status_code}")
        passed += 1

        # ── Test 2: Root ──────────────────────────────────────────
        r = await client.get("/")
        assert r.status_code == 200 and r.json()["success"] is True
        print(f"[PASS] T2  Root Endpoint: {r.status_code}")
        passed += 1

        # ── Test 3: Register ──────────────────────────────────────
        r = await client.post("/api/v1/auth/register", json={
            "full_name": "Aryan Sharma",
            "email": "aryan@finpilot.ai",
            "password": "SecurePass@123",
            "confirm_password": "SecurePass@123",
        })
        body = r.json()
        assert r.status_code == 201 and body["success"] is True, f"Register failed: {body}"
        assert body["data"]["user"]["email"] == "aryan@finpilot.ai"
        print(f"[PASS] T3  Register: {r.status_code} — {body['message']}")
        passed += 1

        # ── Test 4: Duplicate Registration ────────────────────────
        r = await client.post("/api/v1/auth/register", json={
            "full_name": "Aryan Sharma",
            "email": "aryan@finpilot.ai",
            "password": "SecurePass@123",
            "confirm_password": "SecurePass@123",
        })
        body = r.json()
        assert r.status_code == 400 and body["success"] is False
        print(f"[PASS] T4  Duplicate Email: {r.status_code} — {body['error']}")
        passed += 1

        # ── Test 5: Login ─────────────────────────────────────────
        r = await client.post("/api/v1/auth/login", json={
            "email": "aryan@finpilot.ai",
            "password": "SecurePass@123",
        })
        body = r.json()
        assert r.status_code == 200 and body["success"] is True, f"Login failed: {body}"
        assert "access_token" in body["data"]
        assert "refresh_token" in body["data"]
        access_token = body["data"]["access_token"]
        refresh_token = body["data"]["refresh_token"]
        print(f"[PASS] T5  Login: {r.status_code} — JWT issued (expires_in={body['data']['expires_in']}s)")
        passed += 1

        # ── Test 6: Wrong Password ────────────────────────────────
        r = await client.post("/api/v1/auth/login", json={
            "email": "aryan@finpilot.ai",
            "password": "WrongPass@999",
        })
        body = r.json()
        assert r.status_code == 401 and body["success"] is False
        print(f"[PASS] T6  Wrong Password: {r.status_code} — {body['error']}")
        passed += 1

        # ── Test 7: Protected Route — No Token ────────────────────
        r = await client.get("/api/v1/auth/me")
        body = r.json()
        assert r.status_code == 401 and body["success"] is False
        print(f"[PASS] T7  /me no token: {r.status_code} — {body['error']}")
        passed += 1

        # ── Test 8: Protected Route — Valid Token ─────────────────
        r = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        body = r.json()
        assert r.status_code == 200 and body["success"] is True, f"/me failed: {body}"
        assert body["data"]["user"]["email"] == "aryan@finpilot.ai"
        print(f"[PASS] T8  /me valid JWT: {r.status_code} — email={body['data']['user']['email']}")
        passed += 1

        # ── Test 9: Protected Route — Tampered Token ──────────────
        r = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.tampered.sig"},
        )
        body = r.json()
        assert r.status_code == 401 and body["success"] is False
        print(f"[PASS] T9  /me tampered JWT: {r.status_code} — {body['error']}")
        passed += 1

        # ── Test 10: Refresh Token ────────────────────────────────
        r = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        body = r.json()
        assert r.status_code == 200 and "access_token" in body["data"], f"Refresh failed: {body}"
        new_token = body["data"]["access_token"]
        print(f"[PASS] T10 Refresh Token: {r.status_code} — new access token issued")
        passed += 1

        # ── Test 11: New Token Works ──────────────────────────────
        r = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {new_token}"},
        )
        assert r.status_code == 200 and r.json()["success"] is True
        print(f"[PASS] T11 /me with refreshed JWT: {r.status_code} — OK")
        passed += 1

        # ── Test 12: Logout ───────────────────────────────────────
        r = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {new_token}"},
        )
        body = r.json()
        assert r.status_code == 200 and body["success"] is True
        print(f"[PASS] T12 Logout: {r.status_code} — {body['message']}")
        passed += 1

        # ── Test 13: Weak Password Rejected ──────────────────────
        r = await client.post("/api/v1/auth/register", json={
            "full_name": "Weak User",
            "email": "weak@finpilot.ai",
            "password": "password",
            "confirm_password": "password",
        })
        assert r.status_code == 422
        print(f"[PASS] T13 Weak password rejected: {r.status_code} (422 Unprocessable)")
        passed += 1

    print()
    print(f"{'='*50}")
    print(f"  Results: {passed} passed, {failed} failed out of {passed+failed} tests")
    print(f"{'='*50}")

    await engine.dispose()

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_tests())
