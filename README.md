# Instapaper Auto-Archiver

*Auto-archiving for older unread bookmarks in Instapaper, inspired by Pocket Casts’ configurable auto-archive feature.*

## Motivation

This tool aims to reduce stress induced by a long Instapaper reading backlog, by automatically archiving older unread bookmarks for you.

This is the Instapaper equivalent of my [Feedbin Auto-Archiver](https://github.com/cdzombak/feedbin-auto-archiver). Please see [its Motivation discussion](https://github.com/cdzombak/feedbin-auto-archiver/blob/master/README.md#motivation) for more details.

## Requirements

- An [Instapaper](https://www.instapaper.com/) account
- An [Instapaper API Token/Secret](https://www.instapaper.com/main/request_oauth_consumer_token)

**To run with Docker:** a working Docker installation is required.

**To run with a local Python installation:** Python **3.6** is required. The newest available version of [pyinstapaper](https://pypi.org/project/pyinstapaper/), on which this script depends, requires a specific libxml version that does not build on newer Python versions. Additionally, pyinstapaper has [a bug](https://github.com/mdorn/pyinstapaper/pull/7) that prevents it from working with Python 3.5 or older.

Due to these compatibility issues, I recommend using this script under Docker; the provided Dockerfile builds a working image based on python3.6-alpine.

## Installation (Docker)

Pre-built Docker images are available. [See Docker Hub for details](https://hub.docker.com/r/cdzombak/instapaper-auto-archiver).

No installation is required to use these images under Docker.

## Installation (local Python)

1. Clone the repo and change into the `feedbin-auto-archiver` directory
2. Run `make virtualenv` to create a virtualenv for the project & install dependencies

## Configuration

### Credentials

Your Instapaper API token and secret are supplied via the environment variables `INSTAPAPER_API_ID` and `INSTAPAPER_API_SECRET`. [Get these here](https://www.instapaper.com/main/request_oauth_consumer_token).

Credentials are supplied via the environment variables `INSTAPAPER_LOGIN` and `INSTAPAPER_PASSWORD`.

#### Docker Configuration

Credentials may be placed in a `.env` file and given to the `docker run` command like:

```shell
docker run --rm --env-file .env cdzombak/instapaper-auto-archiver:1 [OPTIONS]
```

(See `.env.sample` for a sample file.)

Alternatively, credentials may be passed directly to the `docker run` command like:

```shell
docker run --rm \
    -e INSTAPAPER_API_ID=my_instapaper_api_key \
    -e INSTAPAPER_API_SECRET=my_instapaper_api_secret \
    -e INSTAPAPER_LOGIN=me@example.com \
    -e INSTAPAPER_PASSWORD=p@ssw0rd \
    cdzombak/instapaper-auto-archiver:1 [OPTIONS]
```

#### Local Python Configuration

Your credentials can be stored in a `.env` file alongside the `instapaper_archiver.py` script. The script will automatically read environment variables from that file. (See `.env.sample` for an example.)

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

## Usage

### Docker Usage

Invoke the script with `docker run`. To use a rules file, you will need to mount it into the container.

```shell
docker run --rm --env-file .env \
    -v /path/to/my_rules.json:/rules.json \
    cdzombak/instapaper-auto-archiver:1 \
    --rules-file /rules.json [--dry-run false] [OPTIONS]
```

### Local Python Usage

1. Activate the virtualenv: `. venv/bin/activate`
2. Run the script: `python instapaper_archiver.py --rules-file /path/to/my_rules.json [--dry-run false] [OPTIONS]`

Alternatively, invoke the virtualenv's Python interpreter directly:

```shell
venv/bin/python3.6 instapaper_archiver.py --rules-file /path/to/my_rules.json [--dry-run false] [OPTIONS]
```

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

(For Docker, run `docker run --rm --env-file .env cdzombak/instapaper-auto-archiver:1 list-domains`.)

### Crontab Example

This is how I’m running this tool on my personal server:

```text
# Instapaper Archiver
# Runs daily at 1:30am
30   1   *   *   *   docker run --rm --env-file $HOME/.config/instapaper/env cdzombak/instapaper-auto-archiver:1 --max-age 180 --entries-limit 100 --dry-run false
```

## License

[MIT License](https://choosealicense.com/licenses/mit/#).

## Author

Chris Dzombak, [dzombak.com](https://www.dzombak.com)
