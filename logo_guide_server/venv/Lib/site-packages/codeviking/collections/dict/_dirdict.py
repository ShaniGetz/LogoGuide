'''
File-based Mapping classes.
'''

import abc, json, os, pickle
from  collections import Mapping, MutableMapping

__all__ = ['ItemMapperError',
           'ItemMapper', 'ExtItemMapper',
           'JsonMapper', 'PickleMapper',
           'DirDictReader', 'DirDict']


class ItemMapperError(Exception):
    '''used when a ItemMapper fails. 
    '''
    pass


class ItemMapper(object):
    '''Loads and saves values and translates between keys and rpath (relative
     path)  All rpaths are relative to the root path.
    '''
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def key_to_rpath(self, *keyparts):
        '''Calculate a relative path from a key.  
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def rpath_to_key(self, *rpath):
        '''Calculate a key from a relative path.  If rpath cannot be mapped to
        a key, return `None`.
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def load_value(self, path):
        '''Load an object from the given path.'''
        raise NotImplementedError

    @abc.abstractmethod
    def save_value(self, obj, path):
        '''Save an object to the given path.'''
        raise NotImplementedError


def split_path(path):
    '''Split a path into individual components (the parts between path
    separators).
    
    :param path: the path to split.
    :type path: `basestring`
    :return: the path components
    :rtype: `list`
    '''
    p, f = os.path.split(path)
    result = [f]
    while p:
        p, f = os.path.split(p)
        result = [f] + result
    return result


class ExtItemMapper(ItemMapper):
    '''An ItemMapper that maps keys to files with a specific extension. A key
    is translated to a file path by adding an exension to in.  If a file is 
    more than one directory deep, the os-specific path separators are replaced
    with `path_sep`.
    '''
    # pylint: disable-msg=W0223

    def __init__(self, ext, path_sep='/'):
        '''
        :param ext: the extension for files
        :type ext: `basestring` 
        :param path_sep: the separator to use between directory names 
        :type path_sap: `basestring` 
        '''
        super(ExtItemMapper, self).__init__()
        self._ext = ext
        self._path_sep = path_sep

    def key_to_rpath(self, *keyparts):
        key = self._path_sep.join(keyparts)
        try:
            p = key.split(self._path_sep)
            p[-1] = p[-1] + self._ext
            return os.path.join(*p)
        except:
            raise ItemMapperError('Unable to map key="%s" to an rpath.' %
                                 repr(key))

    def rpath_to_key(self, *rpath):
        rpath = os.path.join(*rpath)
        result = split_path(rpath)
        if not result[-1].endswith(self._ext):
            return None
        result[-1] = result[-1][:-len(self._ext)]
        return self._path_sep.join(result)

    def join(self, *key):
        '''Join names together wth path_sep, creating a composite key.
        '''
        return self._path_sep.join(key)


class JsonMapper(ExtItemMapper):
    '''A `ItemMapper` that stores values in json files.
    '''
    def __init__(self, path_sep='/'):
        super(JsonMapper, self).__init__(ext='.json', path_sep=path_sep)

    def load_value(self, path):
        return json.load(open(path, 'r'))

    def save_value(self, obj, path):
        json.dump(obj, open(path, 'w'))


class PickleMapper(ExtItemMapper):
    '''A `ItemMapper` that stores values in pickle files.
    '''
    def __init__(self, path_sep='/'):
        super(PickleMapper, self).__init__(ext='.pickle', path_sep=path_sep)

    def load_value(self, path):
        return pickle.load(open(path, 'r'))

    def save_value(self, obj, path):
        pickle.dump(obj, open(path, 'w'))


