#!/bin/sh

for orig in files/*/original.* ; do
	./encode.sh "$orig"
done
