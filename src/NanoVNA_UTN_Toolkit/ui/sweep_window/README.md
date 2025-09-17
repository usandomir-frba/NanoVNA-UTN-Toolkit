# Sweep Options Window

Esta ventana permite configurar los parámetros de sweep para el NanoVNA.

## Características

### Configuración de Frecuencia
- **Start Frequency**: Frecuencia de inicio del sweep con selección de unidades (Hz, kHz, MHz, GHz)
- **Stop Frequency**: Frecuencia de parada del sweep con selección de unidades (Hz, kHz, MHz, GHz)
- **Steps**: Número de pasos de medición en el sweep (limitado según el dispositivo conectado)

### Valores Calculados (Solo Lectura)
- **Center Frequency**: Punto medio entre las frecuencias de inicio y parada (con unidades automáticas)
- **Span**: Diferencia entre las frecuencias de parada e inicio (con unidades automáticas)
- **Hz/step**: Resolución de frecuencia por paso de medición (con unidades automáticas)

### Límites de Frecuencia
- **Frecuencia Máxima**: Configurable desde el archivo config.ini (por defecto 6 GHz)
- Este límite no es modificable desde la interfaz de usuario

### Límites de Steps (Específicos por Dispositivo)
- **Límites Automáticos**: Los rangos min/max de steps se ajustan automáticamente según el dispositivo VNA conectado
- **Información Visible**: Se muestra el dispositivo detectado y sus límites en la interfaz
- **Ejemplos de límites por dispositivo**:
  - NanoVNA-H4: 11-101 steps
  - SV4401A: 101-1001 steps  
  - LiteVNA64: 11-65535 steps
  - Sin dispositivo: 11-1001 steps (valores por defecto)

## Funcionalidades

### Botones
- **Apply**: Aplica y guarda la configuración actual
- **Cancel**: Cierra la ventana sin guardar cambios y restaura los valores originales
- **Reset to Defaults**: Restaura los valores por defecto

### Validaciones
- La frecuencia de inicio debe ser menor que la de parada
- La frecuencia de parada no puede exceder el límite máximo configurado
- El número de pasos debe estar dentro del rango permitido por el dispositivo conectado
- Se muestran advertencias específicas si los valores no son válidos para el dispositivo actual

### Comportamiento del Botón Cancel
- El botón **Cancel** descarta todos los cambios realizados en la sesión actual
- Restaura automáticamente los valores que estaban configurados al abrir la ventana
- No guarda ningún cambio en el archivo config.ini
- Los valores se restauran instantáneamente antes de cerrar la ventana

### Detección Automática de Dispositivos
- La ventana detecta automáticamente el dispositivo VNA conectado
- Los límites de steps se ajustan dinámicamente según las capacidades del dispositivo
- Si no se detecta dispositivo, se usan valores por defecto conservadores
- La información del dispositivo se muestra debajo del campo de steps

## Configuración

Los ajustes se guardan automáticamente en el archivo:
```
src/NanoVNA_UTN_Toolkit/ui/sweep_window/config/config.ini
```

### Estructura del archivo config.ini
```ini
[Frequency]
StartFreqHz=50000
StopFreqHz=1500000000
Segments=100
StartUnit=kHz
StopUnit=GHz

[Limits]
MaxFrequencyHz=6000000000
```

## Valores por Defecto
- **Start Frequency**: 50.0 kHz
- **Stop Frequency**: 1.5 GHz
- **Steps**: 100
- **Max Frequency**: 6.0 GHz (configurable solo desde config.ini)

## Configuración Avanzada

### Cambiar Límite de Frecuencia Máxima

Para cambiar el límite de frecuencia máxima permitida, edita el archivo `config.ini`:

```ini
[Limits]
MaxFrequencyHz=6000000000  # 6 GHz en Hz
```

Ejemplos de valores comunes:
- 1 GHz: `MaxFrequencyHz=1000000000`
- 3 GHz: `MaxFrequencyHz=3000000000` 
- 6 GHz: `MaxFrequencyHz=6000000000`
- 10 GHz: `MaxFrequencyHz=10000000000`

⚠️ **Nota**: Este límite solo puede ser modificado editando directamente el archivo config.ini, no desde la interfaz de usuario.

## Acceso desde el Menú Principal

La ventana se puede abrir desde el menú principal de NanoVNA Graphics:
```
Sweep → Options
```

## Prueba Independiente

Para probar la ventana de forma independiente, ejecuta:
```bash
cd src/NanoVNA_UTN_Toolkit/ui/sweep_window
python test_sweep_window.py
```

## Integración

La ventana está integrada con el sistema principal de NanoVNA Graphics y se puede acceder a través del método `open_sweep_options()` de la clase `NanoVNAGraphics`.
