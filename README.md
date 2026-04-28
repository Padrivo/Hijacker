# 🚀 HIJACKER: The Ultimate Broken Link Hijacking Framework

**HIJACKER** is a powerful, interactive reconnaissance framework built in Python. It automates the process of finding "forgotten" or "broken" social media and technical platform links hidden within a target's infrastructure (Current & Archived).

Developed with a focus on **Bug Bounty Hunters** and **Red Teamers**, it combines sub-domain enumeration, deep crawling, and intelligent regex filtering into one seamless pipeline.

---

## 🎨 Visual Branding
Created and Maintained by: **Padrivo**

```text
    __  ______    _____    ________ __ __________ 
   / / / /  /    / /   | / ____/ //_// ____/ __ \
  / /_/ // /__  / / /| |/ /   / ,<  / __/ / /_/ /
 / __  // // /_/ / ___ / /___/ /| |/ /___/ _, _/ 
/_/ /_/___/\____/_/  |_\____/_/ |_/_____/_/ |_|  
                                                  
          [ Developed by: Padrivo ]
```

---

## 🛠 Features
- **Comprehensive Enumeration:** Combines Passive (Amass, Subfinder) and Active (PureDNS, Gobuster) techniques.
- **Recursive Discovery:** Automatically scans for sub-subdomains to expand the attack surface.
- **Deep Archive Crawling:** Pulls historical URLs from Wayback Machine and GAU.
- **Live Analysis:** Real-time crawling using Katana and Hakrawler.
- **Smart Filtering:** Uses optimized Regex to identify 20+ platforms (Social, Dev, Blogs, Chat).
- **Session Persistence:** Save and resume your progress anytime via `session.json`.
- **Organized Output:** Results are sorted into clean directories and platform-specific files.

---

## 🏗 Workflow Pipeline
1. **Input:** Accept single domain or bulk list.
2. **Recon:** Horizontal & Vertical subdomain discovery.
3. **Extraction:** Fetching all URLs from live and archived sources.
4. **Regex Filter:** Identifying potential hijackable links.
5. **Report:** Categorizing links by platform for final verification.

---

## 🚀 Installation & Prerequisites

Ensure you have the following tools installed and added to your `PATH`:
- **Subdomains:** `amass`, `subfinder`, `assetfinder`, `findomain`, `puredns`, `massdns`, `gobuster`, `shuffledns`.
- **Crawling:** `waybackurls`, `gau`, `katana`, `hakrawler`.

### Python Dependencies
```bash
pip install colorama tqdm requests
```

---

## 💻 Usage
Run the tool interactively:
```bash
python3 hijacker.py
```
The tool will prompt you for:
1. Target Domain or List Path.
2. DNS Wordlist Path (for Active Discovery).
3. Number of Threads (Speed).

---

## 📊 Supported Platforms
- **Social:** Twitter, Facebook, Instagram, LinkedIn, YouTube, TikTok.
- **Tech:** GitHub, GitLab, Bitbucket, DockerHub, NPM.
- **Blogs:** Medium, Reddit, Tumblr, Pinterest, Quora.
- **Chat:** Discord, Telegram, Slack.
- **Creative:** Behance, Dribbble, Flickr, Vimeo.

---
