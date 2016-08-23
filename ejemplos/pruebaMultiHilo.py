import threading
import time
def worker():
    for i in range (0,8):
        print('Ejecutando hilo ' + threading.currentThread().getName() + str(i))
        time.sleep(2)
    
def servicio():
    print (threading.currentThread().getName(), 'Lanzado')
    print (threading.currentThread().getName(), 'Deteniendo')

t = threading.Thread(target=servicio, name='Servicio')
w = threading.Thread(target=worker, name='Trabajo')
w.start()
t.start()
time.sleep(20)