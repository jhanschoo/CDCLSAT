#!/usr/bin/env zsh


for f in $(ls "test_suite" | grep "\\.cnf$")
do
  echo "Processing $f"
  cat "test_suite/$f" |
  docker run --rm -i msoos/cryptominisat |
  grep "^s " |
  sed -e "s/s/c/" |
  cat <(echo "c $f") - "test_suite/$f" > "test_suite/$f.tmp"
  mv "test_suite/$f.tmp" "test_suite/$f"
done