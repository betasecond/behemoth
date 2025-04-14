#!/usr/bin/env python3
import subprocess
import logging
import sys
import os

# 配置宿主机脚本的日志记录 (输出到控制台)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - HOST_SCRIPT - %(message)s')

# 脚本所在的目录，用于定位 docker-compose.yml 等
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR) # 项目根目录

def run_command(command, capture_output=False, cwd=PROJECT_ROOT):
    """执行shell命令并记录日志"""
    logging.info(f"Executing command: {' '.join(command)} in {cwd}")
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=capture_output, cwd=cwd, errors='ignore')
        if capture_output and result.stdout:
            logging.info(f"Command stdout:\n{result.stdout.strip()}")
        if capture_output and result.stderr:
            logging.warning(f"Command stderr:\n{result.stderr.strip()}")
        return result.stdout if capture_output else True
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {' '.join(command)}\nError: {e}")
        if capture_output:
            logging.error(f"Stderr:\n{e.stderr}")
        return None

def manage_environment(profile, action="up"):
    """管理Docker Compose环境 (up/down)"""
    cmd = ["docker-compose"]
    if profile:
        cmd.extend(["--profile", profile])
    if action == "up":
        cmd.extend(["up", "-d", "--build", "--remove-orphans"])
    elif action == "down":
        cmd.extend(["down", "-v"])
    else:
        logging.error(f"Invalid action: {action}")
        return False
    return run_command(cmd)

def run_crack():
    """执行密码破解实验并解析结果"""
    logging.info("Starting password cracking experiment...")
    hash_file = "/data/hashes.txt" # 假设的哈希文件名
    wordlist = "/data/wordlist.txt" # 假设的字典文件名

    # 在cracker容器内执行hashcat
    crack_cmd = [
        "docker", "exec", "cracker_tool",
        "hashcat", "-m", "1000", hash_file, wordlist, "--potfile-disable", "--show" # 使用 --show 获取已破解结果
    ]
    output = run_command(crack_cmd, capture_output=True)

    if output:
        logging.info("Hashcat execution finished. Parsing results...")
        cracked = False
        for line in output.strip().split('\n'):
            if ":" in line and not line.startswith("Session") and not line.startswith("Status"): # 简易判断是否为破解结果行
                logging.info(f"Cracked Hash/Password found: {line}")
                cracked = True
        if not cracked:
            logging.info("No passwords cracked or already shown in previous runs.")
    else:
        logging.error("Password cracking command failed to execute.")

def run_sniff():
    """执行网络嗅探实验并解析结果"""
    logging.info("Starting network sniffing experiment...")
    pcap_file = "/pcap/sniff.pcap"
    filter_exp = "tcp port 21 or tcp port 23"

    # 启动 tshark 抓包 (后台)
    tshark_start_cmd = [
        "docker", "exec", "-d", "sniffer_tool",
        "tshark", "-i", "eth0", "-w", pcap_file, "-f", filter_exp
    ]
    if not run_command(tshark_start_cmd):
        logging.error("Failed to start tshark.")
        return
    logging.info("tshark started capturing.")

    # 执行 FTP/Telnet 操作 (简化示例，实际可能需要更可靠的交互方式如pexpect)
    try:
        run_command(["docker", "exec", "attacker_node", "sh", "-c", "sleep 2 && echo -e 'user testuser\\npass testpass\\nquit' | ftp ftp_service"], capture_output=True)
        logging.info("FTP interaction performed.")
        run_command(["docker", "exec", "attacker_node", "sh", "-c", "sleep 2 && echo -e 'testuser\\ntestpass\\nls\\nexit' | telnet telnet_service"], capture_output=True)
        logging.info("Telnet interaction performed.")
    except Exception as e:
        logging.warning(f"Client interaction might have failed: {e}")

    # 停止 tshark (通过停止容器)
    run_command(["docker", "stop", "sniffer_tool"])
    logging.info("tshark stopped.")
    
    # 重启 sniffer 容器以便后续使用
    run_command(["docker", "start", "sniffer_tool"])
    
    # 分析 pcap 文件提取凭据信息
    logging.info("Analyzing captured pcap file...")
    analysis_cmd = [
        "docker", "exec", "sniffer_tool",
        "tshark", "-r", pcap_file,
        "-Y", "ftp.request.command == USER or ftp.request.command == PASS or telnet.data",
        "-T", "fields", "-e", "frame.number", "-e", "ftp.request.command", "-e", "ftp.request.arg", "-e", "telnet.data"
    ]
    
    analysis_output = run_command(analysis_cmd, capture_output=True)
    
    if analysis_output:
        logging.info(f"Sniffing analysis results (potential credentials):\n{analysis_output}")
        # TODO: Further parse the output for clear credential pairs
    else:
        logging.warning("Pcap analysis command failed or produced no output matching the filter.")
        logging.info(f"Check Loki logs or the pcap file at 'data/sniff_data/sniff.pcap' for plaintext credentials.")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ["crack", "sniff", "down"]:
        print("Usage: python run_experiment.py [crack|sniff|down] [profile_name]")
        print("Example: python run_experiment.py crack cracking")
        print("Example: python run_experiment.py sniff sniffing")
        print("Example: python run_experiment.py down cracking")
        sys.exit(1)

    command = sys.argv[1]
    profile = sys.argv[2] if len(sys.argv) > 2 else None
    
    if command == "down" and profile == "all":
        logging.info("Tearing down all environments...")
        manage_environment(None, action="down")
    elif command == "down":
        logging.info(f"Tearing down environment for profile '{profile}'...")
        manage_environment(profile, action="down")
    else:
        logging.info(f"Setting up environment for profile '{profile}'...")
        if manage_environment(profile, action="up"):
            if command == "crack":
                run_crack()
            elif command == "sniff":
                run_sniff()
            # 自动清理可选
            # logging.info(f"Cleaning up environment for profile '{profile}'...")
            # manage_environment(profile, action="down")
        else:
            logging.error("Environment setup failed.")

    logging.info("Script finished.")