#!/bin/bash
project='course'
variant=$1

SETTINGS_FILE="deployment/${project}/${variant}/local_settings.py"

echo "Cloning Settings"
git clone git@go.btech.id:dev/deployment.git

if [ -f "${SETTINGS_FILE}" ]; then
  /bin/cp "${SETTINGS_FILE}" "nolsatu_courses/local_settings.py"
else
  echo "ERROR: Settings file not found"
fi

rm -rf deployment

