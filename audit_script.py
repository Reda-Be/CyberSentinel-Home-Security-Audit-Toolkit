import os
import platform
import subprocess
import socket
import datetime
import json

def run_command(command):
    """Executes a system command and returns the output."""
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return result.decode('utf-8', errors='ignore').strip()
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e.output.decode('utf-8', errors='ignore')}"

def get_system_info():
    """Retrieves basic system information."""
    return {
        "OS": platform.system(),
        "Release": platform.release(),
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Hostname": socket.gethostname(),
        "Processor": platform.processor()
    }

def translate_output(text):
    """Translates common Windows command output terms from French to English."""
    replacements = {
        "Paramètres Profil": "Profile Settings",
        "de domaine": "Domain",
        "privé": "Private",
        "public": "Public",
        "État": "State",
        "Actif": "Active",
        "Inactif": "Inactive",
        "comptes d'utilisateurs de": "User accounts for",
        "La commande s'est termine correctement": "The command completed successfully",
        "Carte Ethernet": "Ethernet Adapter",
        "Carte réseau sans fil": "Wireless LAN Adapter",
        "Carte Tunnel": "Tunnel Adapter",
        "Suffixe DNS propre à la connexion": "Connection-specific DNS Suffix",
        "Adresse physique": "Physical Address",
        "DHCP activé": "DHCP Enabled",
        "Oui": "Yes",
        "Non": "No",
        "Configuration automatique activée": "Auto-configuration Enabled",
        "Adresse IPv6 de liaison locale": "Link-local IPv6 Address",
        "Adresse IPv4": "IPv4 Address",
        "Masque de sous-réseau": "Subnet Mask",
        "Passerelle par défaut": "Default Gateway",
        "Média déconnecté": "Media disconnected",
        "Bail obtenu": "Lease Obtained",
        "Bail expirant": "Lease Expires",
        "Serveur DHCP": "DHCP Server",
        "Serveurs DNS": "DNS Servers",
        "AUTORITE NT\\Système": "NT AUTHORITY\\System",
        "Activé": "Enabled",
        "Désactivé": "Disabled",
        "préféré": "preferred",
        "août": "August", "avril": "April", "décembre": "December", "février": "February", # Basic months if needed
        "janvier": "January", "juillet": "July", "juin": "June", "mai": "May", 
        "mars": "March", "novembre": "November", "octobre": "October", "septembre": "September",
        "lundi": "Monday", "mardi": "Tuesday", "mercredi": "Wednesday", "jeudi": "Thursday", 
        "vendredi": "Friday", "samedi": "Saturday", "dimanche": "Sunday"
    }
    
    for fr, en in replacements.items():
        text = text.replace(fr, en)
    return text

def get_firewall_status():
    """Checks Windows Firewall status."""
    # Using netsh to check firewall
    output = run_command("netsh advfirewall show allprofiles state")
    return translate_output(output)

def get_antivirus_status():
    """Checks for Antivirus via WMI (Windows)."""
    # Using wmic to list antivirus products (may require admin rights)
    output = run_command("wmic /namespace:\\\\root\\SecurityCenter2 path AntiVirusProduct get displayName,productState /format:list")
    if not output.strip():
        return "No antivirus detected or access denied (try running as administrator)."
    return output

def get_user_accounts():
    """Lists local user accounts."""
    output = run_command("net user")
    return translate_output(output)

def get_windows_updates():
    """Retrieves the latest installed updates."""
    # Lists the last 10 hotfixes
    output = run_command("wmic qfe list brief /format:table")
    # Translate specific output if possible, though update descriptions are mixed
    output = translate_output(output)
    lines = output.split('\n')
    # Keep header and last 10 lines to avoid clutter
    if len(lines) > 15:
        return "\n".join(lines[:2] + lines[-10:])
    return output

def get_network_config():
    """Retrieves network configuration."""
    output = run_command("ipconfig /all")
    return translate_output(output)

def generate_html_report(data):
    """Generates a stylized HTML report."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Security Audit Report</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f9; color: #333; line-height: 1.6; }}
            .container {{ width: 80%; margin: auto; overflow: hidden; padding: 20px; background: #fff; box-shadow: 0 0 10px rgba(0,0,0,0.1); margin-top: 30px; border-radius: 8px; }}
            h1 {{ color: #2c3e50; text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #2980b9; border-left: 5px solid #3498db; padding-left: 10px; margin-top: 30px; }}
            pre {{ background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap; }}
            .info-item {{ margin-bottom: 10px; }}
            .footer {{ text-align: center; margin-top: 40px; font-size: 0.9em; color: #777; }}
            .status-ok {{ color: green; font-weight: bold; }}
            .status-warning {{ color: orange; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Security Audit Report</h1>
            <p><strong>Audit Date:</strong> {timestamp}</p>
            <p><strong>Machine:</strong> {data['System Info']['Hostname']}</p>

            <h2>1. System Information</h2>
            <div class="section">
                <ul>
    """
    
    for key, value in data['System Info'].items():
        html += f"<li><strong>{key}:</strong> {value}</li>"
    
    html += """
                </ul>
            </div>

            <h2>2. Firewall Status</h2>
            <div class="section">
                <pre>""" + data['Firewall'] + """</pre>
            </div>

            <h2>3. Antivirus Detected</h2>
            <div class="section">
                <pre>""" + data['Antivirus'] + """</pre>
            </div>

            <h2>4. User Accounts</h2>
            <div class="section">
                <pre>""" + data['Users'] + """</pre>
            </div>

            <h2>5. System Updates (Recent)</h2>
            <div class="section">
                <pre>""" + data['Updates'] + """</pre>
            </div>

            <h2>6. Network Configuration</h2>
            <div class="section">
                <pre>""" + data['Network'] + """</pre>
            </div>

            <div class="footer">
                <p>Generated by your Personal Security Audit Tool</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    filename = f"audit_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return filename

def main():
    print("Starting security audit...")
    
    data = {}
    
    print("- Collecting system info...")
    data['System Info'] = get_system_info()
    
    print("- Checking firewall...")
    data['Firewall'] = get_firewall_status()
    
    print("- Checking antivirus...")
    data['Antivirus'] = get_antivirus_status()
    
    print("- Analyzing user accounts...")
    data['Users'] = get_user_accounts()
    
    print("- Checking updates...")
    data['Updates'] = get_windows_updates()
    
    print("- Analyzing network...")
    data['Network'] = get_network_config()
    
    print("- Generating report...")
    report_file = generate_html_report(data)
    
    print(f"\nAudit complete! The report has been generated: {os.path.abspath(report_file)}")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
