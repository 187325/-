import requests


def get_public_ip():
    # 多个IP查询服务，提高成功率
    services = [
        'https://httpbin.org/ip',
        'https://api.ipify.org?format=json',
        'https://jsonip.com',
        'https://api.myip.com'
    ]

    for service in services:
        try:
            response = requests.get(service, timeout=5)
            data = response.json()

            # 不同服务返回的字段名可能不同
            if 'origin' in data:
                return data['origin']
            elif 'ip' in data:
                return data['ip']
            elif 'country' in data:  # myip.com的格式
                return data['ip']

        except Exception as e:
            print(f"服务 {service} 失败: {e}")
            continue

    return None


public_ip = get_public_ip()
print(f"公网IP: {public_ip}")
