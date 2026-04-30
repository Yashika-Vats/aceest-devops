import requests

def test_health():
    res = requests.get("http://localhost:5000/health")
    assert res.status_code == 200