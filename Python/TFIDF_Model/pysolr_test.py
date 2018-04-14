import pysolr
import re
from os import listdir
from os.path import isfile, join

dirName = "./data"
files = [f for f in listdir(dirName) if isfile(join(dirName, f))]
solr = pysolr.Solr('http://140.124.183.39:8983/solr/EBCStation', timeout=10)

solr.delete(id='test_*')

index = 0
for file in files:
	index += 1
	solrID = "test_" + str(index)
	with open(join(dirName, file), 'r', encoding='utf-8') as infile:
		solrContent = re.sub('[\s+]', '', infile.read().replace("<UNK>", ""))
		solr.add([
	    {
	        "id": solrID,
	        "content": solrContent,
	    }])

# Setup a Solr instance. The timeout is optional.
# solr = pysolr.Solr('http://140.124.183.39:8983/solr/EBCStation', timeout=10)

# # How you'd index data.
# solr.add([
#     {
#         "id": "doc_1",
#         "title": "A test document",
#     },
#     {
#         "id": "doc_2",
#         "title": "The Banana: Tasty or Dangerous?",
#     },
# ])