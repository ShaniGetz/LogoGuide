'''
File-based Mapping classes.
'''

import abc, json, pickle
from  collections import Mapping
from _FrozenDict import FrozenDict

__all__ = ['FileDictReader', 'FileDict',
           'JsonDictReader', 'JsonDict',
           'PickleDictReader', 'PickleDict']


class FileDictReader(FrozenDict):
    '''A read-only dict stored in a file.'''

    def __init__(self, path):
        self._path = path
        content = self._load_dict(self._path)
        assert isinstance(content, Mapping)
        super(FileDictReader, self).__init__(content)

    @abc.abstractmethod
    def _load_dict(self, path):
        '''Load a dict from the given path.
        
        :param path: the path to load the dict from
        :type path: str
        :return: the dict loaded from the given path
        :rtype: Mapping
        '''
        raise NotImplementedError

    @property
    def path(self):
        '''the path where this dict is stored.
        
        :type: str'''
        return self._path


class FileDict(dict):
    '''A dict stored in a file.'''

    def __init__(self, path, idict=None):
        super(FileDict, self).__init__()
        self._path = path
        if idict is not None:
            super(FileDict, self).__init__(idict)
            self._save_dict(self._path)
        else:
            self.update(self._load_dict(self._path))

    def flush(self):
        '''Flush any changes to file.'''
        self._save_dict(self._path)

    @abc.abstractmethod
    def _load_dict(self, path):
        '''Load a dict from the given path.
        
        :param path: the path to load the dict from
        :type path: str
        :return: the dict loaded from the given path
        :rtype: Mapping
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def _save_dict(self, path):
        '''Save this dict to the given path.
        
        :param path: the path to save the dict to
        :type path: str
        '''
        raise NotImplementedError

    @property
    def path(self):
        '''the path where this dict is stored.
        
        :type: str'''
        return self._path


class JsonDictReader(FileDictReader):
    '''Dict that reads itself from a json file.
    '''
    def _load_dict(self, path):
        m = json.load(open(path, 'r'))
        assert isinstance(m, Mapping)
        return m


class JsonDict(FileDict):
    '''Dict that reads and writes itself from a json file.
    '''
    def _load_dict(self, path):
        m = json.load(open(path, 'r'))
        assert isinstance(m, Mapping)
        return m

    def _save_dict(self, path):
        json.dump(self, open(path, 'w'))


class PickleDictReader(FileDictReader):
    '''Dict that reads itself from a json file.
    '''
    def _load_dict(self, path):
        m = pickle.load(open(path, 'r'))
        assert isinstance(m, Mapping)
        return m


class PickleDict(FileDict):
    '''Dict that reads and writes itself from a json file.
    '''
    def _load_dict(self, path):
        m = pickle.load(open(path, 'r'))
        assert isinstance(m, Mapping)
        return m

    def _save_dict(self, path):
        pickle.dump(self, open(path, 'w'))
