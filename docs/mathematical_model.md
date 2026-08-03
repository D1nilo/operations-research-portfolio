# Modelo Matemático

## Tipo de Modelo

Mixed Integer Linear Programming (MILP)

---

# Objetivo

Determinar la combinación óptima de cargas que deben ser transportadas en un vuelo para maximizar el ingreso total, respetando las restricciones operacionales de la aeronave.

---

# Conjuntos

Sea:

- **I** = Conjunto de cargas disponibles.

Cada elemento **i ∈ I** representa una carga candidata para ser transportada.

---

# Parámetros

Cada carga posee los siguientes atributos:

- **peso_i** : Peso de la carga i.
- **volumen_i** : Volumen de la carga i.
- **ingreso_i** : Ingreso esperado de la carga i.
- **prioridad_i** : Prioridad logística de la carga i.

Parámetros del avión:

- **PesoMáximo**
- **VolumenMáximo**
- **CantidadMínimaPrioridadAlta**

---

# Variable de Decisión

Para cada carga i se define:

xᵢ

Donde:

- xᵢ = 1 → La carga será transportada.
- xᵢ = 0 → La carga no será transportada.

---

# Función Objetivo

Maximizar el ingreso total obtenido por las cargas seleccionadas.

---

# Restricciones

## Restricción de Peso

El peso total de las cargas seleccionadas no puede superar la capacidad máxima del avión.

---

## Restricción de Volumen

El volumen total de las cargas seleccionadas no puede superar la capacidad máxima disponible.

---

## Restricción de Prioridad

Debe seleccionarse al menos una cantidad mínima de cargas con prioridad alta.

---

## Restricción Binaria

Cada carga solamente puede:

- Ser seleccionada.
- No ser seleccionada.

No existen valores intermedios.

---

# Salidas Esperadas

El modelo debe entregar:

- Lista de cargas seleccionadas.
- Peso total utilizado.
- Volumen total utilizado.
- Ingreso total.
- Capacidad utilizada.
- Estado de la solución.