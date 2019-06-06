# Introduction
Generates the API ref doc pages (https://www.defold.com/ref) using the existing Django template systems used by the rest of the site.

# Requirements
You need the following python libraries:

* django
* pygments

Install:

    pip install django
    pip install pygments

# Usage
Run it from the command line:

    python generate.py

Files will be generated to `out/<sha1>/xyz.html`.
