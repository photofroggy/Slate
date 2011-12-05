''' stutter.logging module
    Created by photofroggy
    Copyright (c) photofroggy 2011
'''

import os
import sys
import time
import os.path
from Queue import Queue
from threading import Thread
from threading import BoundedSemaphore


class LEVEL:
    """ Determines the logging levels available in the package. """
    DEBUG = 0
    MESSAGE = 1
    WARNING = 2
    ERROR = 3


class BaseLogger(object):
    """ Basic object used for logging.
        
        No buffering or threading is used in this object. Output messages given
        to the different methods are instantly given to the provided output
        method and saved to a log file in the desired log folder.
    """
    
    level = LEVEL.MESSAGE
    save_logs = True
    save_folder = None
    stamp = None
    
    def __init__(self, stdout=None, stamp=None, level=None, save_folder=None, save_logs=True):
        
        if stdout is None:
            def default_write(msg=''):
                sys.stdout.write(msg)
                sys.stdout.flush()
            self.stdout = default_write
        else:
            self.stdout = stdout
        
        self.save_logs = save_logs
        
        if level is not None:
            self.level = level
        
        self.save_folder = save_folder or './log'
        if not os.path.exists(self.save_folder):
            os.mkdir(self.save_folder, 0o755)
        
        self.stamp = stamp or '%H:%M:%S|'
    
    def _fname(self, timestamp, **kwargs):
        """ Return a file name based on the given input. """
        return '{0}/{1}.txt'.format(self.save_folder, time.strftime('%Y-%m-%d', time.localtime(timestamp)))
    
    def get_level(self):
        """ Return the current log level of the logger. """
        return self.level
    
    def set_level(self, level):
        """ Set the current log level of the logger. """
        self.level = level
    
    def time(self, timestamp=None):
        """ Return the time formatted according to `stamp`. """
        return time.strftime(self.stamp, time.localtime(timestamp))
    
    def display(self, level, message, timestamp=None, **kwargs):
        """ Display the message on the screen. """
        msg = '{0}{1}\n'.format(self.time(timestamp), message)
        
        if self.get_level() <= level:
            self.stdout(msg)
        
        self.save(message, timestamp, **kwargs)
    
    def error(self, message, timestamp=None, **kwargs):
        """ Display an error message. """
        self.display(LEVEL.ERROR,
            'ERROR| {0}'.format(message),
            timestamp or time.time(),
            **kwargs
        )
    
    def warning(self, message, timestamp=None, **kwargs):
        """ Display a warning. """
        self.display(LEVEL.WARNING,
            'WARNING| {0}'.format(message),
            timestamp or time.time(),
            **kwargs
        )
    
    def message(self, message, timestamp=None, **kwargs):
        """ Display a message. """
        self.display(LEVEL.MESSAGE,
            ' {0}'.format(message),
            timestamp or time.time(),
            **kwargs
        )
    
    def debug(self, message, timestamp=None, **kwargs):
        """ Display a debug message. """
        self.display(LEVEL.DEBUG,
            'DEBUG| {0}'.format(message),
            timestamp or time.time(),
            **kwargs
        )
    
    def save(self, message, timestamp=None, **kwargs):
        """ Save the given message to a log file. """
        if not self.save_logs or not self.save_folder:
            return
        
        if not os.path.exists(self.save_folder):
            os.mkdir(self.save_folder, 0o755)
        
        with open(self._fname(timestamp, **kwargs), 'a') as file:
            file.write('{0}{1}\n'.format(self.time(timestamp), message))


class BufferedLogger(BaseLogger):
    """ Buffered logger.
        
        This logging object does not instantly save messages. Instead, messages
        are placed in a queue, and only saved when the `push` method is called.
        
        Typically, no programs should use this object unless greater control is
        needed when saving messages.
    """
    
    queue = None
    default_push = None
    
    def __init__(self, default_push=5, *args, **kwargs):
        super(BufferedLogger, self).__init__(*args, **kwargs)
        self.queue = Queue()
        self.default_push = default_push
    
    def _display(self, lower, message, timestamp, **kwargs):
        """ Display the message. """
        if lower:
            return
        
        self.stdout('{0}{1}\n'.format(self.time(timestamp), message))
    
    def _save(self, fname, chunk):
        """ Save multiple log messages to a single file. """
        with open(fname, 'a') as file:
            for data in chunk:
                file.write('{0}{1}\n'.format(self.time(data[3]), data[2]))
    
    def display(self, level, message, timestamp=None, **kwargs):
        """ Buffered display method. """
        data = (self.get_level(), level, message, timestamp or time.time(), kwargs)
        self._display(data[0] > data[1], data[2], data[3], **data[4])
        self.queue.put(data)
    
    def push(self, limit=None):
        """ Push some queued items out of the queue.
            
            This method causes queued items to be written to be saved to a file.
            
            Only `limit` items will be pushed out of the queue. If `limit` is
            `0`, then all items will be pushed from the queue.
        """
        if limit is None:
            limit = self.default_push
        
        if limit < 0:
            return
        
        if self.queue.empty():
            return
        
        sdata = {}
        iter = 0
        
        # First we sort the data we want into lists of messages that will be
        # saved in the same file. This way we don't have to keep opening and
        # closing files.
        while not self.queue.empty():
            item = self.queue.get()
            fname = self._fname(item[3], **item[4])
            
            try:
                sdata[fname].append(item)
            except KeyError:
                sdata[fname] = []
                sdata[fname].append(item)
            
            iter+= 1
            
            if limit == iter:
                break
        
        # The following two lines make the above loop pointless save for the
        # purpose of syphoning the queue.
        if not self.save_logs:
            return
        
        for fname in sdata:
            self._save(fname, sdata[fname])


class ThreadedLogger(BufferedLogger):
    """ A logger which actively runs in a thread.
        
        As with the `BufferedLogger` object, messages are not instantly saved
        to files. The difference here being that a thread is used to automate
        calls to `push`.
        
        With this, application developers shouldn't have to worry about whether
        or not all messages have been written to files.
    """
    
    control = None
    stop_loop = False
    
    def __init__(self, *args, **kwargs):
        super(ThreadedLogger, self).__init__(*args, **kwargs)
        self.level_lock = BoundedSemaphore()
        self.stop_loop = False
    
    def get_level(self):
        """ Return the current logging level. This blocks when threaded. """
        self.level_lock.acquire()
        l = self.level
        self.level_lock.release()
        return l
    
    def set_level(self, level):
        """ Set the current logging level. This blocks when threaded. """
        self.level_lock.acquire()
        self.level = level
        self.level_lock.release()
    
    def start(self):
        """ Start logging things in a thread. """
        self.stop_loop = False
        self.control = Thread(target=self.main)
        self.control.start()
    
    def stop(self):
        """ Tell the logger to stop running in a thread. """
        if self.control is None:
            return
        
        self.stop_loop = True
    
    def join(self, *args, **kwargs):
        """ Shortcut for `Thread.join`. """
        if self.control is None or self.stop_loop is False:
            return
        
        self.control.join(*args, **kwargs)
    
    def is_running(self):
        """ Determine whether or not the logger is running in a thread. """
        if self.control is None:
            return False
        
        return self.control.is_alive()
    
    def main(self):
        """ Main loop for the logger. """
        while True:
            time.sleep(2)
            self.push()
            if self.stop_loop:
                break
        
        self.stop_loop = False
        self.control = None
    


# EOF
