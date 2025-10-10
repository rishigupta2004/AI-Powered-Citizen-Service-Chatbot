"""
Integration test: /api/v1/admin/backup and /api/v1/admin/restore
"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_admin_backup_restore():
    try:
        from fastapi.testclient import TestClient
        import app

        client = TestClient(app.app)

        dest_dir = "data/db/backups/test_integration"
        Path(dest_dir).mkdir(parents=True, exist_ok=True)

        # Backup
        resp = client.post("/api/v1/admin/backup", json={"scope": "all", "destination": dest_dir})
        assert resp.status_code == 200
        data = resp.json()
        print("Backup response:", data)
        assert data.get("status") == "completed"
        assert os.path.exists(os.path.join(dest_dir, "manifest.json"))

        # Restore
        resp2 = client.post("/api/v1/admin/restore", json={"source": dest_dir})
        assert resp2.status_code == 200
        data2 = resp2.json()
        print("Restore response:", data2)
        assert data2.get("status") == "completed"

        return True
    except Exception as e:
        print(f"❌ Admin backup/restore integration failed: {e}")
        return False

def main():
    print("🧪 Running admin backup/restore integration test...")
    ok = test_admin_backup_restore()
    print("✅ Result:", ok)
    return ok

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)