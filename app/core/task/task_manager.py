from abc import ABC, abstractmethod



class TaskManager(ABC):
    def __init__(self):
        ...

    @abstractmethod
    def trigger(self, task):
        ...