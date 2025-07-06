from abc import ABC, abstractmethod

class IEnvironmentBase(ABC): # TODO Do I need something like this?
    
    @abstractmethod
    def analyse(self):
        pass