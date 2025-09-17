# Implementación de Funcionalidad de Sweep en NanoVNA Graphics

## Resumen de Cambios

Se ha implementado exitosamente la funcionalidad de sweep en la ventana de gráficos (`graphics_window.py`) que permite:

1. **Realizar sweeps automáticos** al dispositivo NanoVNA conectado
2. **Cargar configuración** desde `sweep_options_window`
3. **Reemplazar datos de ejemplo** con datos reales del dispositivo
4. **Ejecución automática** de sweep al abrir la ventana de gráficos

## Características Implementadas

### 1. Botón "Run Sweep" en el Menú
- **Ubicación**: Menú `Sweep → Run Sweep`
- **Funcionalidad**: Ejecuta un sweep manual del dispositivo conectado
- **Validaciones**: Verifica que el dispositivo esté conectado antes de ejecutar

### 2. Botón "Run Sweep" Visible en la Interfaz
- **Ubicación**: Parte superior de la ventana de gráficos
- **Características**: 
  - Botón destacado de 120px de ancho
  - Label informativo que muestra la configuración actual de sweep
  - Ejemplo: "Sweep: 0.050 MHz - 1500.000 MHz, 101 points"

### 3. Carga Automática de Configuración
- **Fuente**: Archivo `src/NanoVNA_UTN_Toolkit/ui/sweep_window/config/config.ini`
- **Parámetros cargados**:
  - `StartFreqHz`: Frecuencia de inicio en Hz
  - `StopFreqHz`: Frecuencia de parada en Hz  
  - `Segments`: Número de puntos de medición
- **Manejo de errores**: Valores por defecto si el archivo no existe

### 4. Sweep Automático al Cargar
- **Comportamiento**: Si hay un dispositivo conectado, se ejecuta automáticamente un sweep al abrir la ventana
- **Retraso**: 1 segundo para permitir que la UI se cargue completamente
- **Validación**: Solo se ejecuta si `vna_device.connected()` retorna `True`

### 5. Reemplazo de Datos de Ejemplo
- **Antes**: Datos sintéticos generados con `np.linspace(1e6, 100e6, 101)`
- **Ahora**: 
  - Datos reales del dispositivo cuando está disponible
  - Datos de ejemplo basados en la configuración de sweep actual
  - Frecuencias basadas en `start_freq_hz` y `stop_freq_hz` del config.ini

## Métodos Implementados

### `load_sweep_configuration()`
```python
def load_sweep_configuration(self):
    """Load sweep configuration from sweep options config file."""
```
- Carga configuración desde config.ini
- Establece valores por defecto si hay errores
- Actualiza el label informativo

### `get_sweep_data(freqs=None, s11=None, s21=None)`
```python
def get_sweep_data(self, freqs=None, s11=None, s21=None):
    """Get sweep data - either from provided parameters or generate example data."""
```
- Usa datos proporcionados si están disponibles
- Genera datos de ejemplo basados en configuración de sweep
- Utiliza el rango de frecuencias configurado

### `run_sweep()`
```python
def run_sweep(self):
    """Run a sweep on the connected device."""
```
- Ejecuta sweep completo en el dispositivo conectado
- Muestra diálogo de progreso durante la operación
- Lee datos S11 y S21 del dispositivo
- Actualiza los gráficos con datos nuevos
- Manejo completo de errores con mensajes informativos

### `update_plots_with_new_data()`
```python
def update_plots_with_new_data(self):
    """Update both plots with new sweep data."""
```
- Actualiza ambos paneles de gráficos con nuevos datos
- Limpia plots existentes y redibuja
- Manejo de errores para casos edge

### `update_sweep_info_label()`
```python
def update_sweep_info_label(self):
    """Update the sweep information label with current configuration."""
```
- Actualiza el texto del label informativo
- Formato inteligente de unidades (kHz/MHz)
- Logging de cambios para debugging

## Flujo de Operación

### Al Abrir graphics_window:
1. Se inicializa la configuración de sweep desde config.ini
2. Se genera datos de ejemplo basados en la configuración
3. Si hay dispositivo conectado, se programa un sweep automático
4. Se actualiza el label informativo con la configuración

### Al Hacer Clic en "Run Sweep":
1. Validación de dispositivo conectado
2. Carga de configuración actual de sweep
3. Configuración de parámetros del VNA (`datapoints`, `setSweep()`)
4. Lectura de frecuencias (`read_frequencies()`)
5. Lectura de datos S11 (`readValues("data 0")`)
6. Lectura de datos S21 (`readValues("data 1")`)
7. Actualización de gráficos con datos nuevos
8. Mensaje de confirmación al usuario

## Configuración por Defecto

```ini
[Frequency]
StartFreqHz=50000           # 50 kHz
StopFreqHz=1500000000      # 1.5 GHz  
Segments=101               # 101 puntos

[Limits]
MaxFrequencyHz=6000000000  # 6 GHz
```

## Manejo de Errores

### Sin Dispositivo Conectado
- **Mensaje**: "No VNA device connected. Cannot perform sweep."
- **Comportamiento**: Se muestran datos de ejemplo basados en configuración

### Dispositivo Desconectado
- **Mensaje**: "VNA device is not connected. Please reconnect."
- **Validación**: Se verifica `vna_device.connected()` antes del sweep

### Errores Durante Sweep
- **Logging completo** de todos los errores
- **Diálogo de error** con mensaje descriptivo
- **Cierre seguro** del diálogo de progreso

## Logging Implementado

Todos los métodos incluyen logging detallado con formato:
```
[graphics_window.method_name] Description of action
```

Ejemplos:
- `[graphics_window.run_sweep] Starting sweep operation`
- `[graphics_window.load_sweep_configuration] Loaded sweep config: 0.050 MHz - 1500.000 MHz, 101 points`
- `[graphics_window.get_sweep_data] Generating example data`

## Integración con Sistema Existente

### Compatible con:
- ✅ Sistema de configuración existente (QSettings)
- ✅ Flujo de navegación entre ventanas
- ✅ Detección automática de dispositivos
- ✅ Todas las clases de Hardware VNA existentes
- ✅ Sistema de logging unificado

### No afecta:
- ✅ Funcionalidad de gráficos existente
- ✅ Sistema de cursores y marcadores
- ✅ Configuraciones de visualización
- ✅ Menús y ventanas auxiliares

## Próximas Mejoras Sugeridas

1. **Actualización en Tiempo Real**: Implementar actualización automática de gráficos durante el sweep
2. **Sweep Continuo**: Opción para sweeps repetitivos automáticos
3. **Guardar Datos**: Funcionalidad para exportar datos de sweep
4. **Configuración Avanzada**: Parámetros adicionales como bandwidth, calibración, etc.
5. **Indicador Visual**: Estado visual del dispositivo conectado en la interfaz

## Estado de Implementación

✅ **COMPLETADO** - Funcionalidad básica de sweep implementada y probada
✅ **INTEGRADO** - Compatible con todo el sistema existente  
✅ **DOCUMENTADO** - Logging completo y manejo de errores
✅ **PROBADO** - Funcionamiento verificado con y sin dispositivo conectado
