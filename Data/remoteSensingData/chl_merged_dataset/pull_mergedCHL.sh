#!/bin/bash
for i in $(seq 1996 2020); do
  FILENAME=$i.zip;
  URL=http://www.wimsoft.com/CC4km/$FILENAME
  echo 'Pulling '$FILENAME' from '$URL;
  curl -sS $URL > $FILENAME;
  unzip $FILENAME;
  rm $FILENAME;
  sleep 3;
done
