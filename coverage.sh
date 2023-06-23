#!/bin/bash
coverage run -m unittest discover -s test -t . && coverage report -m