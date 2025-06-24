import requests

def get_public_ip():
    try:
        response = requests.get('https://httpbin.org/ip', timeout=10)
        return response.json()['origin']
    except Exception as e:
        print(f"获取失败: {e}")
        return None

public_ip = get_public_ip()
print(f"公网IP: {public_ip}")
