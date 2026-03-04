#!/usr/bin/env bash
# simple wrapper to install dependencies and start tracker service
cd "$(dirname "$0")/tracker" || exit 1
npm install
npm run start
