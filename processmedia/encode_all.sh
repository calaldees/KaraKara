#!/bin/sh

for orig in files/*/[A-Z]* ; do
	./encode.sh "$orig"
done
