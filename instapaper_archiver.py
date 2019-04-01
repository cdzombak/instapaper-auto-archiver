import argparse
import datetime as dt
import json
from jsoncomment import JsonComment
import os
from pyinstapaper.instapaper import Instapaper
import sys
from urllib.parse import urlparse

from dotenv import load_dotenv
load_dotenv()


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


class Rules(object):

    class SpecException(Exception):
        pass

    class ValidationException(Exception):
        pass

    def __init__(self, max_age, only_domain=None):
        self.default_max_age = max_age
        self.only_domain = only_domain
        self.domain_rules = {}

    def add_rules(self, rules_dict):
        if 'max_age' not in rules_dict:
            raise Rules.SpecException('Rules file must contain a global max_age specification.')
        self.default_max_age = int(rules_dict['max_age'])
        if 'domain_specific' not in rules_dict:
            raise Rules.SpecException('Rules file must contain a domain_specific rules list.')
        for rule in rules_dict['domain_specific']:
            if 'domain' not in rule or 'max_age' not in rule:
                raise Rules.SpecException('Domain rule {} must include a domain and max_age.'.format(json.dumps(rule)))
            self.domain_rules[rule['domain']] = int(rule['max_age'])

    def max_age(self, domain):
        retv = self.default_max_age
        if domain in self.domain_rules:
            retv = self.domain_rules[domain]
        if self.only_domain is not None and domain != self.only_domain:
            return dt.timedelta.max
        return dt.timedelta(days=retv)


def _domain_from_bookmark(bookmark):
    """Return the domain for this bookmark, lowercase and without a leading 'www.'"""
    parts = urlparse(bookmark.url)
    domain = parts.hostname
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain


def list_domains(ip_api, entries_limit):
    bookmarks = ip_api.get_bookmarks(folder='unread', limit=entries_limit)
    domains = sorted({_domain_from_bookmark(b) for b in bookmarks})
    for d in domains:
        print(d)


def run_archive(ip_api, entries_limit, rules, dry_run):
    if dry_run:
        print('Listing entries which would be archived...')
    else:
        print('Archiving old entries...')
    now = dt.datetime.now(dt.timezone.utc)
    bookmarks = ip_api.get_bookmarks(folder='unread', limit=entries_limit)
    count = 0
    for b in bookmarks:
        # entry_ts = dt.datetime.utcfromtimestamp(b.time).replace(tzinfo=dt.timezone.utc)
        entry_age = now - b.time.replace(tzinfo=dt.timezone.utc)
        domain = _domain_from_bookmark(b)
        max_age = rules.max_age(domain)
        if entry_age > max_age:
            print('')
            print('{domain:s}: {title:s}'.format(domain=domain, title=b.title))
            print('{age:d} days old (max age is {max:d} days)'.format(age=entry_age.days, max=max_age.days))
            print(b.url)
            if not dry_run:
                b.archive()
            count += 1
    print('')
    print('{:d} bookmarks affected.'.format(count))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Archive old Instapaper entries.')
    parser.add_argument('action', nargs='?', default='run', choices={'run', 'list-domains'})
    parser.add_argument('--dry-run', type=str2bool, default='true', help='True to print what would be archived, then exit. False to archive old unread entries. Default: True.')
    parser.add_argument('--entries-limit', type=int, default=250, help='Max number of entries to fetch via the Instapaper API. Default: 250. Max: 500.')
    parser.add_argument('--max-age', type=int, default=90, help='Entries older than this many days will be marked as read. Ignored if using --rules-file. Default: 90.')
    parser.add_argument('--only-domain', default=None, help='Operate on only entries from the given domain. Default: none.')
    parser.add_argument('--rules-file', default=None, help='Extended rules JSON file. See rules.sample.json for an example.')
    args = parser.parse_args()

    instapaper_api_id = os.getenv('INSTAPAPER_API_ID')
    instapaper_api_secret = os.getenv('INSTAPAPER_API_SECRET')
    instapaper_login = os.getenv('INSTAPAPER_LOGIN')
    instapaper_pass = os.getenv('INSTAPAPER_PASSWORD')
    if not instapaper_api_id or not instapaper_api_secret or not instapaper_login or not instapaper_pass:
        eprint("Instapaper API key & credentials must be set using environment variables.")
        eprint("Copy .env.sample to .env and fill it out to provide credentials.")
        sys.exit(1)
    ip_api = Instapaper(instapaper_api_id, instapaper_api_secret)
    try:
        ip_api.login(instapaper_login, instapaper_pass)
    except Exception as e:
        eprint("Instapaper authentication failed: {}".format(e))
        eprint("Check your credentials and try again.")
        sys.exit(1)

    if args.action == 'list-domains':
        list_domains(ip_api, args.entries_limit)
        sys.exit(0)

    if args.action == 'run':
        rules = Rules(args.max_age, only_domain=args.only_domain)
        if args.rules_file:
            rules_dict = JsonComment().loadf(args.rules_file)
            try:
                rules.add_rules(rules_dict)
            except Rules.SpecException as e:
                eprint(e)
                sys.exit(1)
        run_archive(ip_api, entries_limit=args.entries_limit, rules=rules, dry_run=args.dry_run)
        sys.exit(0)

    raise Exception('Unexpected/unhandled action argument encountered.')
