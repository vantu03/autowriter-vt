from setuptools import setup, find_packages

setup(
    name="autowriter-vt",
    version="0.1.1",
    author="Ma Văn Tú",
    description="AI-based content generator for Vietnamese articles",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vantu03/autowriter-vt",
    packages=find_packages(),
    install_requires=[
        "openai",
        "beautifulsoup4",
        "python-slugify",
    ],
    python_requires=">=3.7",
    include_package_data=True,
)
