
import os
import json
from collections import Counter

import requests


token = os.environ['ST2_AUTH_TOKEN']
if not token:
    print('You must set the ST2_AUTH_TOKEN env variable to use this script.')

try:
    base_api_url = os.environ['ST2_BASE_URL']
except KeyError:
    base_api_url = 'http://127.0.0.1:9101'

headers = {'X-Auth-Token': token}


def get_executions_with_offset(action, offset):
    url = '{}/v1/executions/?action={}&status=failed' \
          '&sort_asc=True&limit=100&offset={}'.format(base_api_url, action, offset)
    resp = requests.get(url, headers=headers)
    resp_json = json.loads(resp.content)
    return resp_json


def get_all_executions(action):
    offset = 0
    results = []
    while True:
        executions = get_executions_with_offset(action, offset)
        results = results + executions
        if not executions:
            break
        offset += 100
    return results

query_results = get_all_executions('snpseq_packs.run_checkqc') + get_all_executions('arteria-packs.run_checkqc')

error_handlers = []
for r in query_results:
    execution_results = r['result']['result']
    try:
        for key in execution_results.keys():
            if "Handler" in key:
                error_handlers.append(key)
    # Sometimes there are no results, just skip those
    except AttributeError:
        pass


for handler, count in Counter(error_handlers).most_common(100):
    print("{}\t{}".format(handler, count))

print("\n")
print("UndeterminedPercentage in results")
timestamps = []
for r in query_results:
    execution_results = r['result']['result']
    try:
        if any("UndeterminedPercentage" in s for s in execution_results.keys()) and \
                        int(execution_results['version'].split('.')[0]) == 3:
            print("\t".join([r['start_timestamp'],
                             execution_results['version'],
                             execution_results['run_summary']['instrument_and_reagent_type']]))
    except AttributeError:
        pass

print("\n")
print("UnidentifiedIndexHandler in results")
for r in query_results:
    execution_results = r['result']['result']
    try:
        if any("UnidentifiedIndexHandler" in s for s in execution_results.keys()):
            print("\t".join([r['start_timestamp'],
                             execution_results['version'],
                             execution_results['run_summary']['instrument_and_reagent_type']]))
    except AttributeError:
        pass

print("\n")
print("ReadsPerSampleHandler in results")
instrs = []
for r in query_results:
    execution_results = r['result']['result']
    try:
        if any("ReadsPerSampleHandler" in s for s in execution_results.keys()):
            instrs.append(execution_results['run_summary']['instrument_and_reagent_type'])
            print("\t".join([r['start_timestamp'],
                             execution_results['version'],
                             execution_results['run_summary']['instrument_and_reagent_type']]))
    except AttributeError:
        pass
    except KeyError:
        pass

print(Counter(instrs))
