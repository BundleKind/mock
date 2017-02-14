# Sorry, I don't have time to learn Ruby.
#
# Pull the data from the SQLite3 database and make
# the nonprofit pages.
import os
import sqlite3
from collections import namedtuple

Row = namedtuple('Row', [
    'name', 'tags', 'ein', 'url',
    'address', 'state', 'city', 'lng', 'lat',
    'description', 'is_501c3', 'long_description'
])


content = """---
name: "{name}"
tags:{tags}
ein: {ein}
homepage: "{url}"
address: |
 {address}
state: "{state}"
city: "{city}"
lng: {lng}
lat: {lat}
description: "{description}"
is_501c3: {is_501c3}
---

## Long description

{long_description}
"""


DBNAME = os.path.join('..', '..', 'nfp-acquisition', 'nonprofits.db')
conn = sqlite3.connect(DBNAME)
c = conn.cursor()

query = """
SELECT
    name, joined_tags, ein, url,
    business_address, state, city, lon AS lng, lat,
    activity,
    is_501c3,
    mission || '\n\n' || description AS long_description
FROM combined_data
WHERE city in ('Chicago', 'Seattle', 'New York', 'New_York', 'Atlanta', 'Billings', 'Detroit')
"""

def split_and_join_tags(tags):
    if tags:
        return '\n- ' + '\n- '.join(tags.split(','))
    else:
        return ''


def process(element):
    if element is None:
        return ''
    if isinstance(element, str):
        return element.replace('\n', '\n  ').replace('"', "'")
    else:
        return element


def capitalize_sentences(sentences):
    return '. '.join(s.lstrip().capitalize() for s in sentences.split('.'))


result = c.execute(query)
for entry in result:
    new_entry = [process(e) for e in entry]
    new_entry[9] = capitalize_sentences(new_entry[9])
    new_entry[11] = capitalize_sentences(new_entry[11])
    joined_tags = split_and_join_tags(new_entry[1])
    row = Row(new_entry[0], joined_tags, *new_entry[2:])
    if not row.ein or not row.city or not row.state:
        continue
    
    dir_path = os.path.join(
        '..', '_non_profits', row.state, row.city.replace(' ', '-')
    )
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    path = os.path.join(dir_path, '{}.md'.format(row.ein))
    with open(path, 'w') as outfile:
        outfile.write(content.format(**row._asdict()))
