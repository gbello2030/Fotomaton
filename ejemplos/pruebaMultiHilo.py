import threading
import time

seguir = True

def worker(repeticiones, otroArg):
    global seguir
    print(otroArg)
    for i in range (0,repeticiones):
        print('Ejecutando hilo ' + threading.currentThread().getName() + str(i))
        time.sleep(2)
    print("Fin del hilo")
    seguir = False
    
def servicio():
    print (threading.currentThread().getName(), 'Lanzado')
    print (threading.currentThread().getName(), 'Deteniendo')

t = threading.Thread(target=servicio, name='Servicio')
w = threading.Thread(target=worker, name='Trabajo', args=(2,'imprime',))
w.start()
t.start()

while seguir :
    t = threading.Thread(target=servicio, name='Servicio')
    time.sleep(0.5)
    t.start()