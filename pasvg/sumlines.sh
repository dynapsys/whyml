#!/bin/bash
find /home/tom/github/dynapsys/whyml/pasvg/src -type f -name "*.py" -exec wc -l {} \; | sort -nr