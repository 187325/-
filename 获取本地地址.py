import streamlit as st
import subprocess
import sys

def install_package(package):
    """自动安装缺失的包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_requests():
    """检查并安装requests包"""
    try:
        import requests
        return requests
    except ImportError:
        st.warning("正在安装 requests 包...")
        if install_package("requests"):
            st.success("requests 包安装成功！")
            import requests
            return requests
        else:
            st.error("无法安装 requests 包")
            return None

def get_public_ip():
    """获取公网IP"""
    # 确保requests包可用
    requests = check_and_install_requests()
    if not requests:
        return None
    
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
            st.warning(f"服务 {service} 失败: {e}")
            continue

    return None

# Streamlit 应用界面
def main():
    st.title("🌐 公网IP地址查询工具")
    st.write("点击按钮获取当前的公网IP地址")
    
    if st.button("获取公网IP", type="primary"):
        with st.spinner("正在查询公网IP..."):
            public_ip = get_public_ip()
            
        if public_ip:
            st.success(f"🎉 公网IP: **{public_ip}**")
            
            # 额外显示一些信息
            st.info("ℹ️ 这是您当前网络的公网IP地址")
            
            # 可以添加复制按钮的提示
            st.code(public_ip, language="text")
            
        else:
            st.error("❌ 无法获取公网IP，请检查网络连接")
    
    # 添加一些说明
    with st.expander("ℹ️ 关于此工具"):
        st.write("""
        这个工具会查询多个IP服务来获取您的公网IP地址：
        - httpbin.org
        - api.ipify.org  
        - jsonip.com
        - api.myip.com
        
        如果一个服务失败，会自动尝试下一个服务。
        """)

if __name__ == "__main__":
    main()
