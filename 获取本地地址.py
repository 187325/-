import streamlit as st
import subprocess
import sys
import platform
import os
from datetime import datetime

def install_package(package):
    """自动安装缺失的包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_package(package_name, import_name=None):
    """检查并安装指定包"""
    if import_name is None:
        import_name = package_name
    
    try:
        return __import__(import_name)
    except ImportError:
        st.warning(f"正在安装 {package_name} 包...")
        if install_package(package_name):
            st.success(f"{package_name} 包安装成功！")
            return __import__(import_name)
        else:
            st.error(f"无法安装 {package_name} 包")
            return None

def check_and_install_requests():
    """检查并安装requests包"""
    return check_and_install_package("requests")

def check_and_install_psutil():
    """检查并安装psutil包"""
    return check_and_install_package("psutil")

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

def get_basic_system_info():
    """获取基本系统信息（不需要psutil）"""
    try:
        import socket
        
        basic_info = {
            "系统信息": {
                "操作系统": platform.system(),
                "系统版本": platform.version(),
                "架构": platform.machine(),
                "处理器": platform.processor() or "未知",
                "Python版本": platform.python_version(),
                "主机名": platform.node(),
                "当前进程PID": os.getpid(),
            },
            "环境信息": {
                "Python路径": sys.executable,
                "当前工作目录": os.getcwd(),
                "用户名": os.getenv('USER', '未知'),
                "HOME目录": os.getenv('HOME', '未知'),
            }
        }
        
        # 尝试获取一些网络信息
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            basic_info["网络信息"] = {
                "本地主机名": hostname,
                "本地IP": local_ip,
            }
        except:
            basic_info["网络信息"] = {"网络信息": "无法获取"}
        
        # 尝试获取一些环境变量
        env_info = {}
        important_vars = ['PATH', 'PYTHONPATH', 'STREAMLIT_SERVER_PORT', 'STREAMLIT_SERVER_ADDRESS']
        for var in important_vars:
            value = os.getenv(var)
            if value:
                # 如果值太长，截断显示
                if len(str(value)) > 100:
                    env_info[var] = str(value)[:100] + "..."
                else:
                    env_info[var] = str(value)
        
        if env_info:
            basic_info["环境变量"] = env_info
        
        return basic_info
        
    except Exception as e:
        st.error(f"获取基本系统信息时出错: {e}")
        return None
def get_system_info():
    """获取系统硬件信息"""
    # 首先尝试使用psutil获取详细信息
    psutil_module = check_and_install_psutil()
    
    if psutil_module:
        return get_detailed_system_info(psutil_module)
    else:
        st.warning("⚠️ 无法安装psutil包，将显示基本系统信息")
        return get_basic_system_info()

def get_detailed_system_info(psutil_module):
    """使用psutil获取详细系统信息"""
    try:
        # 基本系统信息
        system_info = {
            "系统": platform.system(),
            "系统版本": platform.version(),
            "架构": platform.machine(),
            "处理器": platform.processor(),
            "Python版本": platform.python_version(),
            "主机名": platform.node(),
        }
        
        # CPU信息
        cpu_info = {
            "CPU核心数": psutil_module.cpu_count(),
            "CPU逻辑核心数": psutil_module.cpu_count(logical=True),
            "CPU使用率": f"{psutil_module.cpu_percent(interval=1):.1f}%",
        }
        
        # 尝试获取CPU频率（某些环境可能不支持）
        try:
            cpu_freq = psutil_module.cpu_freq()
            if cpu_freq:
                cpu_info["CPU频率"] = f"{cpu_freq.current:.0f} MHz"
            else:
                cpu_info["CPU频率"] = "未知"
        except:
            cpu_info["CPU频率"] = "不支持"
        
        # 内存信息
        memory = psutil_module.virtual_memory()
        memory_info = {
            "总内存": f"{memory.total / (1024**3):.2f} GB",
            "已用内存": f"{memory.used / (1024**3):.2f} GB",
            "可用内存": f"{memory.available / (1024**3):.2f} GB",
            "内存使用率": f"{memory.percent:.1f}%",
        }
        
        # 磁盘信息
        try:
            disk = psutil_module.disk_usage('/')
            disk_info = {
                "总磁盘空间": f"{disk.total / (1024**3):.2f} GB",
                "已用磁盘空间": f"{disk.used / (1024**3):.2f} GB",
                "可用磁盘空间": f"{disk.free / (1024**3):.2f} GB",
                "磁盘使用率": f"{(disk.used / disk.total) * 100:.1f}%",
            }
        except:
            disk_info = {"磁盘信息": "无法获取"}
        
        # 网络信息
        try:
            network = psutil_module.net_io_counters()
            if network:
                network_info = {
                    "发送字节数": f"{network.bytes_sent / (1024**2):.2f} MB",
                    "接收字节数": f"{network.bytes_recv / (1024**2):.2f} MB",
                    "发送包数": f"{network.packets_sent:,}",
                    "接收包数": f"{network.packets_recv:,}",
                }
            else:
                network_info = {"网络信息": "无法获取"}
        except:
            network_info = {"网络信息": "无法获取"}
        
        # 进程信息
        try:
            process_info = {
                "运行进程数": len(psutil_module.pids()),
                "当前进程PID": os.getpid(),
            }
            
            # 尝试获取系统启动时间
            try:
                boot_time = psutil_module.boot_time()
                process_info["系统启动时间"] = datetime.fromtimestamp(boot_time).strftime("%Y-%m-%d %H:%M:%S")
            except:
                process_info["系统启动时间"] = "无法获取"
                
        except:
            process_info = {"进程信息": "无法获取"}
        
        return {
            "系统信息": system_info,
            "CPU信息": cpu_info,
            "内存信息": memory_info,
            "磁盘信息": disk_info,
            "网络信息": network_info,
            "进程信息": process_info,
        }
        
    except Exception as e:
        st.error(f"获取详细系统信息时出错: {e}")
        return get_basic_system_info()
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
    st.title("🌐 系统信息查询工具")
    st.write("查询公网IP地址和系统硬件配置信息")
    
    # 创建两个选项卡
    tab1, tab2 = st.tabs(["🌍 公网IP查询", "💻 硬件配置"])
    
    with tab1:
        st.header("公网IP地址查询")
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
        with st.expander("ℹ️ 关于IP查询"):
            st.write("""
            这个工具会查询多个IP服务来获取您的公网IP地址：
            - httpbin.org
            - api.ipify.org  
            - jsonip.com
            - api.myip.com
            
            如果一个服务失败，会自动尝试下一个服务。
            """)
    
    with tab2:
        st.header("系统硬件配置")
        st.write("查看当前系统的详细硬件配置信息")
        
        if st.button("获取硬件信息", type="primary", key="hardware"):
            with st.spinner("正在获取系统信息..."):
                system_info = get_system_info()
            
            if system_info:
                # 显示各类信息
                for category, info in system_info.items():
                    st.subheader(f"📊 {category}")
                    
                    # 创建两列布局
                    col1, col2 = st.columns(2)
                    
                    items = list(info.items())
                    mid_point = len(items) // 2
                    
                    with col1:
                        for key, value in items[:mid_point]:
                            st.metric(label=key, value=str(value))
                    
                    with col2:
                        for key, value in items[mid_point:]:
                            st.metric(label=key, value=str(value))
                    
                    st.divider()
                
                # 添加导出选项
                st.subheader("📥 导出信息")
                
                # 将信息格式化为文本
                export_text = f"系统信息报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                export_text += "=" * 50 + "\n\n"
                
                for category, info in system_info.items():
                    export_text += f"{category}:\n"
                    export_text += "-" * 20 + "\n"
                    for key, value in info.items():
                        export_text += f"{key}: {value}\n"
                    export_text += "\n"
                
                st.download_button(
                    label="📥 下载系统信息报告",
                    data=export_text,
                    file_name=f"system_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
                
            else:
                st.error("❌ 无法获取系统信息")
        
        with st.expander("ℹ️ 关于系统信息"):
            st.write("""
            这个工具会检测以下硬件和系统信息：
            
            **系统信息**: 操作系统、版本、架构等基本信息
            **CPU信息**: 处理器核心数、使用率、频率等
            **内存信息**: 总内存、已用内存、可用内存等
            **磁盘信息**: 磁盘空间使用情况
            **网络信息**: 网络流量统计
            **进程信息**: 系统进程和启动时间
            
            注意：在云端环境中，某些信息可能受到限制。
            """)

if __name__ == "__main__":
    main()
