# NanoVNA UTN Toolkit - Tools

This directory contains utility tools for working with NanoVNA devices.

## Tools Available

### `check_nanovna.py`
Simple NanoVNA connection checker that attempts to connect to a NanoVNA device and verifies the connection.

**Usage:**
```bash
python -m src.NanoVNA_UTN_Toolkit.tools.check_nanovna
```

### `dfu_communicator.py`
NanoVNA DFU Mode Communicator for devices in DFU (Device Firmware Update) mode.

**Usage:**
```bash
python -m src.NanoVNA_UTN_Toolkit.tools.dfu_communicator
```

### `nano_vna_checker.py`
Advanced NanoVNA checker with additional device verification capabilities.

**Usage:**
```bash
python -m src.NanoVNA_UTN_Toolkit.tools.nano_vna_checker
```

### `vna_tester.py`
Comprehensive VNA testing tool.

**Usage:**
```bash
python -m src.NanoVNA_UTN_Toolkit.tools.vna_tester
```

## Running Tools

All tools can be run from the project root using the module syntax shown above, or you can navigate to the tools directory and run them directly:

```bash
cd src/NanoVNA_UTN_Toolkit/tools
python check_nanovna.py
```
