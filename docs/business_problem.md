# Problema de Negocio

## Contexto

Una aerolínea de carga recibe diariamente múltiples solicitudes para transportar mercancías hacia diferentes destinos.

Cada solicitud posee características particulares, tales como:

- Peso.
- Volumen.
- Prioridad logística.
- Ingreso esperado.
- Tipo de carga.

Debido a que la capacidad del avión es limitada, no es posible transportar todas las cargas disponibles en un mismo vuelo.

Por esta razón, la empresa debe decidir qué cargas aceptar y cuáles dejar para vuelos posteriores.

---

# Problema

Actualmente la selección de carga puede realizarse mediante reglas simples o decisiones manuales.

Este enfoque puede generar:

- Pérdida de ingresos.
- Mala utilización de la capacidad del avión.
- Selección ineficiente de mercancías.
- Incumplimiento de prioridades operacionales.

---

# Objetivo del Negocio

Maximizar el ingreso generado por cada vuelo utilizando de forma eficiente la capacidad disponible del avión.

---

# Restricciones Operacionales

La solución deberá respetar las siguientes restricciones:

- Capacidad máxima de peso.
- Capacidad máxima de volumen.
- Cantidad mínima de carga prioritaria.
- Una carga solo puede ser seleccionada una vez.
- Las cargas no seleccionadas permanecerán disponibles para futuros vuelos.

---

# Beneficios Esperados

La implementación del modelo permitirá:

- Maximizar los ingresos por vuelo.
- Optimizar el uso de la capacidad del avión.
- Automatizar la selección de carga.
- Mejorar la toma de decisiones.
- Reducir errores asociados a decisiones manuales.

---

# Alcance

Este proyecto considera únicamente la selección óptima de carga para un único vuelo.

No se consideran:

- Optimización de rutas.
- Asignación de tripulación.
- Consumo de combustible.
- Costos operacionales.
- Múltiples aeronaves.

Estas funcionalidades podrán incorporarse en futuras versiones del proyecto.