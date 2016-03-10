
import logging
import os
import platform

from rhsm.facts import collection

log = logging.getLogger(__name__)


def get_arch(prefix=None):
    """Get the systems architecture.

    This relies on portable means, like uname to determine
    a high level system arch (ie, x86_64, ppx64,etc).

    We need that so we can decide how to collect the
    arch specific hardware infomation.

    Also support a 'prefix' arg that allows us to override
    the results. The contents of the '/prefix/arch' will
    override the arch. The 'prefix' arg defaults to None,
    equiv to '/'. This is intended only for test purposes.

    Returns a string containing the arch."""

    DEFAULT_PREFIX = '/'
    ARCH_FILE_NAME = 'arch'
    prefix = prefix or DEFAULT_PREFIX

    if prefix == DEFAULT_PREFIX:
        return platform.machine()

    arch_file = os.path.join(prefix, ARCH_FILE_NAME)
    try:
        with open(arch_file, 'r') as arch_fd:
            return arch_fd.read().strip()
    except IOError as e:
        # If we specify a prefix, and there is no 'arch' file,
        # consider that fatal.
        log.exception(e)
        raise

# An empty FactsCollector should just return an empty dict on get_all()


class FactsCollector(object):
    def __init__(self, arch=None, prefix=None, testing=None,
                 hardware_methods=None, collected_hw_info=None, collectors=None):
        """Base class for facts collecting classes.

        self._collected_hw_info will reference the passed collected_hw_info
        arg. When possible this should be a reference (or copy) to all of the facts
        collected in this run. Some collection methods need to alter behavior
        based on facts collector from other modules/classes.
        self._collected_hw_info isn't meant to be altered as a side effect, but
        no promises."""
        self.log = logging.getLogger(__name__ + '.' + self.__class__.__name__)
        self.log.debug("FactsCollector init")

        self.allhw = {}
        self.prefix = prefix or ''
        self.testing = testing or False

        self._collected_hw_info = collected_hw_info
        # we need this so we can decide which of the
        # arch specific code bases to follow
        self.arch = arch or get_arch(prefix=self.prefix)

        self.hardware_methods = hardware_methods or []
        self.collectors = collectors or iter([])

    def collect(self):
        """Return a FactsCollection iterable."""
        self.log.debug("in _collect")
        facts_dict = self.get_all()
        self.log.debug("facts_dict=%s", facts_dict)
        facts_collection = collection.FactsCollection(facts_dict=facts_dict)
        self.log.debug("facts_collection=%s", facts_collection)
        return facts_collection

    def get_all(self):

        # try each hardware method, and try/except around, since
        # these tend to be fragile
        all_hw_info = {}
        for hardware_method in self.hardware_methods:
            info_dict = {}
            try:
                info_dict = hardware_method()
            except Exception as e:
                log.warn("%s" % hardware_method)
                log.warn("Hardware detection failed: %s" % e)

            all_hw_info.update(info_dict)

        return all_hw_info


class CachedFactsCollector(FactsCollector):

    def save_to_cache(self, facts_collection):
        # Create a new FactsCollection with new timestamp
        cached_facts = collection.FactsCollection.from_facts_collection(facts_collection)
        cached_facts.save()

    def collect(self):
        cached_collection = collection.FactsCollection.from_cache_file(self.cache_file)
        fresh_collection = collection.FactsCollection()

        # not really '==', but more of a 'close-enough-to-equals', ie
        # the cache isn't expired, so don't bother looking any closer.
        #
        #
        if cached_collection == fresh_collection:
            return cached_collection

        # replace with an iterator
        fresh_collection.data = self.get_all()
        # Most of the time, we still haven't collected any facts yet.
        # Until we iterate over fresh_facts, does it's iter start collection
        return fresh_collection
        #return self.collection
