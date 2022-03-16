from multiprocessing import Process
from multiprocessing import Condition, Lock, Value
from multiprocessing import Array, Manager
import time
import random

class Table():
    def __init__(self, nphil, manager):
        self.nphil = nphil
        self.phil = None
        self.mutex = Lock()
        self.tenedores = Array('i',[-1 for _ in range(nphil)])
        self.tenedores_libres = Condition(self.mutex)

    def puede_comer(self):
        return self.tenedores[self.phil] == -1 and self.tenedores[(self.phil-1)%self.nphil] == -1

    def wants_eat(self, num):
        self.mutex.acquire()
        self.tenedores_libres.wait_for(lambda: self.puede_comer())
        self.tenedores[self.phil] = self.phil
        self.tenedores[(self.phil-1)%self.nphil] = self.phil
        self.mutex.release()

    def wants_think(self, num):
        self.mutex.acquire()
        self.tenedores[self.phil] = -1
        self.tenedores[(self.phil-1)%self.nphil] = -1
        self.tenedores_libres.notify()
        self.mutex.release()

    def set_current_phil(self, num):
        self.phil = num

    def get_current_phil(self):
        return self.phil


class CheatMonitor():
    def __init__(self):
        self.comiendo = Value('i', 0)
        self.mutex = Lock()
        self.pensar_libre = Condition(self.mutex)

    def puede_pensar(self):
        return self.comiendo.value == 2

    def wants_think(self, nphil):
        self.mutex.acquire()
        self.pensar_libre.wait_for(lambda: self.puede_pensar())
        self.comiendo.value -= 1
        self.mutex.release()

    def is_eating(self, nphil):
        self.mutex.acquire()
        self.comiendo.value += 1
        self.pensar_libre.notify()
        self.mutex.release()

class AnticheatTable():
    def __init__(self, nphil, manager):
        self.nphil = nphil
        self.phil = None
        self.mutex = Lock()
        self.tenedores = Array('i',[-1 for _ in range(nphil)])
        self.tenedores_libres = Condition(self.mutex)

    # come si el siguiente tambien puede comer
    def puede_comer(self):
        return self.tenedores[self.phil] == -1 \
            and self.tenedores[(self.phil-1)%self.nphil] == -1 \
            and self.tenedores[(self.phil+1)%self.nphil] == -1

    def wants_eat(self, num):
        self.mutex.acquire()
        self.tenedores_libres.wait_for(lambda: self.puede_comer())
        self.tenedores[self.phil] = self.phil
        self.tenedores[(self.phil-1)%self.nphil] = self.phil
        self.mutex.release()

    def wants_think(self, num):
        self.mutex.acquire()
        self.tenedores[self.phil] = -1
        self.tenedores[(self.phil-1)%self.nphil] = -1
        self.tenedores_libres.notify()
        self.mutex.release()

    def set_current_phil(self, num):
        self.phil = num

    def get_current_phil(self):
        return self.phil