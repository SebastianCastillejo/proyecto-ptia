# Agrupamiento de ingredientes

Coocurrencia receta-receta normalizada por fila; K-means se compara mediante inercia (codo) y silueta. El k informado maximiza silueta. Los pares candidatos son del mismo clúster y se observan juntos en ≤0,1% de recetas; requieren validación culinaria.

|   k |   inercia |   silueta |
|----:|----------:|----------:|
|   2 |   363.331 | 0.207547  |
|   3 |   345.59  | 0.123296  |
|   4 |   333.767 | 0.110998  |
|   5 |   324.941 | 0.078629  |
|   6 |   319.138 | 0.051261  |
|   7 |   314.971 | 0.07399   |
|   8 |   309.317 | 0.0584193 |
|   9 |   305.349 | 0.031246  |
|  10 |   301.992 | 0.0529808 |

Candidatos exportados: 500.

![Método del codo](codo.png)
