from models.data import Data
from implementations.youtube import YouTubeEnvironment
import json

DATA_LOCATION = "config/data.json" # TODO maybe read all config files to make back ups? Or only specific one, other files would be for storing options?

f = open(DATA_LOCATION, 'r')

out = f.read()

j = json.loads(out)

array = [Data(**i) for i in j]

for data in array:
    if data.environment == 'youtube':
        test = YouTubeEnvironment(data) # TODO Make less constrained?
    if (test == None or test.error): # TODO Make this shit better
        print(f"FAILED successfully")
        continue
    test.analyse()
    got = test.start()
    test.generate_m3u()

print(f"COMPLETED")
