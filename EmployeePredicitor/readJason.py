import json

data = {}  
data['people'] = []  
data['people'].append({  
    'name': 'Scott',
    'website': 'stackabuse.com',
    'from': 'Nebraska'
})
data['people'].append({  
    'name': 'Larry',
    'website': 'google.com',
    'from': 'Michigan'
})
data['people'].append({  
    'name': 'Tim',
    'website': 'apple.com',
    'from': 'Alabama'
})

fp = open('output.txt', 'w')
for obj in data['people']:
    line = json.dumps(obj)
    fp.write(line + '\n')
fp.close()

#with open('data.txt', 'w') as outfile:  
#        json.dump(data, outfile)        