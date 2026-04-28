#!/usr/bin/env python3
"""
HIJACKER - Automated Reconnaissance & Broken Link Hijacking Framework
Developed by: Padrivo | Version: 1.0 - Stable
"""

import os
import sys
import json
import re
import shutil
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
except ImportError:
    os.system("pip install colorama tqdm --break-system-packages -q")
    from colorama import Fore, Back, Style, init
    init(autoreset=True)

try:
    from tqdm import tqdm
except ImportError:
    os.system("pip install tqdm --break-system-packages -q")
    from tqdm import tqdm

# ─── GLOBAL CONFIG ────────────────────────────────────────────────────────────

PASSIVE_TOOLS  = ["amass", "subfinder", "assetfinder", "findomain"]
ACTIVE_TOOLS   = ["puredns", "massdns", "gobuster", "shuffledns"]
CRAWLER_TOOLS  = ["waybackurls", "gau", "katana", "hakrawler"]
ALL_TOOLS      = PASSIVE_TOOLS + ACTIVE_TOOLS + CRAWLER_TOOLS

PLATFORM_PATTERNS = {
    "github":    r"https?://(www\.)?github\.com/[A-Za-z0-9_.-]+/?$",
    "gitlab":    r"https?://(www\.)?gitlab\.com/[A-Za-z0-9_.-]+/?$",
    "bitbucket": r"https?://(www\.)?bitbucket\.org/[A-Za-z0-9_.-]+/?$",
    "dockerhub": r"https?://(www\.)?hub\.docker\.com/(u|r)/[A-Za-z0-9_.-]+",
    "npm":       r"https?://(www\.)?npmjs\.com/(package|~)/[A-Za-z0-9_.-]+",
    "twitter":   r"https?://(www\.)?(twitter|x)\.com/[A-Za-z0-9_]+/?$",
    "facebook":  r"https?://(www\.)?facebook\.com/[A-Za-z0-9_./-]+/?$",
    "instagram": r"https?://(www\.)?instagram\.com/[A-Za-z0-9_.]+/?$",
    "linkedin":  r"https?://(www\.)?linkedin\.com/(in|company)/[A-Za-z0-9_.-]+",
    "youtube":   r"https?://(www\.)?youtube\.com/(channel|user|c)/[A-Za-z0-9_-]+",
    "tiktok":    r"https?://(www\.)?tiktok\.com/@[A-Za-z0-9_.]+",
    "medium":    r"https?://(www\.)?medium\.com/@?[A-Za-z0-9_.-]+",
    "reddit":    r"https?://(www\.)?reddit\.com/(r|u)/[A-Za-z0-9_]+",
    "tumblr":    r"https?://[A-Za-z0-9_-]+\.tumblr\.com/?$",
    "pinterest": r"https?://(www\.)?pinterest\.com/[A-Za-z0-9_.-]+",
    "quora":     r"https?://(www\.)?quora\.com/profile/[A-Za-z0-9_-]+",
    "behance":   r"https?://(www\.)?behance\.net/[A-Za-z0-9_.-]+",
    "dribbble":  r"https?://(www\.)?dribbble\.com/[A-Za-z0-9_.-]+",
    "flickr":    r"https?://(www\.)?flickr\.com/(photos|people)/[A-Za-z0-9@_.-]+",
    "vimeo":     r"https?://(www\.)?vimeo\.com/[A-Za-z0-9_-]+",
    "discord":   r"https?://(www\.)?discord\.(gg|com/invite)/[A-Za-z0-9_-]+",
    "telegram":  r"https?://(www\.)?t\.me/[A-Za-z0-9_]+",
    "slack":     r"https?://[A-Za-z0-9_-]+\.slack\.com/?",
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def banner():
    print(Fore.CYAN + r"""
    __  ______    _____    ________ __ __________ 
   / / / /  /    / /   | / ____/ //_// ____/ __ \
  / /_/ // /__  / / /| |/ /   / ,<  / __/ / /_/ /
 / __  // // /_/ / ___ / /___/ /| |/ /___/ _, _/ 
/_/ /_/___/\____/_/  |_\____/_/ |_/_____/_/ |_|  
                                                  
          [ Developed by: Padrivo ]
          [ Version: 1.0 - Stable ]
""" + Style.RESET_ALL)

def c(color, msg):
    colors = {
        "red":    Fore.RED,
        "green":  Fore.GREEN,
        "yellow": Fore.YELLOW,
        "cyan":   Fore.CYAN,
        "blue":   Fore.BLUE,
        "white":  Fore.WHITE,
        "magenta":Fore.MAGENTA,
    }
    print(colors.get(color, Fore.WHITE) + msg + Style.RESET_ALL)

def section(title):
    print()
    print(Fore.CYAN + "─" * 60)
    print(Fore.CYAN + f"  ▶  {title}")
    print(Fore.CYAN + "─" * 60 + Style.RESET_ALL)

def run_cmd(cmd, timeout=300):
    """Run shell command, return (stdout, stderr, returncode)"""
    try:
        proc = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return proc.stdout.strip(), proc.stderr.strip(), proc.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout expired", 1
    except Exception as e:
        return "", str(e), 1

def save_lines(path, lines):
    """Append unique lines to a file"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = set(path.read_text().splitlines()) if path.exists() else set()
    new_lines = set(lines) - existing
    if new_lines:
        with open(path, "a") as f:
            f.write("\n".join(sorted(new_lines)) + "\n")
    return len(new_lines)

def load_lines(path):
    p = Path(path)
    if not p.exists():
        return []
    return [l.strip() for l in p.read_text().splitlines() if l.strip()]

# ─── DEPENDENCY CHECK ─────────────────────────────────────────────────────────

def check_tools():
    section("Tool Dependency Check")
    available = {}
    missing   = []

    for tool in ALL_TOOLS:
        if shutil.which(tool):
            c("green", f"  [✔] {tool} found")
            available[tool] = True
        else:
            c("red", f"  [!] Tool {tool} is missing.")
            available[tool] = False
            missing.append(tool)

    skip_missing = set()
    for tool in missing:
        ans = input(Fore.YELLOW + f"  Do you want to continue without {tool}? (y/n): " + Style.RESET_ALL).strip().lower()
        if ans == "y":
            skip_missing.add(tool)
        else:
            c("red", "Aborting.")
            sys.exit(1)

    return {t: v for t, v in available.items() if v or t in skip_missing}

# ─── SESSION MANAGER ──────────────────────────────────────────────────────────

class Session:
    def __init__(self, outdir, target):
        self.path   = Path(outdir) / "session.json"
        self.target = target
        self.data   = {
            "target":    target,
            "created":   datetime.now().isoformat(),
            "stage":     0,
            "subdomains":[],
            "sub_subs":  [],
            "urls":      [],
        }

    def load(self):
        if self.path.exists():
            with open(self.path) as f:
                saved = json.load(f)
            if saved.get("target") == self.target:
                return saved
        return None

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    def update(self, key, value):
        self.data[key] = value
        self.save()

    def set_stage(self, stage):
        self.data["stage"] = stage
        self.save()

# ─── STAGE 1: SUBDOMAIN DISCOVERY ─────────────────────────────────────────────

def run_passive(domain, outdir, wordlist, threads, available):
    subs = set()
    sub_file = Path(outdir) / "subs_passive.txt"

    def _amass():
        out, _, _ = run_cmd(f"amass enum -passive -d {domain} -o /tmp/amass_{domain}.txt", timeout=120)
        lines = load_lines(f"/tmp/amass_{domain}.txt")
        return lines

    def _subfinder():
        out, _, _ = run_cmd(f"subfinder -d {domain} -silent -o /tmp/sf_{domain}.txt", timeout=120)
        return load_lines(f"/tmp/sf_{domain}.txt")

    def _assetfinder():
        out, _, _ = run_cmd(f"assetfinder --subs-only {domain}", timeout=60)
        return [l for l in out.splitlines() if l.strip()]

    def _findomain():
        out, _, _ = run_cmd(f"findomain -t {domain} -q", timeout=60)
        return [l for l in out.splitlines() if l.strip()]

    runners = {
        "amass":       _amass,
        "subfinder":   _subfinder,
        "assetfinder": _assetfinder,
        "findomain":   _findomain,
    }

    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(fn): name for name, fn in runners.items() if available.get(name)}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="  Passive", unit="tool", colour="cyan"):
            name = futures[fut]
            try:
                results = fut.result()
                subs.update(results)
                c("green", f"  [+] {name}: {len(results)} subdomains")
            except Exception as e:
                c("red", f"  [!] {name} error: {e}")

    return list(subs)


def run_active(domain, outdir, wordlist, resolvers, threads, available):
    subs = set()

    # Build resolver flags per-tool
    r_shuffledns = f"-r {resolvers}" if resolvers and Path(resolvers).exists() else ""
    r_puredns    = f"--resolvers {resolvers}" if resolvers and Path(resolvers).exists() else ""

    def _gobuster():
        if not wordlist or not Path(wordlist).exists():
            return []
        out, _, _ = run_cmd(
            f"gobuster dns -d {domain} -w {wordlist} -t {threads} -q --no-error",
            timeout=300
        )
        results = []
        for line in out.splitlines():
            m = re.search(r"Found:\s+(\S+)", line)
            if m:
                results.append(m.group(1))
        return results

    def _shuffledns():
        if not wordlist or not Path(wordlist).exists():
            return []
        if not r_shuffledns:
            c("yellow", f"  [~] shuffledns skipped ({domain}) — resolvers file required")
            return []
        out, _, _ = run_cmd(
            f"shuffledns -d {domain} -w {wordlist} {r_shuffledns} -silent -o /tmp/sdns_{domain}.txt",
            timeout=300
        )
        return load_lines(f"/tmp/sdns_{domain}.txt")

    def _puredns():
        if not wordlist or not Path(wordlist).exists():
            return []
        out, _, _ = run_cmd(
            f"puredns bruteforce {wordlist} {domain} {r_puredns} -o /tmp/puredns_{domain}.txt",
            timeout=300
        )
        return load_lines(f"/tmp/puredns_{domain}.txt")

    runners = {
        "gobuster":   _gobuster,
        "shuffledns": _shuffledns,
        "puredns":    _puredns,
    }

    with ThreadPoolExecutor(max_workers=3) as ex:
        futures = {ex.submit(fn): name for name, fn in runners.items() if available.get(name)}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="  Active", unit="tool", colour="yellow"):
            name = futures[fut]
            try:
                results = fut.result()
                subs.update(results)
                c("green", f"  [+] {name}: {len(results)} subdomains")
            except Exception as e:
                c("red", f"  [!] {name} error: {e}")

    return list(subs)


def stage1_subdomain_discovery(targets, outdir, wordlist, resolvers, threads, available):
    section("Stage 1 — Subdomain Discovery")
    all_subs = set()

    for domain in tqdm(targets, desc="  Targets", unit="domain", colour="green"):
        domain_dir = Path(outdir) / domain
        domain_dir.mkdir(parents=True, exist_ok=True)

        passive = run_passive(domain, domain_dir, wordlist, threads, available)
        active  = run_active(domain, domain_dir, wordlist, resolvers, threads, available)

        combined = set(passive + active)
        combined.discard(domain)
        combined = {s for s in combined if domain in s}

        all_subs.update(combined)
        save_lines(domain_dir / "subdomains.txt", combined)
        c("cyan", f"  [→] {domain}: {len(combined)} unique subdomains")

    c("green", f"\n  [✔] Total subdomains: {len(all_subs)}")
    return list(all_subs)


# ─── STAGE 2: RECURSIVE ENUMERATION ──────────────────────────────────────────

def stage2_recursive(subdomains, outdir, wordlist, resolvers, threads, available):
    section("Stage 2 — Recursive Sub-Subdomain Enumeration")
    sub_subs = set()

    def probe_sub(sub):
        found = set()
        # passive subfinder on sub
        out, _, _ = run_cmd(f"subfinder -d {sub} -silent", timeout=60)
        for line in out.splitlines():
            if line.strip() and sub in line:
                found.add(line.strip())

        # gobuster if wordlist available
        if wordlist and Path(wordlist).exists() and available.get("gobuster"):
            out2, _, _ = run_cmd(
                f"gobuster dns -d {sub} -w {wordlist} -t {threads} -q --no-error",
                timeout=120
            )
            for line in out2.splitlines():
                m = re.search(r"Found:\s+(\S+)", line)
                if m:
                    found.add(m.group(1))
        return found

    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = {ex.submit(probe_sub, sub): sub for sub in subdomains}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="  Recursion", unit="sub", colour="magenta"):
            sub = futures[fut]
            try:
                found = fut.result()
                if found:
                    sub_subs.update(found)
                    root = ".".join(sub.split(".")[-2:])
                    save_lines(Path(outdir) / root / "sub_subs.txt", found)
            except Exception as e:
                c("red", f"  [!] Error on {sub}: {e}")

    c("green", f"\n  [✔] Total sub-subdomains found: {len(sub_subs)}")
    return list(sub_subs)


# ─── STAGE 3: URL EXTRACTION (CRAWLING) ───────────────────────────────────────

def crawl_domain(domain, available, threads):
    urls = set()

    def _waybackurls():
        out, _, _ = run_cmd(f"echo {domain} | waybackurls", timeout=120)
        return out.splitlines()

    def _gau():
        out, _, _ = run_cmd(f"echo {domain} | gau --subs", timeout=120)
        return out.splitlines()

    def _katana():
        out, _, _ = run_cmd(f"katana -u https://{domain} -silent -d 3", timeout=120)
        return out.splitlines()

    def _hakrawler():
        out, _, _ = run_cmd(f"echo https://{domain} | hakrawler -subs", timeout=60)
        return out.splitlines()

    runners = {
        "waybackurls": _waybackurls,
        "gau":         _gau,
        "katana":      _katana,
        "hakrawler":   _hakrawler,
    }

    for name, fn in runners.items():
        if available.get(name):
            try:
                results = fn()
                urls.update([u.strip() for u in results if u.strip()])
            except Exception as e:
                pass

    return list(urls)


def stage3_url_extraction(all_domains, outdir, available, threads):
    section("Stage 3 — URL Extraction (Crawling)")
    all_urls = []
    lock = threading.Lock()

    def crawl_and_save(domain):
        urls = crawl_domain(domain, available, threads)
        root = ".".join(domain.split(".")[-2:])
        if urls:
            save_lines(Path(outdir) / root / "urls.txt", urls)
        with lock:
            all_urls.extend(urls)
        return len(urls)

    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = {ex.submit(crawl_and_save, d): d for d in all_domains}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="  Crawling", unit="domain", colour="blue"):
            domain = futures[fut]
            try:
                count = fut.result()
                if count:
                    c("green", f"  [+] {domain}: {count} URLs")
            except Exception as e:
                c("red", f"  [!] Crawl error {domain}: {e}")

    c("green", f"\n  [✔] Total URLs collected: {len(all_urls)}")
    return all_urls


# ─── STAGE 4: INTELLIGENT FILTERING ──────────────────────────────────────────

def stage4_filter(urls, outdir):
    section("Stage 4 — Broken Link Hijacking Filter")

    results = {platform: set() for platform in PLATFORM_PATTERNS}
    compiled = {p: re.compile(pat, re.IGNORECASE) for p, pat in PLATFORM_PATTERNS.items()}

    for url in tqdm(urls, desc="  Filtering", unit="url", colour="yellow"):
        for platform, regex in compiled.items():
            if regex.search(url):
                results[platform].add(url)

    # Save per-platform
    links_dir = Path(outdir) / "broken_links"
    links_dir.mkdir(parents=True, exist_ok=True)

    total_found = 0
    for platform, links in results.items():
        if links:
            out_file = links_dir / f"{platform}_links.txt"
            save_lines(out_file, links)
            c("yellow", f"  [🎯] {platform:12s}: {len(links)} potential broken links → {out_file}")
            total_found += len(links)

    c("green", f"\n  [✔] Total potential broken links: {total_found}")
    return results


# ─── MAIN SETUP + ORCHESTRATION ───────────────────────────────────────────────

def get_inputs():
    section("Interactive Setup")

    # Target(s)
    target_input = input(Fore.CYAN + "  [?] Enter target domain OR path to domains file: " + Style.RESET_ALL).strip()
    if os.path.isfile(target_input):
        targets = [l.strip() for l in open(target_input) if l.strip()]
        c("green", f"  [✔] Loaded {len(targets)} targets from file")
    else:
        targets = [target_input]
        c("green", f"  [✔] Single target: {target_input}")

    # Wordlist (bruteforce subdomains list)
    wordlist = input(Fore.CYAN + "  [?] Bruteforce wordlist path (e.g. subdomains.txt — leave blank to skip): " + Style.RESET_ALL).strip()
    if wordlist and not os.path.exists(wordlist):
        c("yellow", "  [!] Wordlist not found — active bruteforce will be skipped.")
        wordlist = None
    elif wordlist:
        c("green", f"  [✔] Wordlist: {wordlist}")
    else:
        c("yellow", "  [~] No wordlist — active bruteforce disabled.")

    # Resolvers list
    resolvers = input(Fore.CYAN + "  [?] Resolvers list path (e.g. resolvers.txt — leave blank to use tool defaults): " + Style.RESET_ALL).strip()
    if resolvers and not os.path.exists(resolvers):
        c("yellow", "  [!] Resolvers file not found — tools will use their built-in defaults.")
        resolvers = None
    elif resolvers:
        c("green", f"  [✔] Resolvers: {resolvers}")
    else:
        c("yellow", "  [~] No resolvers file — tools will use built-in defaults.")

    # Threads
    threads_input = input(Fore.CYAN + "  [?] Number of threads [Default: 10]: " + Style.RESET_ALL).strip()
    threads = int(threads_input) if threads_input.isdigit() else 10
    c("green", f"  [✔] Threads: {threads}")

    return targets, wordlist, resolvers, threads


def print_summary(outdir, subdomains, sub_subs, broken_links):
    section("Final Summary")
    total_subs    = len(subdomains)
    total_subsubs = len(sub_subs)
    total_broken  = sum(len(v) for v in broken_links.values())

    c("cyan",  f"  📁  Output directory : {outdir}")
    c("green", f"  🌐  Subdomains found  : {total_subs}")
    c("green", f"  🔍  Sub-subdomains    : {total_subsubs}")
    c("yellow",f"  🎯  Broken link hits  : {total_broken}")

    if total_broken:
        c("magenta", "\n  Top platforms with hits:")
        sorted_platforms = sorted(broken_links.items(), key=lambda x: len(x[1]), reverse=True)
        for platform, links in sorted_platforms[:10]:
            if links:
                print(Fore.YELLOW + f"    ├─ {platform:12s}: {len(links)}" + Style.RESET_ALL)

    c("green", "\n  [✔] HIJACKER completed successfully!\n")


def main():
    banner()

    targets, wordlist, resolvers, threads = get_inputs()
    available = check_tools()

    # Setup output dir based on first target
    primary_target = targets[0].replace("http://", "").replace("https://", "").rstrip("/")
    outdir = Path(f"hijacker_{primary_target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    outdir.mkdir(parents=True, exist_ok=True)

    # Session handling
    session = Session(outdir, primary_target)
    saved   = session.load()
    resume_stage = 0

    if saved:
        ans = input(Fore.YELLOW + "\n  [?] Existing session found. Resume from last step? (y/n): " + Style.RESET_ALL).strip().lower()
        if ans == "y":
            session.data = saved
            resume_stage = saved.get("stage", 0)
            c("green", f"  [✔] Resuming from stage {resume_stage}")

    # ── Stage 1
    if resume_stage < 1:
        subdomains = stage1_subdomain_discovery(targets, outdir, wordlist, resolvers, threads, available)
        session.update("subdomains", subdomains)
        session.set_stage(1)
    else:
        subdomains = session.data.get("subdomains", [])
        c("cyan", f"  [→] Loaded {len(subdomains)} subdomains from session")

    # ── Stage 2
    if resume_stage < 2:
        sub_subs = stage2_recursive(subdomains, outdir, wordlist, resolvers, threads, available)
        session.update("sub_subs", sub_subs)
        session.set_stage(2)
    else:
        sub_subs = session.data.get("sub_subs", [])
        c("cyan", f"  [→] Loaded {len(sub_subs)} sub-subdomains from session")

    # ── Stage 3
    all_domains = targets + subdomains + sub_subs
    all_domains = list(set(
        d.replace("http://", "").replace("https://", "").rstrip("/")
        for d in all_domains if d
    ))

    if resume_stage < 3:
        urls = stage3_url_extraction(all_domains, outdir, available, threads)
        session.update("urls", urls)
        session.set_stage(3)
    else:
        urls = session.data.get("urls", [])
        c("cyan", f"  [→] Loaded {len(urls)} URLs from session")

    # ── Stage 4
    if resume_stage < 4:
        broken_links = stage4_filter(urls, outdir)
        session.set_stage(4)
    else:
        c("cyan", "  [→] Stage 4 already completed in previous session. Re-running filter...")
        broken_links = stage4_filter(urls, outdir)

    # ── Summary
    print_summary(outdir, subdomains, sub_subs, broken_links)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n  [!] Interrupted by user. Session saved.\n" + Style.RESET_ALL)
        sys.exit(0)
