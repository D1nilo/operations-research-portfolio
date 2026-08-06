# ✈️ Operations Research Portfolio

## Airline Cargo Optimization using Python, MILP & Google OR-Tools

> Solución de optimización desarrollada en Python para maximizar el ingreso de una aeronave mediante técnicas de **Mixed Integer Linear Programming (MILP)** y **Google OR-Tools**, aplicando buenas prácticas de ingeniería de software, validación de datos y pruebas automatizadas.

---

# 📌 Descripción

Este proyecto forma parte de mi portafolio profesional de **Data Science** y **Operations Research**, donde desarrollo soluciones orientadas a resolver problemas reales de optimización utilizando modelado matemático, programación lineal entera mixta (MILP) y herramientas de ingeniería de software.

El objetivo del proyecto es construir una solución modular, mantenible y escalable que permita optimizar la selección y asignación de carga considerando múltiples restricciones operacionales.

---

# 🚀 Funcionalidades

Actualmente el proyecto incorpora:

- ✅ Optimización mediante Mixed Integer Linear Programming (MILP)
- ✅ Maximización del ingreso esperado
- ✅ Restricciones por capacidad de peso
- ✅ Restricciones por capacidad de volumen
- ✅ Asignación de carga por compartimientos
- ✅ Restricciones para mercancías peligrosas
- ✅ Soporte para cadena de frío
- ✅ Compatibilidad e incompatibilidad entre cargas
- ✅ Restricciones por rutas y destinos
- ✅ Validación de datos
- ✅ Validación de reglas de negocio
- ✅ Exportación automática de resultados
- ✅ Generación de visualizaciones
- ✅ Arquitectura modular
- ✅ Pruebas automatizadas

---

# 🏗️ Arquitectura del Proyecto

```text
operations-research-portfolio
│
├── configs/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── docs/
│
├── notebooks/
│
├── reports/
│   ├── figures/
│   └── results/
│
├── src/
│   └── airline_cargo_optimization/
│       ├── config.py
│       ├── data_loader.py
│       ├── data_validation.py
│       ├── exporter.py
│       ├── model.py
│       ├── results.py
│       ├── solver.py
│       ├── visualization.py
│
├── tests/
│
├── README.md
├── requirements.txt
└── pytest.ini
```

---

# 🔄 Flujo de la Solución

```text
Carga de datos
        │
        ▼
Validación de datos
        │
        ▼
Reglas de negocio
        │
        ▼
Modelo MILP
        │
        ▼
Google OR-Tools
        │
        ▼
Solución óptima
        │
        ▼
Exportación de resultados
        │
        ├── CSV
        ├── JSON
        └── Visualizaciones
```

---

# 🧠 Tecnologías Utilizadas

## Lenguaje

- Python 3.12

## Optimización

- Google OR-Tools
- SCIP Solver
- Mixed Integer Linear Programming (MILP)

## Ciencia de Datos

- Pandas

## Visualización

- Matplotlib

## Calidad de Código

- Ruff

## Testing

- Pytest

## Control de Versiones

- Git
- GitHub

---

# 📊 Resultados Generados

El proyecto genera automáticamente:

```text
reports/
│
├── figures/
│   ├── capacity_utilization.png
│   └── selected_cargo_revenue.png
│
└── results/
    ├── selected_cargo.csv
    └── solution_summary.json
```

Los resultados incluyen:

- Ingreso total optimizado.
- Peso total utilizado.
- Volumen utilizado.
- Utilización porcentual de capacidad.
- Métricas técnicas del solver.
- Cargas seleccionadas.
- Visualizaciones automáticas.

---

# 🧪 Testing

El proyecto cuenta con pruebas automatizadas para validar:

- Configuración
- Validación de datos
- Modelo matemático
- Solver
- Resultados
- Exportaciones
- Visualizaciones
- Reglas de negocio

Ejecutar todas las pruebas:

```bash
pytest
```

---

# ⚙️ Instalación

Clonar el repositorio:

```bash
git clone https://github.com/D1nilo/operations-research-portfolio.git
```

Ingresar al proyecto:

```bash
cd operations-research-portfolio
```

Crear entorno virtual:

```bash
python -m venv .venv
```

Activar entorno (Windows):

```bash
.venv\Scripts\activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

# ▶️ Ejecución

```bash
python -m airline_cargo_optimization.main
```

---

# 📁 Salida Esperada

Después de ejecutar el modelo se generan automáticamente:

- Resultados optimizados en CSV.
- Resumen técnico en JSON.
- Visualizaciones.
- Indicadores de capacidad.
- Métricas del solver.

---

# 📚 Conceptos Aplicados

- Operations Research
- Mixed Integer Linear Programming (MILP)
- Binary Optimization
- Constraint Programming
- Data Validation
- Business Rules
- Clean Code
- Automated Testing
- Software Engineering

---

# 📈 Roadmap

Próximas funcionalidades:

- 🔄 Orden de descarga por escalas
- 🔄 Dashboard interactivo con Streamlit
- 🔄 Benchmark con heurísticas
- 🔄 Análisis de sensibilidad
- 🔄 Múltiples aeronaves
- 🔄 Escenarios operacionales
- 🔄 KPIs logísticos
- 🔄 Reporte ejecutivo automático

---

# 👨‍💻 Autor

**Daniel Bastián Nilo Palacios**

GitHub:
https://github.com/D1nilo

LinkedIn:
*(Agregar enlace cuando publiques el proyecto)*

---

# ⭐ Objetivo

Este proyecto busca demostrar la aplicación de técnicas de **Data Science**, **Operations Research** y **Optimization** para resolver problemas complejos mediante modelado matemático, desarrollo de software y buenas prácticas de ingeniería.

Además del algoritmo de optimización, el proyecto enfatiza aspectos como la calidad del código, la validación de datos, la automatización de pruebas y la construcción de soluciones mantenibles y reproducibles.