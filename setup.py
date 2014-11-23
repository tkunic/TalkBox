try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

config = {
	'description': 'A Raspberry Pi app that enables action assignment to MPR121 pins.',
	'author': 'Toni Kunic',
	'url': 'tkunic.me/TalkBox',
	'download_url': 'https://github.com/tkunic/raspitap/zipball/master',
	'version': '0.1',
	'install_requires': ['nose', 'smbus', 'evdev'],
	'packages': ['raspitap'],
	'scripts': [],
	'name': 'raspitap'
}

setup(**config)
