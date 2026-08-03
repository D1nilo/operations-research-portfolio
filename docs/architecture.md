# Arquitectura de la Solución

## Objetivo

Definir una arquitectura modular y mantenible para el proyecto de optimización de carga aérea, separando claramente la lectura de datos, validación, construcción del modelo, resolución y presentación de resultados.

---

## Flujo General

```text
Archivos de entrada
        │
        ▼
Carga de datos
        │
        ▼
Validación de datos
        │
        ▼
Construcción del modelo MILP
        │
        ▼
Ejecución del solver
        │
        ▼
Procesamiento de resultados
        │
        ▼
Visualización y reportes
```

---

## Componentes

### 1. Datos de entrada

Los datos del proyecto se almacenan en:

```text
data/
├── raw/
├── processed/
└── sample/
```

- `raw/`: datos originales sin modificar.
- `processed/`: datos transformados y validados.
- `sample/`: datos pequeños utilizados para demostraciones y pruebas.

---

### 2. Configuración

Los parámetros operacionales se almacenan en:

```text
configs/
```

Ejemplos:

- Capacidad máxima de peso.
- Capacidad máxima de volumen.
- Cantidad mínima de cargas prioritarias.
- Identificador de la aeronave.

---

### 3. Carga de datos

Archivo responsable:

```text
data_loader.py
```

Responsabilidades:

- Leer archivos CSV.
- Verificar la existencia de los archivos.
- Convertir los datos a estructuras utilizables.
- Entregar los datos al módulo de validación.

---

### 4. Validación de datos

Archivo responsable:

```text
data_validation.py
```

Responsabilidades:

- Verificar columnas obligatorias.
- Validar tipos de datos.
- Detectar valores nulos.
- Validar identificadores duplicados.
- Comprobar valores negativos o inconsistentes.
- Detener la ejecución si los datos no cumplen las reglas.

---

### 5. Configuración del modelo

Archivo responsable:

```text
config.py
```

Responsabilidades:

- Leer parámetros desde archivos JSON.
- Validar configuraciones.
- Entregar los límites operacionales al modelo.

---

### 6. Modelo MILP

Archivo responsable:

```text
model.py
```

Responsabilidades:

- Crear las variables de decisión.
- Definir la función objetivo.
- Incorporar las restricciones de peso.
- Incorporar las restricciones de volumen.
- Incorporar las restricciones de prioridad.
- Entregar el modelo configurado al solver.

---

### 7. Resolución del modelo

Archivo responsable:

```text
solver.py
```

Responsabilidades:

- Ejecutar el solver.
- Interpretar el estado de la solución.
- Detectar soluciones óptimas, factibles o inviables.
- Recuperar los valores de las variables de decisión.
- Entregar los resultados para su procesamiento.

---

### 8. Procesamiento de resultados

Archivo responsable:

```text
results.py
```

Responsabilidades:

- Identificar las cargas seleccionadas.
- Calcular el ingreso total.
- Calcular el peso utilizado.
- Calcular el volumen utilizado.
- Calcular porcentajes de utilización.
- Preparar los resultados para reportes y visualizaciones.

---

### 9. Visualización

Archivo responsable:

```text
visualization.py
```

Responsabilidades:

- Generar gráficos de utilización de capacidad.
- Comparar cargas seleccionadas y no seleccionadas.
- Mostrar distribución de ingresos.
- Guardar figuras en `reports/figures/`.

---

### 10. Orquestación

Archivo responsable:

```text
main.py
```

Responsabilidades:

- Coordinar el flujo completo.
- Cargar configuración y datos.
- Ejecutar validaciones.
- Construir el modelo.
- Resolver el problema.
- Procesar resultados.
- Generar salidas.

---

## Estructura Técnica

```text
operations-research-portfolio/
├── configs/
├── data/
├── docs/
├── notebooks/
├── reports/
├── src/
│   └── airline_cargo_optimization/
│       ├── __init__.py
│       ├── config.py
│       ├── data_loader.py
│       ├── data_validation.py
│       ├── main.py
│       ├── model.py
│       ├── results.py
│       ├── solver.py
│       └── visualization.py
├── tests/
├── README.md
└── requirements.txt
```

---

## Principios de Diseño

La solución seguirá los siguientes principios:

- Separación de responsabilidades.
- Código modular y reutilizable.
- Validación temprana de errores.
- Configuración externa al código.
- Reproducibilidad.
- Pruebas automatizadas.
- Documentación técnica.
- Trazabilidad de resultados.

---

## Evolución Futura

La arquitectura permitirá incorporar posteriormente:

- Múltiples aeronaves.
- Múltiples vuelos.
- Distintos destinos.
- Compatibilidad entre cargas.
- Costos operacionales.
- Penalizaciones por carga rechazada.
- Optimización de rutas.
- Integración con APIs.
- Despliegue en la nube.