# Instapaper Auto-Archiver

*Auto-archiving for older unread bookmarks in Instapaper, inspired by Pocket Casts’ configurable auto-archive feature.*

## Motivation

This tool aims to reduce stress induced by a long Instapaper reading backlog, by automatically archiving older unread bookmarks for you.

This is the Instapaper equivalent of my [Feedbin Auto-Archiver](https://github.com/cdzombak/feedbin-auto-archiver). Please see [its Motivation discussion](https://github.com/cdzombak/feedbin-auto-archiver/blob/master/README.md#motivation) for more details.

## Requirements

- Python 3 + [virtualenv](https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv)
- An [Instapaper](https://www.instapaper.com/) account
- An [Instapaper API Token/Secret](https://www.instapaper.com/main/request_oauth_consumer_token)

I know this works on macOS and Ubuntu; it should work pretty much anywhere Python 3 runs.

## Installation

- Clone the repo
- Run `make bootstrap` to create a virtualenv for the project & install dependencies
- Copy `.env.sample` to `.env` and fill out your credentials

### Crontab Example

This is how I’m running this tool on my personal server:

```
# Instapaper Archiver
# Runs daily
30   0   *   *   *   /home/cdzombak/scripts/instapaper-auto-archiver/venv/bin/python3 /home/cdzombak/scripts/instapaper-auto-archiver/instapaper_archiver.py --max-age 100 --entries-limit 100 --dry-run false
```

### Cleanup

`make clean` will remove the virtualenv and cleanup any temporary artifacts (currently, there are none of those).

## Usage

- Activate the virtualenv: `. venv/bin/activate`
- Run the script: `python instapaper_archiver.py [flags]`

At least some flags are needed to make the script do anything useful. Credential configuration is documented in “Configuration,” below.

### Flags

All flags are optional (though if you omit `--dry-run`, no changes will ever be made in your Instapaper account).

#### `--dry-run`

**Boolean. Default: True.**

Dry-run specifies whether the script should actually change anything in your Instapaper account. By default, this is `true`, meaning no changes will be made.

Once you’re confident in your configuration, activate the script with `--dry-fun false`.

#### `--entries-limit`

**Integer. Default: 250. Max: 500.**

Max number of bookmarks to try to fetch via the Instapaper API. Instapaper limits this to a maximum of `500`; a smaller number should suffice.

#### `--max-age`

**Integer. Default: 90.**

The maximum age for unread bookmarks. Bookmarks older than this will be marked as read.

This argument is ignored when using a rules file (see `--rules-file` below).

#### `--only-domain`

**String. Default: none.**

Only archive bookmarks from the given domain. This is useful for eg. debugging or one-off archviing tasks.

#### `--rules-file`

**String (path/filename). Default: none.**

The path to a JSON file describing your per-domain rules. See “Configuration” below for details.

If a rules file is specified, the `--max-age` flag has no effect.

### List Domains

Run `python instapaper_archiver.py list-domains` to print a list domains from which you currently have unread bookmarks, for use in writing per-domain rules.

The output is grep-able. For example, to find the NY Times website, try `python instapaper_archiver.py list-domains | grep -i "nytimes"`

## Configuration

### Credentials

Your Instapaper API token and secret are supplied via the environment variables `INSTAPAPER_API_ID` and `INSTAPAPER_API_SECRET`.

Credentials are supplied via the environment variables `INSTAPAPER_LOGIN` and `INSTAPAPER_PASSWORD`.

Optionally, these can be stored in a `.env` file alongside the `instapaper_archiver` script. The script will automatically read environment variables from that file. (See `.env.sample` for an example.)

### Rules File

The rules file is a JSON file specifying per-domain maximum unread bookmark ages. The file is allowed to contain comments, allowing for clarity & easier maintenance. See `rules.sample.json` for an example.

The file must contain an object with two top-level keys: `max_age` and `domain_specific`.

`max_age` is equivalent to the `--max-age` argument; any bookmarks older than that age will be marked as read, unless they’re from a domain for which you’ve created a custom rule.

`domain_specific` is a list of objects, each of which have two keys, like this:

```javascript
"domain_specific": [
  {
    "domain": "nytimes.com",
    "max_age": 30
  }, // …
]
```

Those domain-specific rules take precedence over `max_age`. This allows you to set a quicker expiration for certain sites, or set a longer expiration for sites that tend to have evergreen articles you really don’t want to miss.

### “Ignore This Domain”

To avoid the archiver marking anything as read for a given domain, specify `999999999` for the domain’s `max_age`. (That is roughly 2.7 million years.)

This is the [maximum](https://docs.python.org/3/library/datetime.html#datetime.timedelta.max) number of days a Python `timedelta` object can represent.

## License

[MIT License](https://choosealicense.com/licenses/mit/#).

## Author

Chris Dzombak, [dzombak.com](https://www.dzombak.com)
