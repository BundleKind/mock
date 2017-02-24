import glob
import path
import os
import yaml

script = """---
---
{%% capture all_the_things %%}
{%% comment %%} ----------------- Setup: get this city's nfps ------------------------ {%% endcomment %%}
{%% assign nfps = site.non_profits | where: "state", "%s" | where: "city", "%s" %%}

{%% comment %%} ----------------- Output : A JSON object ----------------------------

  Output will look like this:
    [
        { ein: <ein>, name: <name>, url: <url>, tags:[<tag>, <tag>, ..., <tag>] }, 
        ...
    ]

{%% endcomment %%}

[
{%% for nfp in  nfps %%}
    {%% capture url %%}%s/{{ nfp.ein }}{%% endcapture %%}
    { "ein": "{{nfp.ein}}", "name": "{{nfp.name}}", "url": "{{ url }}", "tags":[{%% assign len = nfp.tags | size %%}{%% if len > 0 %%}"{{nfp.tags | join: '", "'}}"{%% endif %%}] }{%% if forloop.last == false %%},{%% endif %%}
{%% endfor %%}
]
{%% endcapture %%}
{%% comment %%} -------------------------- Actual output here! --------------------------- {%% endcomment %%}
{{ all_the_things | replace: "\\n\\n", "\\n " }}
"""

for state_path in glob.glob(os.path.join('..', '_non_profits', '*')):
    state = os.path.basename(state_path)
    for city_path in glob.glob(os.path.join(state_path, '*')):
        dash_city = os.path.basename(city_path)
        city = ' '.join(dash_city.split('-'))
        url_midsection = os.path.join(state, dash_city + '.html')
        destination_path = city_path.replace('_non_profits', os.path.join('assets', 'data')) + '.json'
        destination_dir = os.path.dirname(destination_path)
        if not os.path.exists(destination_dir):
            os.path.mkdir(destination_dir)
        with open(destination_path, 'w') as outfile:
            outfile.write(script % (state, city, url_midsection))
