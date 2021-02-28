from setuptools import setup
import re

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open("vrcpy/__init__.py") as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(),
                        re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Version is not set')

with open("README.md") as f:
    readme = f.read()

extras_require = {
    'aquick': [
        'cchardet',
        'aiodns',
        'brotlipy'
    ]
}

setup(
    name="vrcpy",
    author="Katistic",
    url="https://github.com/VRChatAPI/VRChatPython",
    project_urls={
        "Issue Tracker": "https://github.com/VRChatAPI/VRChatPython/issues",
        "Examples": "https://github.com/VRChatAPI/VRChatPython/tree/master/examples"
    },
    version=version,
    packages=['vrcpy'],
    # license="MIT",
    description="A Python wrapper for the VRChat WebAPI supporting both sync and async",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras_require,
    python_requires=">=3.5.3",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8"
    ]
)
