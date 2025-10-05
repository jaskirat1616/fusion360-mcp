from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fusion360-mcp",
    version="1.0.0",
    author="FusionMCP Team",
    description="Multi-model MCP integration for Autodesk Fusion 360",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fusion360-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "requests>=2.31.0",
        "aiohttp>=3.9.1",
        "pydantic>=2.5.3",
        "pydantic-settings>=2.1.0",
        "python-dotenv>=1.0.0",
        "loguru>=0.7.2",
        "httpx>=0.26.0",
        "anthropic>=0.18.1",
        "openai>=1.10.0",
        "google-generativeai>=0.3.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.23.3",
            "black>=23.12.1",
            "ruff>=0.1.9",
        ],
    },
)
