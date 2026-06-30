from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai_profiler",
    version="1.0.0",
    author="J.G. Arvidsson",
    description="Perfilador de hardware para recomendar motores de IA locales",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jgarvidsson/ai_profiler",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
    install_requires=[
        "psutil>=5.9.0",
        "nvidia-ml-py>=12.0.0",
        "requests>=2.28.0",
        "httpx>=0.24.0",
        "Pillow>=9.0.0",
        "tabulate>=0.9.0",
        "colorama>=0.4.6",
    ],
    extras_require={
        "web": ["flask>=2.3.0", "flask-cors>=4.0.0"],
        "models": ["huggingface-hub>=0.16.0", "transformers>=4.30.0"],
        "dev": ["pytest>=7.0.0", "pytest-cov>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "perfilador-ia=src.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
