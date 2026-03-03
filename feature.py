import re
import socket
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

try:
    import whois as whois_lib
except ImportError:
    whois_lib = None

try:
    from googlesearch import search as google_search
except ImportError:
    google_search = None


SHORTENING_SERVICES = re.compile(
    r'bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
    r'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
    r'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
    r'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|lnkd\.in|'
    r'db\.tt|qr\.ae|adf\.ly|bitly\.com|cur\.lv|tinyurl\.com|ity\.im|'
    r'q\.gs|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|'
    r'prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|link\.zip\.net',
    re.IGNORECASE
)

PHISH_HINTS = [
    'login', 'signin', 'sign-in', 'log-in', 'verify', 'update', 'account',
    'secure', 'banking', 'confirm', 'password', 'credential', 'suspend',
    'authenticate', 'wallet', 'alert', 'notification', 'pay', 'billing',
    'invoice', 'transaction', 'refund', 'unlock', 'expire',
]

SUSPICIOUS_TLDS = {
    'zip', 'review', 'country', 'kim', 'cricket', 'science', 'work',
    'party', 'gq', 'link', 'ml', 'tk', 'ga', 'cf', 'top', 'xyz',
    'date', 'faith', 'win', 'accountant', 'racing', 'stream', 'download',
    'bid', 'loan', 'trade', 'men', 'click',
}

KNOWN_BRANDS = {
    'apple', 'google', 'facebook', 'amazon', 'microsoft', 'paypal',
    'netflix', 'instagram', 'twitter', 'linkedin', 'dropbox', 'yahoo',
    'chase', 'wellsfargo', 'bankofamerica', 'citibank', 'hsbc', 'usaa',
    'ebay', 'spotify', 'adobe', 'github', 'steam', 'whatsapp',
}

# Cache phishing URLs in memory once
_phish_hosts = None

