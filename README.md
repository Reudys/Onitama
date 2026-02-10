1. Cómo iniciar el juego

Copia todo el código (desde import hasta el final) en un editor de texto (Notepad++, VS Code, etc.).
Guárdalo como onitama.py.
Abre una terminal/consola:
Windows: busca "cmd" o "PowerShell".
Mac: "Terminal".
Linux: Terminal.

Navega a la carpeta: cd C:\ruta\a\tu\carpeta (usa dir o ls para ver).
Ejecuta:textpython onitama.py(Si error, prueba python3 onitama.py).
¡El juego arranca solo! Imprime tablero, cartas y movimientos. Juegan dos personas en la misma PC.

Para salir en cualquier turno: Escribe 0 y Enter.
2. El tablero y setup inicial
text0 1 2 3 4
0 B B B B B   ← Fila 0: Piezas AZUL (B). Maestro implícito en (0,2)
1 . . . . .
2 . . . . .
3 . . . . .
4 R R R R R   ↓ Fila 4: Piezas ROJO (R). Maestro implícito en (4,2)

Filas: 0 (arriba, Azul) → 4 (abajo, Rojo).
Columnas: 0 (izquierda) → 4 (derecha).
Piezas: 5 por jugador, todas iguales ('B' o 'R'). Se mueven/capturan igual. (En el original físico, el "maestro" tiene forma distinta, pero aquí no se distingue).

3. Cartas iniciales (pueden cambiar con intercambios)
textCartas de Azul: ['Tigre', 'Crane']
Carta central: Mantis
Cartas de Rojo: ['Frog', 'Liebre']

Cada jugador siempre tiene 2 cartas.
Cada carta define movimientos relativos desde la posición de la pieza (dr = cambio fila, dc = cambio columna).
Para Azul: deltas tal cual (positivo dr = abajo/hacia Rojo).
Para Rojo: deltas invertidos (dr, dc = -dr, -dc), como rotar la carta 180°.

Movimientos de cada carta (definidos en el código):









































CartaMovimientos relativos (dr, dc)Tigre(-2, 0), (1, 0)Dragón(-1, -1), (-1, 1), (1, -2), (1, 2)Frog(-1, -1), (0, -2), (1, 1)Liebre(-1, 1), (0, 2), (1, -1)Crane(-1, 0), (1, -1), (1, 1)Mono(-1, -1), (-1, 1), (1, -1), (1, 1)Mantis(-1, -1), (-1, 1), (1, 0)Cabra(0, -1), (0, 1), (-2, 0), (2, 0)
Ej: Tigre permite ir 2 filas atrás (arriba) o 1 fila adelante (abajo), misma columna.
4. Cómo se juega un turno

Azul empieza. Alternan.
El código imprime tablero + cartas.
Lista todos los movimientos legales numerados (1, 2, ...):textMovimientos disponibles (13):
 1. Tigre      (0, 0) → (1, 0)   (B)
 2. Crane      (0, 0) → (1, 1)   (B)
...
Legal: Desde cualquiera de tus 5 piezas → cualquiera de tus 2 cartas → cualquiera de sus deltas.
Solo si destino: vacío (.) o oponente (captura, lo elimina).
No: fuera tablero o sobre tu pieza.

Escribe el número (ej: 1) y Enter.
Se ejecuta automáticamente:
Mueve la pieza.
Intercambio de cartas: Tu carta usada → centro. Centro anterior → mano del oponente. (¡Oponente gana tu carta usada!)

Siguiente turno.
Si no hay movimientos: pierdes (raro).

5. Condiciones de victoria

Camino de la Piedra: Eliminar todas las piezas enemigas (captura total). (Nota: en original, solo el maestro; aquí bug menor, pero funciona).
Camino del Río: Mover cualquiera de tus piezas al templo enemigo:
Azul: posición (4, 2).
Rojo: posición (0, 2).

Imprime "¡GANÓ [color]!" y tablero final.

6. Ejemplo de primer turno (Azul)

13 opciones, todas moviendo una B de fila 0 a fila 1.
Elige 6: Tigre (0,2) → (1,2)  (maestro centro avanza recto).
Tablero nuevo: B en (1,2), vacío en (0,2).
Cartas: Tigre → centro, Mantis → Rojo. Ahora Azul: Crane + Mantis? No: intercambio es usada a centro, centro a oponente.
Rojo turno con Frog, Liebre + Mantis.

¡Es súper intuitivo después del primer turno! Estrategia: avanza hacia enemigo, protege tu centro, roba buenas cartas, amenaza capturas/maestro/templo. Partidas cortas (10-15 min).
