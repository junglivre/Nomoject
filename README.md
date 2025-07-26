# Nomoject

en-US | [pt-BR](README_br.md)

Nomoject (No More Eject!) is a Windows application designed to manage hotplug devices in QEMU virtual machines. It allows users to identify and modify removable PCI devices' capabilities through registry modifications.

## Features

- Lists all PCI devices with removable capabilities
- Easy device selection with checkboxes
- Generates registry files to make devices non-removable
- Dark theme modern interface
- Compatible with Windows 7/Server 2008 and newer
- Multi-language support

## Use Cases

- Prevent accidental device removal in QEMU VMs
- Fix "Safely Remove Hardware" showing virtual devices
- Manage PCI passthrough devices in virtual machines
- Batch modification of multiple devices

## Installation

### From Release (Recommended)
1. Download the latest release from the [Releases](https://github.com/junglivre/Nomoject/releases/latest) page
2. Extract the ZIP file
3. Run `Nomoject.exe`

### From Source
1. Install Python 3.7 or newer
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python nomoject.py
   ```

## Building from Source

To create a standalone executable:

1. Install build dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the build script:
   ```
   python build.py
   ```

The executable will be generated in the `dist` folder.

## How It Works

Nomoject scans the Windows Registry under `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\PCI` for devices with `Capabilities` value of 6 (removable). When generating the registry file, it changes this value to 2 (non-removable) for selected devices.

## Security Considerations

- The application requires registry access to function
- Generated .reg files modify system settings
- Run as administrator when applying registry changes
- Always review the generated .reg file before applying

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- QEMU/KVM community
- PyQt developers
- All contributors and users

## Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the documentation 