def _load_phish_hosts():
    global _phish_hosts
    if _phish_hosts is not None:
        return _phish_hosts
    _phish_hosts = set()
    try:
        with open('DataFiles/phishurls.csv', 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        host = urlparse(line).hostname
                        if host:
                            _phish_hosts.add(host)
                    except Exception:
                        _phish_hosts.add(line)
    except Exception:
        pass
    return _phish_hosts


class FeatureExtraction:

    def __init__(self, url):
        self.url = url
        self.parsed = urlparse(url)
        self.hostname = self.parsed.hostname or ''
        self.path = self.parsed.path or ''
        self.scheme = self.parsed.scheme or ''
        self.domain = self._get_domain()
        self.tld = self._get_tld()

        self.response = None
        self.soup = None
        self.whois_data = None
        self._google_indexed = None
        self._dns_result = None

        # Run HTTP fetch, WHOIS, DNS, and Google index in parallel
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {
                pool.submit(self._fetch_page): 'page',
                pool.submit(self._fetch_whois): 'whois',
                pool.submit(self._check_dns): 'dns',
                pool.submit(self._check_google_index): 'google',
            }
            try:
                for future in as_completed(futures, timeout=20):
                    key = futures[future]
                    try:
                        result = future.result()
                        if key == 'page':
                            self.response, self.soup = result
                        elif key == 'whois':
                            self.whois_data = result
                        elif key == 'dns':
                            self._dns_result = result
                        elif key == 'google':
                            self._google_indexed = result
                    except Exception:
                        pass
            except TimeoutError:
                pass

        # Pre-compute cached content features
        self._cached_hyperlink_ratios = None
        self._cached_redirection_ratios = None
        self._cached_media_ratios = None

    def _fetch_page(self):
        try:
            resp = requests.get(self.url, timeout=10, allow_redirects=True,
                                headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(resp.text, 'html.parser')
            return resp, soup
        except Exception:
            return None, None

    def _fetch_whois(self):
        if not whois_lib:
            return None
        try:
            return whois_lib.whois(self.hostname)
        except Exception:
            return None

    def _check_dns(self):
        try:
            socket.gethostbyname(self.hostname)
            return 1
        except Exception:
            return 0

    def _check_google_index(self):
        if google_search:
            try:
                results = list(google_search(f'site:{self.url}', num_results=1))
                return 1 if results else 0
            except Exception:
                return 0
        return 0

    def _get_domain(self):
        parts = self.hostname.split('.')
        return parts[-2] if len(parts) >= 2 else self.hostname

    def _get_tld(self):
        parts = self.hostname.split('.')
        return parts[-1] if len(parts) >= 2 else ''

    def _get_words(self, text):
        words = [w for w in re.split(r'[.\-_/=?&@~%:]+', text) if w]
        return words if words else ['']

    # ===== URL STRING FEATURES =====

    def length_url(self):
        return len(self.url)

    def length_hostname(self):
        return len(self.hostname)

    def ip(self):
        if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', self.hostname):
            return 1
        if re.search(r'0x[\da-f]+', self.hostname, re.IGNORECASE):
            return 1
        return 0

    def nb_dots(self):
        return self.url.count('.')

    def nb_hyphens(self):
        return self.url.count('-')

    def nb_at(self):
        return self.url.count('@')

    def nb_qm(self):
        return self.url.count('?')

    def nb_and(self):
        return self.url.count('&')

    def nb_or(self):
        return self.url.count('|')

    def nb_eq(self):
        return self.url.count('=')

    def nb_underscore(self):
        return self.url.count('_')

    def nb_tilde(self):
        return self.url.count('~')

    def nb_percent(self):
        return self.url.count('%')

    def nb_slash(self):
        return self.url.count('/')

    def nb_star(self):
        return self.url.count('*')

    def nb_colon(self):
        return self.url.count(':')

    def nb_comma(self):
        return self.url.count(',')

    def nb_semicolumn(self):
        return self.url.count(';')

    def nb_dollar(self):
        return self.url.count('$')

    def nb_space(self):
        return self.url.count(' ') + self.url.count('%20')

    def nb_www(self):
        return self.url.lower().count('www')

    def nb_com(self):
        path_and_query = self.path + '?' + (self.parsed.query or '')
        return path_and_query.lower().count('com')

    def nb_dslash(self):
        after_protocol = self.url.split('://', 1)[-1] if '://' in self.url else self.url
        return after_protocol.count('//')

    def http_in_path(self):
        return 1 if 'http' in self.path.lower() else 0

    def https_token(self):
        if 'https' in self.hostname.lower():
            return 0
        return 1

    def ratio_digits_url(self):
        digits = sum(c.isdigit() for c in self.url)
        return round(digits / max(len(self.url), 1), 6)

    def ratio_digits_host(self):
        digits = sum(c.isdigit() for c in self.hostname)
        return round(digits / max(len(self.hostname), 1), 6)

    def punycode(self):
        return 1 if 'xn--' in self.url.lower() else 0

    def port(self):
        p = self.parsed.port
        return 1 if p and p not in (80, 443) else 0

    def tld_in_path(self):
        return 1 if self.tld and self.tld in self.path.lower() else 0

    def tld_in_subdomain(self):
        parts = self.hostname.split('.')
        if len(parts) > 2 and self.tld:
            subdomain = '.'.join(parts[:-2])
            if self.tld in subdomain:
                return 1
        return 0

    def abnormal_subdomain(self):
        return 1 if re.search(r'^www\..+\..+\..+', self.hostname) else 0

    def nb_subdomains(self):
        return len(self.hostname.split('.'))

    def prefix_suffix(self):
        return 1 if '-' in self.domain else 0

    def random_domain(self):
        consonants = set('bcdfghjklmnpqrstvwxyz')
        d = self.domain.lower()
        if len(d) < 4:
            return 0
        cons_streak = 0
        max_cons = 0
        for c in d:
            if c in consonants:
                cons_streak += 1
                max_cons = max(max_cons, cons_streak)
            else:
                cons_streak = 0
        return 1 if max_cons >= 4 else 0

    def shortening_service(self):
        return 1 if SHORTENING_SERVICES.search(self.url) else 0

    def path_extension(self):
        ext_match = re.search(r'\.\w+$', self.path)
        if ext_match:
            ext = ext_match.group().lower()
            if ext in ('.exe', '.zip', '.rar', '.7z', '.bat', '.cmd', '.scr', '.js'):
                return 1
        return 0

    # ===== WORD ANALYSIS FEATURES =====

    def length_words_raw(self):
        return len(self._get_words(self.url))

    def char_repeat(self):
        if not self.url:
            return 0
        max_repeat = 1
        current = 1
        for i in range(1, len(self.url)):
            if self.url[i] == self.url[i - 1]:
                current += 1
                max_repeat = max(max_repeat, current)
            else:
                current = 1
        return max_repeat

    def shortest_words_raw(self):
        words = self._get_words(self.url)
        return min(len(w) for w in words)

    def shortest_word_host(self):
        words = self._get_words(self.hostname)
        return min(len(w) for w in words)

    def shortest_word_path(self):
        words = self._get_words(self.path)
        return min(len(w) for w in words)

    def longest_words_raw(self):
        words = self._get_words(self.url)
        return max(len(w) for w in words)

    def longest_word_host(self):
        words = self._get_words(self.hostname)
        return max(len(w) for w in words)

    def longest_word_path(self):
        words = self._get_words(self.path)
        return max(len(w) for w in words)

    def avg_words_raw(self):
        words = self._get_words(self.url)
        return round(sum(len(w) for w in words) / max(len(words), 1), 6)

    def avg_word_host(self):
        words = self._get_words(self.hostname)
        return round(sum(len(w) for w in words) / max(len(words), 1), 6)

    def avg_word_path(self):
        words = self._get_words(self.path)
        return round(sum(len(w) for w in words) / max(len(words), 1), 6)

    def phish_hints(self):
        url_lower = self.url.lower()
        return sum(1 for hint in PHISH_HINTS if hint in url_lower)

    def domain_in_brand(self):
        return 1 if self.domain.lower() in KNOWN_BRANDS else 0

    def brand_in_subdomain(self):
        parts = self.hostname.split('.')
        if len(parts) > 2:
            subdomain = '.'.join(parts[:-2]).lower()
            for brand in KNOWN_BRANDS:
                if brand in subdomain:
                    return 1
        return 0

    def brand_in_path(self):
        path_lower = self.path.lower()
        for brand in KNOWN_BRANDS:
            if brand in path_lower:
                return 1
        return 0

    def suspecious_tld(self):
        return 1 if self.tld.lower() in SUSPICIOUS_TLDS else 0

    def statistical_report(self):
        hosts = _load_phish_hosts()
        return 1 if self.hostname in hosts else 0

    # ===== CONTENT FEATURES =====

    def nb_hyperlinks(self):
        if not self.soup:
            return 0
        return len(self.soup.find_all('a'))

    def _hyperlink_ratios(self):
        if self._cached_hyperlink_ratios is not None:
            return self._cached_hyperlink_ratios
        if not self.soup:
            self._cached_hyperlink_ratios = (0.0, 0.0, 0.0)
            return self._cached_hyperlink_ratios
        links = self.soup.find_all('a', href=True)
        total = len(links) if links else 1
        internal = external = null = 0
        for link in links:
            href = link['href']
            if href in ('', '#', 'javascript:void(0)', 'javascript:;'):
                null += 1
            elif self.hostname and self.hostname in href:
                internal += 1
            elif href.startswith('http'):
                external += 1
            else:
                internal += 1
        self._cached_hyperlink_ratios = (
            round(internal / total, 9),
            round(external / total, 9),
            round(null / total, 9)
        )
        return self._cached_hyperlink_ratios

    def nb_extCSS(self):
        if not self.soup:
            return 0
        count = 0
        for link in self.soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            if href.startswith('http') and self.hostname not in href:
                count += 1
        return count

    def _redirection_ratios(self):
        if self._cached_redirection_ratios is not None:
            return self._cached_redirection_ratios
        if not self.response or not self.response.history:
            self._cached_redirection_ratios = (0.0, 0.0)
            return self._cached_redirection_ratios
        history = self.response.history
        total = len(history)
        internal = sum(1 for r in history if self.hostname in (r.url or ''))
        external = total - internal
        self._cached_redirection_ratios = (
            round(internal / max(total, 1), 9),
            round(external / max(total, 1), 9)
        )
        return self._cached_redirection_ratios

    def login_form(self):
        if not self.soup:
            return 0
        for form in self.soup.find_all('form'):
            for inp in form.find_all('input'):
                itype = (inp.get('type') or '').lower()
                iname = (inp.get('name') or '').lower()
                if itype == 'password' or 'pass' in iname or 'login' in iname:
                    return 1
        return 0

    def external_favicon(self):
        if not self.soup:
            return 0
        for icon in self.soup.find_all('link', rel=re.compile(r'icon', re.I)):
            href = icon.get('href', '')
            if href.startswith('http') and self.hostname not in href:
                return 1
        return 0

    def links_in_tags(self):
        if not self.soup:
            return 0
        tags = self.soup.find_all(['meta', 'script', 'link'])
        total_links = self.nb_hyperlinks() + len(tags)
        if total_links == 0:
            return 0
        return round(len(tags) / total_links * 100, 6)

    def submit_email(self):
        if not self.soup:
            return 0
        for form in self.soup.find_all('form'):
            action = (form.get('action') or '').lower()
            if 'mailto:' in action:
                return 1
        if self.response and 'mail(' in self.response.text:
            return 1
        return 0

    def _media_ratios(self):
        if self._cached_media_ratios is not None:
            return self._cached_media_ratios
        if not self.soup:
            self._cached_media_ratios = (100.0, 0.0)
            return self._cached_media_ratios
        media = self.soup.find_all(['img', 'video', 'audio', 'source', 'embed'])
        if not media:
            self._cached_media_ratios = (100.0, 0.0)
            return self._cached_media_ratios
        internal = external = 0
        for m in media:
            src = m.get('src') or m.get('data', '')
            if not src or not src.startswith('http') or self.hostname in src:
                internal += 1
            else:
                external += 1
        total = max(internal + external, 1)
        self._cached_media_ratios = (
            round(internal / total * 100, 6),
            round(external / total * 100, 6)
        )
        return self._cached_media_ratios

    def sfh(self):
        if not self.soup:
            return 0
        for form in self.soup.find_all('form'):
            action = (form.get('action') or '').lower()
            if action in ('', 'about:blank'):
                return 1
            if action.startswith('http') and self.hostname not in action:
                return 1
        return 0

    def iframe(self):
        if not self.soup:
            return 0
        return 1 if self.soup.find('iframe') or self.soup.find('frame') else 0

    def popup_window(self):
        if not self.response:
            return 0
        return 1 if re.search(r'window\.open\s*\(', self.response.text) else 0

    def safe_anchor(self):
        if not self.soup:
            return 0.0
        anchors = self.soup.find_all('a', href=True)
        if not anchors:
            return 0.0
        unsafe = sum(1 for a in anchors if a['href'] in ('#', '', 'javascript:void(0)', 'javascript:;'))
        return round(unsafe / len(anchors) * 100, 6)

    def onmouseover(self):
        if not self.response:
            return 0
        return 1 if 'onmouseover' in self.response.text.lower() else 0

    def right_clic(self):
        if not self.response:
            return 0
        return 1 if re.search(r'event\.button\s*==\s*2|oncontextmenu', self.response.text, re.I) else 0

    def empty_title(self):
        if not self.soup:
            return 0
        title = self.soup.find('title')
        return 1 if not title or not title.string or title.string.strip() == '' else 0

    def domain_in_title(self):
        if not self.soup:
            return 0
        title = self.soup.find('title')
        return 1 if title and title.string and self.domain.lower() in title.string.lower() else 0

    def domain_with_copyright(self):
        if not self.response:
            return 0
        text = self.response.text.lower()
        return 1 if ('\u00a9' in text or 'copyright' in text) and self.domain.lower() in text else 0

    # ===== EXTERNAL SERVICE FEATURES =====

    def nb_redirection(self):
        return len(self.response.history) if self.response else 0

    def nb_external_redirection(self):
        if not self.response:
            return 0
        return sum(1 for r in self.response.history if self.hostname not in (r.url or ''))

    def whois_registered_domain(self):
        return 1 if self.whois_data and self.whois_data.domain_name else 0

    def domain_registration_length(self):
        try:
            if self.whois_data:
                exp = self.whois_data.expiration_date
                creation = self.whois_data.creation_date
                if isinstance(exp, list): exp = exp[0]
                if isinstance(creation, list): creation = creation[0]
                if exp and creation:
                    return (exp - creation).days // 30
        except Exception:
            pass
        return 0

    def domain_age(self):
        try:
            if self.whois_data:
                creation = self.whois_data.creation_date
                if isinstance(creation, list): creation = creation[0]
                if creation:
                    from datetime import datetime
                    return (datetime.now() - creation).days
        except Exception:
            pass
        return -1

    def web_traffic(self):
        return 0

    def dns_record(self):
        return self._dns_result if self._dns_result is not None else 0

    def google_index(self):
        return self._google_indexed if self._google_indexed is not None else 0

    def page_rank(self):
        return 0

    # ===== MAIN METHODS =====

    def getFeaturesDict(self):
        h = self._hyperlink_ratios()
        r = self._redirection_ratios()
        m = self._media_ratios()

        return {
            'length_url': self.length_url(),
            'length_hostname': self.length_hostname(),
            'ip': self.ip(),
            'nb_dots': self.nb_dots(),
            'nb_hyphens': self.nb_hyphens(),
            'nb_at': self.nb_at(),
            'nb_qm': self.nb_qm(),
            'nb_and': self.nb_and(),
            'nb_or': self.nb_or(),
            'nb_eq': self.nb_eq(),
            'nb_underscore': self.nb_underscore(),
            'nb_tilde': self.nb_tilde(),
            'nb_percent': self.nb_percent(),
            'nb_slash': self.nb_slash(),
            'nb_star': self.nb_star(),
            'nb_colon': self.nb_colon(),
            'nb_comma': self.nb_comma(),
            'nb_semicolumn': self.nb_semicolumn(),
            'nb_dollar': self.nb_dollar(),
            'nb_space': self.nb_space(),
            'nb_www': self.nb_www(),
            'nb_com': self.nb_com(),
            'nb_dslash': self.nb_dslash(),
            'http_in_path': self.http_in_path(),
            'https_token': self.https_token(),
            'ratio_digits_url': self.ratio_digits_url(),
            'ratio_digits_host': self.ratio_digits_host(),
            'punycode': self.punycode(),
            'port': self.port(),
            'tld_in_path': self.tld_in_path(),
            'tld_in_subdomain': self.tld_in_subdomain(),
            'abnormal_subdomain': self.abnormal_subdomain(),
            'nb_subdomains': self.nb_subdomains(),
            'prefix_suffix': self.prefix_suffix(),
            'random_domain': self.random_domain(),
            'shortening_service': self.shortening_service(),
            'path_extension': self.path_extension(),
            'nb_redirection': self.nb_redirection(),
            'nb_external_redirection': self.nb_external_redirection(),
            'length_words_raw': self.length_words_raw(),
            'char_repeat': self.char_repeat(),
            'shortest_words_raw': self.shortest_words_raw(),
            'shortest_word_host': self.shortest_word_host(),
            'shortest_word_path': self.shortest_word_path(),
            'longest_words_raw': self.longest_words_raw(),
            'longest_word_host': self.longest_word_host(),
            'longest_word_path': self.longest_word_path(),
            'avg_words_raw': self.avg_words_raw(),
            'avg_word_host': self.avg_word_host(),
            'avg_word_path': self.avg_word_path(),
            'phish_hints': self.phish_hints(),
            'domain_in_brand': self.domain_in_brand(),
            'brand_in_subdomain': self.brand_in_subdomain(),
            'brand_in_path': self.brand_in_path(),
            'suspecious_tld': self.suspecious_tld(),
            'statistical_report': self.statistical_report(),
            'nb_hyperlinks': self.nb_hyperlinks(),
            'ratio_intHyperlinks': h[0],
            'ratio_extHyperlinks': h[1],
            'ratio_nullHyperlinks': h[2],
            'nb_extCSS': self.nb_extCSS(),
            'ratio_intRedirection': r[0],
            'ratio_extRedirection': r[1],
            'ratio_intErrors': 0,
            'ratio_extErrors': 0,
            'login_form': self.login_form(),
            'external_favicon': self.external_favicon(),
            'links_in_tags': self.links_in_tags(),
            'submit_email': self.submit_email(),
            'ratio_intMedia': m[0],
            'ratio_extMedia': m[1],
            'sfh': self.sfh(),
            'iframe': self.iframe(),
            'popup_window': self.popup_window(),
            'safe_anchor': self.safe_anchor(),
            'onmouseover': self.onmouseover(),
            'right_clic': self.right_clic(),
            'empty_title': self.empty_title(),
            'domain_in_title': self.domain_in_title(),
            'domain_with_copyright': self.domain_with_copyright(),
            'whois_registered_domain': self.whois_registered_domain(),
            'domain_registration_length': self.domain_registration_length(),
            'domain_age': self.domain_age(),
            'web_traffic': self.web_traffic(),
            'dns_record': self.dns_record(),
            'google_index': self.google_index(),
            'page_rank': self.page_rank(),
        }

    def getFeaturesList(self):
        d = self.getFeaturesDict()
        return list(d.values())
