# Juri - Chatbot creador de contratos de compraventa de veh铆culos

## 馃弰 Introducci贸n

## 馃懛 Instalaci贸n

1. Se debe dar permisos de ejecuci贸n al fichero `Install`
    
    `chmod u+x Install`
    
2. Ejecutar el fichero
    `./Install`

(Esto puede tardar varios minutos dependiendo de la conexi贸n a Internet)

## 馃 Ejecutar Juri

1. Se debe dar permisos de ejecuci贸n al fichero `Run`
    
    `chmod u+x Run`
    
2. Ejecutar el fichero
    `./Run`
3. Dirigirse a http://localhost:8001
    
**NOTA** 

A la hora de matar los procesos puede que alguno persista y siga escuchando en un determinado puerto. Algunos comandos que peuden resultar de ayuda son:

`ss -ltn` Muestra que puertos estan a la escucha

``sudo kill -9 `sudo lsof -t -i:PORT` `` Mata a un proceso escuchando en un determinado puerto

Puertos que usa la aplicaci贸n: `5005`, `5055`, `8000`, y `8001`



## 馃摐 Licencia


