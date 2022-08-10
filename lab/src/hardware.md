# IceLogicBus Hardware
The IceLogicBus (ILB) Hardware consists of modular tiles fitted to the main carrier board as required for the given development project. Onboard the main ILB carrier board is the FPGA and power-train (USB-C-PD/XT30). Mounted on top of this is the BlackEdge Controller (BEC) board with microcontroller, SPI Flash, blades and connectors.

## Connectivity & Power
The BEC has a USB-C connector configured as a USB CDC serial device running [QSPIMEM](./qspimem.md) under [BlackCrab](./blackcrab.md) Rust based firmware . This allows programming of the microcontroller, FPGA and flash, along with uart and monitoring features depending on the required mode.

There is a second Usb-C (Usb-PD) Connector on the ILB which operates as a high Power over Usb 
delivery system operating from 5 to 20 volts in order to be able to power a large range of modular tiles from simple led drivers through to small motor and power-train devices. An auxiliary XT30 power connector is also  provided for the more extreme power delivery requirements across the tiles from sources such as batteries etc.

## Operating Modes
Mode selection is achieved via the 'Mode' button, if depressed on power up it switches the device into Usb-DFU mode which enables the firmware to be updated from the PC host over Usb. Normal startup places the device into _[QSPIMEM](./qspimem.md)_. In QSPIMEM mode the device intelligently listens to Usb traffic for new ILB applications, FPGA updates whilst concurrently relaying monitor, logging and error information.

More advanced functionality can be achieved over USB via _[QSPIMEM](./qspimem.md) including uploads, downloads and data transfers.

## Status and feedback
There is an RGB led on board which can provide feedback and status of the board's mode and operation. In normal mode this is unlit. if and application or FPGA image is uploaded it will flicker green and amber and then extinguish on successful completion. If it remains red it will normally be due to either a hardware fault or bad FPGA synthesis. A third state is possible when the FPGA synthesis drives the blue part of the led for example in a blinky test, the colour will the blink blue. The BEC also has an RGB led which is normally green (power), the other leds can be used to indicate activity and status from the [BlackCrab](./blackcrab.md) firmware.

There is also a 1.27mm pitch 10pin, Arm SWD debug connector if you need to debug what is [BlackCrab](./blackcrab.md) running on the BEC.

