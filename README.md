# Top.py
![issues: unresolved](https://img.shields.io/github/issues/dragdev-studios/top.py?style=flat-square)
![pull requests: unresolved](https://img.shields.io/github/issues-pr/dragdev-studios/top.py?style=flat-square)
![version: unresolved](https://img.shields.io/pypi/v/top.py?style=flat-square)
![supported python versions: unresolved](https://img.shields.io/pypi/pyversions/top.py?style=flat-square)
![downloads: unresolved](https://img.shields.io/pypi/dw/top.py?style=flat-square)
![code style: black](https://img.shields.io/badge/code%20style-black-black?style=flat-square)


An alternative wrapper for the [top.gg API](//docs.top.gg)

*Please note, this is __not an official package from top.gg__. We are not affiliated with top.gg in any way.
If you want to install their official package, please see [their repo](//github.com/top-gg/python-sdk).*

## Introduction
top.py is a python wrapper for the top.gg discord bot list API. top.py aims to be object-oriented, whereas the official
top.gg python SDK is more low-level raw data.

### Supported Features
<!-- ✅ ❌ -->
| Feature Name | Supported? |
| ------------ | ---------- |
| Automatic posting of server count | ✅ |
| Searching/Bulk Querying Bots | ✅ |
| Fetching a bot | ✅ |
| Fetching a user | ✅ |
| Fetching last 1000 upvotes | ✅ |
| Fetching a bot's stats | ✅ |
| Checking individual user vote | ✅ |
| Manual posting server count | ✅ |
| Models for all individual endpoints | ✅ |
| In-house ratelimiting | ✅ |
| Vote Webhooks | ✅ |
| Making you a nice slice of toast | ❌ |

**NOTE:** We do __NOT__ currently provide official support for discord server list. That's coming soon.

### Why use top.py over top.gg's sdk?
It's entirely up to your personal preference. But here's a few differences between this and the official sdk:

* top.py is object-oriented - this means everything has a class, meaning no fiddling with raw data values from top.gg.
* top.py is more humanised - top.py is designed with ease of use in mind, so you may find there is a smoother experience implementing this than top.gg's sdk.

Just try it, you can choose what you like.

Also, while we try to be our own package, you may notice we've aiased a few classes, functions and behavious
to act like top.gg's sdk. This is mainly so you have an easier experience migrating, and it's less headache.


## Installation
You can install the latest stable release here:
```shell
pip install top.py
```
But, if you're reading this, you're most likely a developer - you should know how to install packages by now.

## Useful links
[support](//discord.gg/YBNWw7nMGH) (or mention @eek#7574 in top.gg) | [docs](//toppy.dragdev.xyz) | [PyPi](//pypi.org/project/top.py) |
[examples](/examples.md) | [\(META\) Code Of Conduct](/CODE_OF_CONDUCT.md) | [\(META\) Contributing Guidelines](/CONTRIBUTING.md)

[Experiencing an issue?](/issues/new)
