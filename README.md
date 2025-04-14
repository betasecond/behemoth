# Behemoth

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![Security](https://img.shields.io/badge/Security-Testing-red)

A Docker Compose-based cybersecurity testing platform designed for educational purposes. Behemoth provides isolated environments for practicing common security techniques including password cracking and network sniffing.

<p align="center">
  <img src="docs/behemoth-logo.png" alt="Behemoth Logo" width="300"/>
</p>

## 🔒 Features

- **Isolated Testing Environments**: Secure Docker networks for controlled experimentation
- **Password Cracking Lab**: Simulated Windows NTLM hash cracking environment
- **Network Sniffing Lab**: Vulnerable FTP and Telnet services for protocol analysis
- **Integrated Logging**: Centralized logging with Grafana Loki
- **Automated Orchestration**: Python scripts to manage experiment workflows
- **Security-Focused Design**: Following container security best practices

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.6+
- Linux-based operating system (tested on Ubuntu 20.04+)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/behemoth.git
cd behemoth

# Set up the environment
python3 scripts/setup.py
```

## 📊 Usage

Behemoth organizes experiments into profiles that can be started independently:

### Password Cracking Lab

```bash
# Start the password cracking environment
python3 scripts/run_experiment.py crack cracking

# View results
python3 scripts/view_results.py crack
```

### Network Sniffing Lab

```bash
# Start the network sniffing environment
python3 scripts/run_experiment.py sniff sniffing

# Analyze captured traffic
python3 scripts/view_results.py sniff
```

### Teardown

```bash
# Stop and remove containers for a specific profile
python3 scripts/run_experiment.py down cracking

# Stop and remove all containers
python3 scripts/run_experiment.py down all
```

## 🏗️ Architecture

Behemoth uses a modular microservices architecture with isolated Docker networks:
