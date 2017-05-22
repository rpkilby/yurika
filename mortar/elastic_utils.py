from .models import ProjectTree, Category
from django.conf import settings
import urllib.request
import simplejson, json
import string
from elasticsearch.client import IndicesClient
from elasticsearch import helpers


def create_index(name, analysis_conf=None):
    es = settings.ES_CLIENT
    i_client = IndicesClient(client=es)

    if i_client.exists(name):
        i_client.delete(name)

    if analysis_conf:
        body = analysis_conf
    else:
        body = create_analyzer_conf()
    i_client.create(index=name, body=body)

def reindex(source, dest, query, update=True):
    es = settings.ES_CLIENT
    if update:
        # makes version consistent between indexes, updates doc if id already exists
        helpers.reindex(client=es, source_index=source, target_index=dest, query=query)    
    else:
        # version_type=internal dumps all documents, overwriting same ids. 
        helpers.reindex(client=es, source_index=source, target_index=dest, query=query)    

def build_mortar_query(terms):
    # get tree terms  
    #terms = get_regex_list(tree)
    to_query = []
    for term in terms:
       to_query.append(
           { "match": {
               "content": term  
             }
           }
       )
    query = { 
        'query': {
            'bool': {
                'must': to_query
            }   
        }   
    }
    return query 

def create_analyzer_conf():
    # hardcode some analyzers for now
    return {
        "settings" : {
          "analysis": {
            "analyzer": {
              "content" : {
                "type": "pattern",
                "pattern": "\\s+",
                "filter": ["lowercase"]
                
              }
            }
          }
        }
    }

def create_pos_index(slug):
    i_client = IndicesClient(client=settings.ES_CLIENT)
    i_name = "pos_" + slug
    if i_client.exists(i_name):
        i_client.delete(index=i_name)
    i_settings = {
      'settings': {
        'analysis': {
          'analyzer': {
            'payloads': {
              'type': 'custom',
              'tokenizer': 'whitespace',
              'filter': [
                'lowercase',
                {'delimited_payload_filter': {
                  'encoding': 'identity'
                }}
              ]
            },
            'fulltext': {
              'type': 'custom',
              'stopwords': '_english_',
              'tokenizer': 'whitespace',
              'filter': [
                'lowercase',
                'type_as_payload'
              ]
            }
          }
        }
      },
      'mappings': {
        'doc': {
          'properties': {
            'url': {'type': 'string', 'index': 'not_analyzed'},
            'tstamp': {'type': 'date', 'format': 'strict_date_optional_time||epoch_millis'},
          }
        },
        'sentence': {
          '_parent': { 'type': 'doc' },
          'properties': {
            'content': {'type': 'string', 'analyzer': 'fulltext', "term_vector": "with_positions_offsets_payloads"},
            'tokens': {'type': 'string', 'analyzer': 'payloads', "term_vector": "with_positions_offsets_payloads"},
          }
        },
        'paragraph': {
          '_parent': { 'type': 'doc' },
          'properties': {
            'content': {'type': 'string', 'analyzer': 'fulltext', "term_vector": "with_positions_offsets_payloads"},
            'tokens': {'type': 'string', 'analyzer': 'payloads', "term_vector": "with_positions_offsets_payloads"},
          }
        }
      }
    }
    i_client.create(index=i_name, body=json.dumps(i_settings))

def pos_tokens_to_es(pos_tokens):
    out = []
    for sent in pos_tokens:
        body = {
            '_op_type': 'index',
            '_type': 'sentence',
            '_source': {}
        }
        body['_source']['content'] = "".join([" "+i[0] if not i[0].startswith("'") and i[0] not in string.punctuation else i[0] for i in sent])
        body['_source']['tokens'] = "".join([" "+i[0]+"|"+i[1] for i in sent if len(i[1]) and i[0] not in string.punctuation])
        out.append(body)
    return out

def insert_pos_record(slug, id, esdoc, pos_tokens):
    es = settings.ES_CLIENT
    body = {
      'url': esdoc['_source']['url'],
      'tstamp': esdoc['_source']['tstamp'][:-1],
    }
    es.index(index='pos_' + slug, id=id, doc_type="doc", body=json.dumps(body))
    sentences = pos_tokens_to_es(pos_tokens)
    for sentence in sentences:
        sentence['_index'] = 'pos_' + slug
        sentence['_parent'] = id
    helpers.bulk(client=es, actions=sentences)
    #es.index(index='pos_' + slug, parent=id, doc_type="sentence", body=json.dumps(sentence))

def build_es_annotations(tree):
    docs = models.Document.objects.filter(projecttree=tree)
    