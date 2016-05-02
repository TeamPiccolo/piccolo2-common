"""
.. moduleauthor:: Magnus Hagdorn <magnus.hagdorn@ed.ac.uk>
"""

__all__ = ['PiccoloWorkerThread']

import threading
from Queue import Queue
import logging

class PiccoloWorkerThread(threading.Thread):
    """base piccolo worker thread object"""

    LOGNAME = None

    def __init__(self,name,busy,tasks,results,daemon=True):
        """
        :param name: the name of the worker thread
        :param busy: a lock indicating whether the worker is busy or not
        :type busy: threading.Lock
        :param tasks: a queue used to communicate tasks to the worker
        :type tasks: Queue.Queue
        :param results: a queue used to communicate results to the caller
        :type results: Queue.Queue
        :param daemon: whether the worker should be run in daemon mode or not
        """
        assert isinstance(tasks,Queue)
        assert isinstance(results,Queue)

        threading.Thread.__init__(self)
        self.name = name
        self.daemon = daemon

        self._log = logging.getLogger('piccolo.worker.{0}.{1}'.format(self.LOGNAME,name))
        self.log.info('initialising worker')

        self._busy = busy
        self._tQ = tasks
        self._rQ = results

    @property
    def log(self):
        """the worker log"""
        return self._log

    @property
    def busy(self):
        """the busy lock"""
        return self._busy

    @property
    def tasks(self):
        """the task queue"""
        return self._tQ
    @property
    def results(self):
        """the results queue"""
        return self._rQ

    def run(self):
        """method representing thread's activity

        the method needs to be overridden by the subclasses and contains the 
        actual work the thread is performing. Communication with the caller is
        done via the tasks and results queues."""
        raise NotImplementedError
