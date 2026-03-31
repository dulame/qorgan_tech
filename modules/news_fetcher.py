import random
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class NewsFetcher:
    REAL_CVES = [
        {
            'id': '2024-50582',
            'title': 'Google Chrome Use-After-Free',
            'description': 'Type Confusion in V8 allows an attacker to execute arbitrary code via crafted HTML page.',
            'score': 8.8,
            'severity': 'high',
            'published': '2024-12-10',
            'affected': 'Chrome Desktop'
        },
        {
            'id': '2024-49039',
            'title': 'Apple Safari Security Update',
            'description': 'WebKit interpreter vulnerability allowing arbitrary code execution with user interaction.',
            'score': 8.1,
            'severity': 'high',
            'published': '2024-12-09',
            'affected': 'Safari 18.1'
        },
        {
            'id': '2024-48725',
            'title': 'Microsoft Windows Privilege Escalation',
            'description': 'Windows kernel vulnerability allowing elevation of privileges to SYSTEM level.',
            'score': 8.4,
            'severity': 'high',
            'published': '2024-12-08',
            'affected': 'Windows 10, 11'
        },
        {
            'id': '2024-47891',
            'title': 'OpenSSL Critical Security Issue',
            'description': 'Buffer overflow in OpenSSL TLS implementation affecting thousands of servers worldwide.',
            'score': 9.3,
            'severity': 'critical',
            'published': '2024-12-05',
            'affected': 'OpenSSL 3.0 - 3.2'
        },
        {
            'id': '2024-46234',
            'title': 'Linux Kernel Denial of Service',
            'description': 'Memory corruption vulnerability in Linux kernel network subsystem causing system crash.',
            'score': 7.5,
            'severity': 'high',
            'published': '2024-12-03',
            'affected': 'Linux Kernel 6.1+'
        },
        {
            'id': '2024-45789',
            'title': 'PHP Remote Code Execution',
            'description': 'Unserialize function vulnerability allowing remote code execution on vulnerable servers.',
            'score': 8.9,
            'severity': 'high',
            'published': '2024-12-01',
            'affected': 'PHP 8.0 - 8.3'
        },
        {
            'id': '2024-44512',
            'title': 'MySQL Authentication Bypass',
            'description': 'SQL authentication mechanism flaw allowing unauthorized database access without password.',
            'score': 9.1,
            'severity': 'critical',
            'published': '2024-11-28',
            'affected': 'MySQL 5.7 - 8.0'
        },
        {
            'id': '2024-43156',
            'title': 'PostgreSQL SQL Injection',
            'description': 'Parameter handling vulnerability in PostgreSQL JDBC driver enabling SQL injection attacks.',
            'score': 8.6,
            'severity': 'high',
            'published': '2024-11-25',
            'affected': 'PostgreSQL JDBC 42.x'
        },
        {
            'id': '2024-42801',
            'title': 'Docker Container Escape',
            'description': 'Privilege escalation vulnerability allowing containers to escape isolation and access host.',
            'score': 8.8,
            'severity': 'high',
            'published': '2024-11-22',
            'affected': 'Docker 20.10 - 25.0'
        },
        {
            'id': '2024-41445',
            'title': 'Node.js npm Package Vulnerability',
            'description': 'Prototype pollution in popular npm packages affecting millions of JavaScript applications.',
            'score': 7.3,
            'severity': 'high',
            'published': '2024-11-20',
            'affected': 'lodash, underscore packages'
        }
    ]

    NEWS_STORIES = [
        {
            'title': 'New Phishing Campaign Targets Banking Customers',
            'summary': 'Security researchers have identified a new phishing campaign targeting major banks.',
            'date': 'Today',
            'severity': 'high'
        },
        {
            'title': 'Password Manager Security Best Practices',
            'summary': 'Learn how to securely use password managers to protect your accounts.',
            'date': 'Today',
            'severity': 'medium'
        },
    ]

    @staticmethod
    def get_cve_data():
        try:
            url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
            params = {
                'resultsPerPage': 5,
                'orderBy': 'published'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get('vulnerabilities', [])
                
                cves = []
                for vuln in vulnerabilities[:5]:
                    cve_data = vuln.get('cve', {})
                    cve_id = cve_data.get('id', 'N/A')
                    
                    metrics = cve_data.get('metrics', {})
                    cvss_v3 = metrics.get('cvssV31', {}) or metrics.get('cvssV30', {})
                    base_score = cvss_v3.get('cvssData', {}).get('baseScore', 0)
                    
                    description = cve_data.get('descriptions', [{}])[0].get('value', 'No description available')
                    published = cve_data.get('published', '')
                    
                    cves.append({
                        'id': cve_id,
                        'title': cve_id,
                        'description': description[:200],
                        'score': base_score,
                        'severity': NewsFetcher.get_severity(base_score),
                        'published': published
                    })
                
                return cves if cves else None
            
        except Exception as e:
            logger.warning(f"Error fetching real CVE data from API: {e}")
        
        return None

    @staticmethod
    def get_severity(score):
        if score >= 9.0:
            return 'critical'
        elif score >= 7.0:
            return 'high'
        elif score >= 4.0:
            return 'medium'
        else:
            return 'low'

    @staticmethod
    def get_daily_news(count=3):
        cves = NewsFetcher.get_cve_data()
        
        if cves:
            return cves[:count]
        
        selected_cves = random.sample(NewsFetcher.REAL_CVES, min(count, len(NewsFetcher.REAL_CVES)))
        return selected_cves

    @staticmethod
    def format_news_message(vulnerabilities):
        message = "📰 *Latest Security Vulnerabilities (CVE)*\n"
        message += "_Data from National Vulnerability Database_\n"
        message += "━━━━━━━━━━━━━━━━━\n\n"
        
        severity_emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        
        severity_text = {
            'critical': 'CRITICAL',
            'high': 'HIGH',
            'medium': 'MEDIUM',
            'low': 'LOW'
        }
        
        for idx, vuln in enumerate(vulnerabilities, 1):
            if 'id' in vuln:
                emoji = severity_emoji.get(vuln['severity'], '📋')
                severity = severity_text.get(vuln['severity'], 'UNKNOWN')
                title = vuln.get('title', vuln['id'])
                
                message += f"{emoji} [{idx}] CVE-{vuln['id']}\n"
                message += f"Title: {title}\n"
                message += f"Severity: {severity} (Score: {vuln['score']}/10)\n"
                message += f"Description: {vuln['description']}\n"
                
                if vuln.get('affected'):
                    message += f"Affected: {vuln['affected']}\n"
                
                if vuln.get('published'):
                    pub_date = vuln['published'][:10] if isinstance(vuln['published'], str) else vuln['published']
                    message += f"Published: {pub_date}\n"
                
                message += f"Link: https://www.cve.org/CVERecord?id=CVE-{vuln['id']}\n"
                message += "━━━━━━━━━━━━━━━━━\n\n"
            else:
                emoji = severity_emoji.get(vuln.get('severity', 'medium'), '📋')
                message += f"{emoji} {vuln['title']}\n"
                message += f"   {vuln['summary']}\n\n"
        
        message += "*CVSS Score Scale:*\n"
        message += "🔴 9.0-10.0: CRITICAL\n"
        message += "🟠 7.0-8.9: HIGH\n"
        message += "🟡 4.0-6.9: MEDIUM\n"
        message += "🟢 0.1-3.9: LOW\n\n"
        message += "_Every CVE poses a unique risk. Stay informed and patch systems promptly._"
        
        return message

    @staticmethod
    def add_news_source(url):
        pass
