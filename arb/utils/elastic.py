# -*- coding: utf-8 -*-
from collections import OrderedDict

from elasticsearch.exceptions import ElasticsearchException
from elasticsearch.helpers import reindex
import traceback


_SCROLL_TIME = '15m'


def backup_index(es_source, es_target, source_index, target_index):
    """
    Warning
    ------------------------
    The existing target index is deleted.
    """
    # delete old
    if es_target.indices.exists(target_index):
        es_target.indices.delete(target_index)
    
    # index setup
    mappings = es_source.indices.get_mapping(index=source_index)[source_index]['mappings']
    settings = es_source.indices.get_settings(index=source_index)[source_index]['settings']
    setup_index_template(es_target, target_index, settings, mappings)
    if not _mappings_checking(es_source, es_target, source_index, target_index):
        raise Exception('mappings is not copied correctly')
    if not _settings_checking(es_source, es_target, source_index, target_index):
        raise Exception('settings is not copied correctly')
    
    # data
    es_source.indices.refresh(source_index)
    reindex(client=es_source, target_client=es_target,
            source_index=source_index, target_index=target_index,
            scroll=_SCROLL_TIME)


def setup_index_template(es, index, settings, mappings):
    """
    example of mappings:
    {
      "DOCTYPE": {
        "dynamic_templates": [],
        "date_detection": false,
        "properties": { ... }
      }
    }
    
    example of settings:
    {
        "DOCTYPE": {
            "index": {
              "creation_date": "1469167207934",
              "analysis": {
                "analyzer": {
                  "simple_lowercase_analyzer": {
                    "filter": [
                      "lowercase"
                    ],
                    "type": "custom",
                    "tokenizer": "keyword"
                  }
                }
              },
              "number_of_shards": "1",
              "number_of_replicas": "0",
              "uuid": "A6jFppuqTKuilR-tZPfrGg",
              "version": {
                "created": "2030399"
              }
            }
        }
    }
    """
    body = OrderedDict()
    body['settings'] = settings
    body['mappings'] = mappings
    
    try:
        es.indices.create(index, body)
    except ElasticsearchException as e:
        if e.error == 'index_already_exists_exception':
            pass
        else:
            print traceback.format_exc()
            raise e


def _mappings_checking(es_source, es_target, source_index, target_index):
    source_mappings = es_source.indices.get_mapping(index=source_index)[source_index]['mappings']
    target_mappings = es_target.indices.get_mapping(index=target_index)[target_index]['mappings']
    
    if source_mappings == target_mappings:
        return True
    else:
        return False


def _settings_checking(es_source, es_target, source_index, target_index):
    checked = True
    source_settings = es_source.indices.get_settings(index=source_index)[source_index]['settings']
    target_settings = es_target.indices.get_settings(index=target_index)[target_index]['settings']
    
    # analysis
    if 'analysis' in source_settings['index'].keys():
        if source_settings['index']['analysis'] != target_settings['index']['analysis']:
            checked = False

    return checked


# TESTING ONLY
if __name__ == '__main__':
    pass
