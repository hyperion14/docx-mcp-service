import requests

def test_generate_docx():
    url = "http://localhost:5000/generate_docx"
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    data = {"text": "Testtext", "name": "TestUser"}
    r = requests.post(url, json=data, headers=headers)
    assert r.status_code == 200
    assert "download_url" in r.json()
