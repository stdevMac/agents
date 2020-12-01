# Proyecto de Simulacion

## Agentes 

## Marcos Antonio Maceo Reyes, Grupo 2

### Principales ideas seguidas para la implementacion del Sistema

Basandonos en la bibliografia dada, decidimos implementar el trabajo en python. Nos guiamos por las siguientes pautas
para dar respuesta a la simulacion:
1. Se modelan los elementos del entorno de forma tal que se generen lo mas aleatoriamente posible
2. Adicionamos al entorno el comportamiento de los Bebes
3. Adicionamos el comportamiento de los robots



### Modelos de Agentes considerados

### Ideas seguidas en la implementacion

Para la implementacion nos basamos 2 modulos fundamentales:
`types_defined`: Este contiene el conjunto de clases y es aqui donde se define el comportamiento de cadas una de las 
celdas del tablero. En este modulo se encuentran implementadas las siguientes clases:
    `Cell`: Clase basica que representa una celda basica, esta representa una celda abstracta y contiene metodos 
    comunes a todas las clases que se describen a continuacion:
    `Blank`: Representa una casilla en blanco en nuestro tablero
    `Obstacle`: Representa un obstaculo en el tablero
    `Dirt`: Representa que una casilla contenga basura
    `Corral`: Representa al los corrales que van a contener luego a los bebes
    `Child`: Representa en nuestro tablero una casilla que contiene un bebe.
    `Robot`: Esta es la clase basica de nuestros agentes. Estos heredan directamente de esta y esta a su vez contiene todos
    los metodos y elementos comunes de nuestros agentes.
    `RobotOne`: Representa nuestro primer agente, el cual tiene una mezcla entre agente proactivo y reactivo, en consecuencia
    con sus necesidades
    `RoborTwo`: De forma semejante a su compannero, este Agente mezcla caracteristicas de agentes proactivos con reactivos
    para obtener los mejores resultados.
    
`Board`: Este modulo contiene las reglas generales de la simulacion.

Los elementos del trablero se generan en el siguiente orden:
1. Se acomodan los corrales
2. Se acomodan los bebes
3. Se acomoda la basura
4. Se acomodan los obstaculos
5. Se posiciona al robot.

Una celda del ambiente esta representada por alguna de las clases listadas en el modulo `types_defined`. Cada una de 
estas clases para una mejor representacion visual, se usaron emojis para diferenciar algunos de los estados de la 
simulacion.

Asi luce un tablero recien creado:
*Adjuntar imagen*


    
### Consideraciones obtenidas


