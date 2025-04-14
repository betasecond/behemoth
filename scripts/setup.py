#!/usr/bin/env python3
import os
import subprocess
import logging
import sys
import venv
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get script directory and project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

def run_command(command, capture_output=True, cwd=PROJECT_ROOT):
    """Execute a shell command and log the output"""
    logger.info(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, text=True, 
                               capture_output=capture_output, cwd=cwd)
        if capture_output and result.stdout:
            logger.info(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        if capture_output and e.stderr:
            logger.error(f"Error: {e.stderr.strip()}")
        return False
    except FileNotFoundError as e:
        logger.error(f"Command not found: {e}")
        return False

def setup_venv():
    """Set up a Python virtual environment using uv"""
    venv_path = os.path.join(PROJECT_ROOT, "venv")
    
    # Check if uv is available
    has_uv = shutil.which("uv") is not None
    
    if has_uv:
        logger.info("Creating virtual environment with uv...")
        if not run_command(["uv", "venv", venv_path]):
            return False
        
        # Install required Python packages
        logger.info("Installing required Python packages...")
        requirements = ["pexpect"]  # Add any other Python requirements here
        
        # Find the Python executable in the virtual environment
        venv_python = os.path.join(venv_path, "bin", "python")
        if os.path.exists(venv_python):
            # Use the venv's Python to install packages
            if not run_command([venv_python, "-m", "pip", "install"] + requirements):
                return False
        else:
            logger.error(f"Virtual environment Python not found at {venv_python}")
            return False
    else:
        logger.error("uv command not found! Please install uv first.")
        return False
    
    logger.info(f"Virtual environment created at {venv_path}")
    logger.info(f"Activate with: source {venv_path}/bin/activate")
    return True

def prepare_data_directories():
    """Create and prepare data directories"""
    logger.info("Setting up data directories...")
    
    # Create sample hash file for password cracking
    crack_data_dir = os.path.join(PROJECT_ROOT, "data", "crack_data")
    os.makedirs(crack_data_dir, exist_ok=True)
    
    # Create a sample Windows NTLM hash file (password = 'password123')
    hash_file_path = os.path.join(crack_data_dir, "hashes.txt")
    with open(hash_file_path, "w") as f:
        f.write("testuser:1001:aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c:::\n")
    
    # Create a sample wordlist file
    wordlist_path = os.path.join(crack_data_dir, "wordlist.txt")
    with open(wordlist_path, "w") as f:
        f.write("password123\npassword\nadmin\n123456\nqwerty\n")
    
    # Create directory for network sniffing data
    sniff_data_dir = os.path.join(PROJECT_ROOT, "data", "sniff_data")
    os.makedirs(sniff_data_dir, exist_ok=True)
    
    logger.info("Data directories prepared successfully")
    return True

def create_architecture_doc():
    """Create architecture documentation with Mermaid diagram"""
    docs_dir = os.path.join(PROJECT_ROOT, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    
    arch_file_path = os.path.join(docs_dir, "architecture.md")
    with open(arch_file_path, "w") as f:
        f.write("""# Behemoth Architecture

## System Diagram

```mermaid
graph TD
    subgraph "实验平台架构"
        direction LR

        subgraph "宿主机/控制层"
            Python_Script["run_experiment.py"] -.->|控制 (docker-compose)| DC{Docker Compose}
            User[用户] --> Python_Script
        end

        subgraph "容器化环境 (通过 Docker Compose 管理)"
            DC -- up/down -- cracking_profile("密码破解 Profile")
            DC -- up/down -- sniffing_profile("网络嗅探 Profile")
            DC -- up/down -- Loki_Service["Loki 日志服务"]

            subgraph cracking_profile
                direction TB
                Cracker["Cracker (hashcat)"] -- R/W --> Crack_Data[(Crack Data Vol)]
                XP_Sim["XP Simulator"] -- R --> Crack_Data
                Cracker --> PW_Net{{"password_cracking_net (internal)"}}
                XP_Sim --> PW_Net
            end

            subgraph sniffing_profile
                direction TB
                Attacker["Attacker Client"] --> FTP["FTP Server"]
                Attacker --> Telnet["Telnet Server"]
                Sniffer["Sniffer (tshark)"] -- Captures --> Sniff_Net{{"sniffing_net (internal)"}}
                FTP --> Sniff_Net
                Telnet --> Sniff_Net
                Attacker --> Sniff_Net
                Sniffer -- W --> Sniff_Data[(Sniff Data Vol)]
            end

            Loki_Service <-- Logs --- Cracker
            Loki_Service <-- Logs --- XP_Sim
            Loki_Service <-- Logs --- FTP
            Loki_Service <-- Logs --- Telnet
            Loki_Service <-- Logs --- Sniffer
            Loki_Service <-- Logs --- Attacker
        end
    end

    classDef profile fill:#f9f,stroke:#333,stroke-width:2px;
    class cracking_profile,sniffing_profile profile;
```

## Component Details

### Password Cracking Environment
- **XP Simulator**: Simulates Windows XP hashes for cracking demonstration
- **Cracker**: Contains hashcat and dictionary files for password cracking

### Network Sniffing Environment
- **FTP Server**: Runs vulnerable FTP service
- **Telnet Server**: Runs vulnerable Telnet service
- **Sniffer**: Captures network traffic using tshark
- **Attacker Client**: Client for connecting to vulnerable services

### Logging
- **Loki**: Centralized logging service for all containers
""")
    
    logger.info(f"Created architecture documentation at {arch_file_path}")
    return True

def main():
    """Main setup function"""
    logger.info("Starting Behemoth setup...")
    
    # Check that we're running from the project directory
    if not os.path.isfile(os.path.join(PROJECT_ROOT, "docker-compose.yml")):
        logger.error("Please run this script from the project root directory")
        return False
    
    # Make run_experiment.py executable
    run_command(["chmod", "+x", os.path.join(BASE_DIR, "run_experiment.py")])
    
    # Setup virtual environment
    if not setup_venv():
        logger.error("Failed to set up virtual environment")
        return False
    
    # Prepare data directories
    if not prepare_data_directories():
        logger.error("Failed to prepare data directories")
        return False
    
    # Create architecture documentation
    if not create_architecture_doc():
        logger.warning("Failed to create architecture documentation")
    
    logger.info("Behemoth setup completed successfully!")
    logger.info("Run experiments with: python scripts/run_experiment.py [crack|sniff|down] [profile_name]")
    return True

if __name__ == "__main__":
    sys.exit(0 if main() else 1)