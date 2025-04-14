#!/usr/bin/env python3
import os
import sys
import logging
import subprocess
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get script directory and project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

def run_command(command, capture_output=True, cwd=PROJECT_ROOT):
    """Execute a shell command and log the output"""
    logger.debug(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, text=True, 
                               capture_output=capture_output, cwd=cwd)
        return result.stdout if capture_output else True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        if capture_output and e.stderr:
            logger.error(f"Error: {e.stderr.strip()}")
        return None

def view_crack_results():
    """View the results of the password cracking experiments"""
    logger.info("Viewing password cracking results...")
    
    # Check if the cracker container is running
    check_cmd = ["docker", "ps", "--filter", "name=cracker_tool", "--format", "{{.Names}}"]
    output = run_command(check_cmd)
    
    if not output or "cracker_tool" not in output:
        logger.warning("Cracker container is not running. Starting it first...")
        logger.info("You may need to run 'python scripts/run_experiment.py crack cracking' first.")
        return
    
    # Get cracked hashes from hashcat
    crack_cmd = [
        "docker", "exec", "cracker_tool",
        "hashcat", "-m", "1000", "/data/hashes.txt", "/data/wordlist.txt", "--show"
    ]
    output = run_command(crack_cmd)
    
    if not output:
        logger.warning("No cracked passwords found or an error occurred.")
        return
    
    logger.info("\n=== Password Cracking Results ===")
    
    # Parse and display results in a clean format
    for line in output.strip().split("\n"):
        if ":" in line:
            parts = line.split(":")
            if len(parts) >= 4:
                username = parts[0]
                lm_hash = parts[2]
                ntlm_hash = parts[3]
                password = parts[4] if len(parts) > 4 else "<empty>"
                
                print(f"Username: {username}")
                print(f"NTLM Hash: {ntlm_hash}")
                print(f"Cracked Password: {password}")
                print("-" * 40)
            else:
                print(f"Raw result: {line}")
    
    # Get hash files in the volume
    logger.info("\nHash files available in data volume:")
    run_command(["docker", "exec", "cracker_tool", "ls", "-la", "/data"], 
               capture_output=False)

def view_sniff_results():
    """View the results of the network sniffing experiments"""
    logger.info("Viewing network sniffing results...")
    
    # Check if the sniffer container is running
    check_cmd = ["docker", "ps", "--filter", "name=sniffer_tool", "--format", "{{.Names}}"]
    output = run_command(check_cmd)
    
    if not output or "sniffer_tool" not in output:
        logger.warning("Sniffer container is not running. Start it first...")
        logger.info("You may need to run 'python scripts/run_experiment.py sniff sniffing' first.")
        return
    
    # List PCAP files in the volume
    logger.info("PCAP files available:")
    run_command(["docker", "exec", "sniffer_tool", "ls", "-la", "/pcap"], 
               capture_output=False)
    
    # Analyze FTP credentials in the PCAP
    logger.info("\n=== FTP Credentials in PCAP ===")
    ftp_cmd = [
        "docker", "exec", "sniffer_tool",
        "tshark", "-r", "/pcap/sniff.pcap", 
        "-Y", "ftp.request.command == \"USER\" || ftp.request.command == \"PASS\"",
        "-T", "fields", "-e", "ftp.request.command", "-e", "ftp.request.arg"
    ]
    
    ftp_output = run_command(ftp_cmd)
    if ftp_output:
        # Parse and display FTP credentials
        username = None
        for line in ftp_output.strip().split("\n"):
            if line:
                parts = line.split("\t")
                if len(parts) == 2:
                    cmd, arg = parts
                    if cmd == "USER":
                        username = arg
                        print(f"FTP Username: {username}")
                    elif cmd == "PASS" and username:
                        print(f"FTP Password: {arg}")
                        print(f"Complete FTP credentials captured: {username}:{arg}")
                        username = None
                        print("-" * 40)
    else:
        logger.warning("No FTP credentials found in the PCAP file.")
    
    # Analyze Telnet data in the PCAP
    logger.info("\n=== Telnet Data in PCAP ===")
    telnet_cmd = [
        "docker", "exec", "sniffer_tool",
        "tshark", "-r", "/pcap/sniff.pcap", 
        "-Y", "telnet.data",
        "-T", "fields", "-e", "frame.number", "-e", "telnet.data"
    ]
    
    telnet_output = run_command(telnet_cmd)
    if telnet_output:
        print("Telnet data packets:")
        for line in telnet_output.strip().split("\n"):
            if line:
                print(line)
        
        logger.info("\nNote: Telnet sends each character as a separate packet.")
        logger.info("Look for sequences that form usernames and passwords.")
    else:
        logger.warning("No telnet data found in the PCAP file.")
    
    # Provide instructions for further analysis
    logger.info("\n=== For detailed packet analysis ===")
    logger.info("You can run: docker exec -it sniffer_tool tshark -r /pcap/sniff.pcap")

def main():
    """Main function for viewing experiment results"""
    parser = argparse.ArgumentParser(description='View Behemoth experiment results')
    parser.add_argument('experiment', choices=['crack', 'sniff'], 
                        help='Experiment to view results for')
    
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    if args.experiment == 'crack':
        view_crack_results()
    elif args.experiment == 'sniff':
        view_sniff_results()

if __name__ == "__main__":
    main()