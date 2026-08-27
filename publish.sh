#!/usr/bin/env bash
set -e
git init -b main
git add .
git commit -m "Steinberg displacement limit calculator: web, GUI, CLI"
gh repo create 3_sigma_steinberg_limit --public --source=. --push \
  --description "Steinberg relative displacement limits for PCB components: web calculator, Python GUI, and CLI"