class DirDictReader(Mapping):
    '''A read only dict-like object (`Mapping`) subclass that stores its
    values in a directory.  Keys are filenames, and the file contents are 
    values.
    File names are relative to the root path.
    '''

    def __init__(self, root_path, mapper):
        ''':param root_path: the directory where the files are stored.
        :type root_path: str
        :param mapper: the ItemMapper to use
        :type mapper: ItemMapper
        '''
        super(DirDictReader, self).__init__()
        self._root_path = root_path
        self._mapper = mapper

    @property
    def root_path(self):
        '''the root path of the directory where this dict is stored.
        
        :type: str'''
        return self._root_path

    def get_path(self, key):
        '''Get the full path for a given key.
        
        :param key: the key
        :type key: `basestring`
        '''
        rp = self._mapper.key_to_rpath(key)
        if rp is None:
            return None
        return os.path.join(self._root_path, rp)

    def _keys_in(self, rpath=''):
        '''
        :param rpath: a directory path, relative to the root_path
        :type rpath: str
        :return: a list of the file ids contained in the given directory, and
          all subdirectories.
        :rtype: list
        '''
        path = os.path.join(self._root_path, rpath)
        if not os.path.exists(path):
            return list()
        children = os.listdir(path)
        result = []
        for c in children:
            p = os.path.join(path, c)
            if os.path.isfile(p):
                k = self._mapper.rpath_to_key(rpath, c)
                if k is not None:
                    result.append(k)
            elif os.path.isdir(p):
                d = self._keys_in(os.path.join(rpath, c))
                result.extend(['%s/%s' % (c, f) for f in d])
        return result

    def get(self, key, default=None):
        p = self.get_path(key)
        if p is None or not os.path.exists(p):
            return default
        return self._mapper.load_value(p)

    def keys(self):
        for i in self._keys_in():
            yield i

    def __len__(self):
        return len(self._keys_in())

    def __iter__(self):
        for i in self._keys_in():
            yield i

    def __contains__(self, key):
        p = os.path.join(self._root_path, self._mapper.key_to_rpath(key))
        return (os.path.exists(p) and os.path.isfile(p))

    def __eq__(self, other):
        keys = set(self.keys())
        okeys = set(other.keys())
        if okeys != keys:
            return False
        for k in keys:
            if self.get(k) != other.get(k):
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getitem__(self, key):
        p = self.get_path(key)
        if (not os.path.exists(p)) or (not os.path.isfile(p)):
            raise KeyError('This object does not contain "%s"' % key)
        return self._get_value(p)

    def _get_value(self, path):
        '''Get a value from a file
        
        :param path: the path to read the value from
        :type path: basestring
        :return: the value read from the given path
        '''
        return self._mapper.load_value(path)

    def items(self):
        for k in self.keys():
            yield (k, self.get(k))

    def values(self):
        for k in self.keys():
            yield self.get(k)

    def as_dict(self):
        '''Return contents as a dict'''
        return {k: v for (k, v) in self.items()}


class DirDict(DirDictReader, MutableMapping):
    '''A read-write variant of `FileDictReader`.
    '''
    def __init__(self, root_path, mapper, clear=False):
        super(DirDict, self).__init__(root_path, mapper)
        if clear:
            self._remove_files(self._root_path)
        if not os.path.exists(self._root_path):
            os.makedirs(self._root_path)

    def _remove_files(self, rpath):
        '''Recursively remove all files in the rpath that match the mapper. 
        '''
        path = os.path.join(self._root_path, rpath)
        children = os.listdir(path)
        for c in children:
            p = os.path.join(path, c)
            if os.path.isfile(p):
                rpc = os.path.join(rpath, c)
                if self._mapper.rpath_to_key(rpc) is not None:
                    os.remove(p)
            elif os.path.isdir(p):
                self._remove_files(p)
                if len(os.listdir(p)) == 0:
                    os.removedirs(p)

    def __setitem__(self, key, value):
        p = self.get_path(key)
        # make sure the destination directory exists
        d = os.path.dirname(p)
        if not os.path.exists(d):
            os.makedirs(d)
        self._mapper.save_value(value, p)

    def __delitem__(self, key):
        p = self.get_path(key)
        if not os.path.exists(p):
            raise KeyError('This object does not contain "%s"' % key)
        os.remove(p)
        d = os.path.dirname(p)
        if len(os.listdir(d)) == 0:
            os.removedirs(d)
