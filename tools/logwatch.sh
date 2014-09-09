#!/bin/bash

tail -F latest.log |xargs -0 -d "\n" -I{} -n1 ./send.pl "{}"


