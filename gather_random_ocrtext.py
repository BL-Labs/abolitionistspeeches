import os, json
from random import choice
import csv

archive = "/datastore/newspaperarchive"
store = "ocrtest/random"

from newspaperaccess import NewspaperArchive, papertopath, WEIGHTED_NEWSPAPERS as newspapers

SAMPLESIZE = 925 # pages

fp = open("randomocr.csv", "w")
logdoc = csv.DictWriter(fp, fieldnames = ["newspaper", "year", "month", "day", "page"])

n = NewspaperArchive()

def get_random_newspaper_ref():
  ref = {}
  c = 0
  while "day" not in ref:
    if c > 10:
      raise Exception("Proper fail")
    try:
      ref = {'newspaper' : choice(newspapers)}
      ref['year'] = choice(n.years_available(ref['newspaper']))#
      ref['month'] = choice(n.months_available(ref['newspaper'], ref['year']))
      ref['day'] = choice(n.days_available(ref['newspaper'], ref['year'], ref['month']))
    except Exception as e:
      c += 1
  return ref

def get_random_newspaper():
  ref = get_random_newspaper_ref()
  return ref, n.get(**ref)

def store_text(ref, doc):
  if "page" not in ref:
    raise Exception()
  txt = "\n".join(["{0}\n\n{1}\n".format(*doc[ref['page']][item]) for item in sorted(doc[ref['page']].keys())])
  os.makedirs(os.path.join(store, ref['newspaper'], ref['year']), exist_ok = True)
  # txt
  with open(os.path.join(store, ref['newspaper'], ref['year'], "{month}_{day}_{page}.txt".format(**ref)), "w") as ofp:
    ofp.write(txt)
  # json
  with open(os.path.join(store, ref['newspaper'], ref['year'], "{month}_{day}_{page}.json".format(**ref)), "w") as jfp:
    json.dump(doc[ref['page']], jfp)

count = 0

while count < SAMPLESIZE:
  try:
    ref, doc = get_random_newspaper()
    ref['page'] = choice(list(doc.keys()))
    store_text(ref, doc)
    print("{newspaper} {day}/{month}/{year} pg. {page}".format(**ref))
    logdoc.writerow(ref)
    count += 1
  except ValueError as e:
    print("Hit the dodgy bit")
    print(e)

fp.close()
