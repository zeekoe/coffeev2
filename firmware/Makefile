# Name: Makefile
# Project: Coffee machine v2 firmware
# Author: Ronald Teune
# Tabsize: 4

DEVICE=atmega8
DEFINES += -DF_CPU=4000000
DEFINES += -DDEBUG_LEVEL=0

COMPILE = avr-gcc -Wall -Os -Iusbdrv -I. -mmcu=$(DEVICE) $(DEFINES)
# NEVER compile the final product with debugging! Any debug output will
# distort timing so that the specs can't be met.

OBJECTS = twislave.o main.o

# symbolic targets:
all:	main.hex

.c.o:
	$(COMPILE) -c $< -o $@

.S.o:
	$(COMPILE) -x assembler-with-cpp -c $< -o $@
# "-x assembler-with-cpp" should not be necessary since this is the default
# file type for the .S (with capital S) extension. However, upper case
# characters are not always preserved on Windows. To ensure WinAVR
# compatibility define the file type manually.

.c.s:
	$(COMPILE) -S $< -o $@

flash:	all
	avrdude -p $(DEVICE) -c gpio2    -U flash:w:main.hex
	pigs M 2 0 # this should return the state back to normal
	pigs M 3 0 # so the I2C is working again


# Fuse high byte:
# 0xdd = 1 1 0 1   1 1 0 1
#        ^ ^ ^ ^   ^ \-+-/ 
#        | | | |   |   +------ BODLEVEL 2..0 (brownout trigger level -> 2.7V)
#        | | | |   +---------- EESAVE (preserve EEPROM on Chip Erase -> not preserved)
#        | | | +-------------- WDTON (watchdog timer always on -> disable)
#        | | +---------------- SPIEN (enable serial programming -> enabled)
#        | +------------------ DWEN (debug wire enable)
#        +-------------------- RSTDISBL (disable external reset -> enabled)
#
# Fuse low byte:
# 0xe1 = 1 1 1 0   0 0 0 1
#        ^ ^ \+/   \--+--/
#        | |  |       +------- CKSEL 3..0 (clock selection -> HF PLL)
#        | |  +--------------- SUT 1..0 (BOD enabled, fast rising power)
#        | +------------------ CKOUT (clock output on CKOUT pin -> disabled)
#        +-------------------- CKDIV8 (divide clock by 8 -> don't divide)
# fuse:
# 	$(AVRDUDE) -U hfuse:w:0xdd:m -U lfuse:w:0xe1:m
fuse:
#	sudo avrdude -p attiny45 -c gpio2 -U lfuse:w:0xe2:m
#	sudo avrdude -p attiny2313 -c gpio2 -U lfuse:w:0xe4:m
	sudo avrdude -p atmega8 -c gpio2 -U lfuse:w:0xe3:m
	pigs M 2 0 # this should return the state back to normal
	pigs M 3 0 # so the I2C is working again

clean:
	rm -f main.hex main.lst main.obj main.cof main.list main.map main.eep.hex main.bin *.o

# file targets:
main.bin:	$(OBJECTS)
	$(COMPILE) -o main.bin $(OBJECTS)

main.hex:	main.bin
	rm -f main.hex main.eep.hex
	avr-objcopy -j .text -j .data -O ihex main.bin main.hex
# do the checksize script as our last action to allow successful compilation
# on Windows with WinAVR where the Unix commands will fail.
