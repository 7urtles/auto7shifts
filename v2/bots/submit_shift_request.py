# import requests

# headers = {
#     'Accept': '*/*',
#     'Content-Type': 'application/json',
#     'Referer': 'https://app.7shifts.com/company/139871/shift_pool/up_for_grabs',
#     'Origin': 'https://app.7shifts.com',
#     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
#     'x-xsrf-token': '889e5ad0b8cdc30370d61194a0c60c46',
# }

# json_data = {
#     'operationName': 'BidOnShiftPool',
#     'variables': {
#         'input': {
#             'shiftPoolId': '21692022',
#             'userId': 4849459,
#         },
#     },
#     'query': 'mutation BidOnShiftPool($input: BidOnShiftPoolInput!) {\n  bidOnShiftPool(bidOnShiftPoolInput: $input)\n}\n',
# }

# response = requests.post('https://app.7shifts.com/gql', headers=headers, json=json_data)
