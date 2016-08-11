/*#################################################################################################
	Title	 : Coffee machine v2 Atmega firmware
	Author   : Ronald Teune
	Based on : TWI Slave by Martin Junghans, www.jtronics.de
	License	 : GNU General Public License 
	
	LICENSE:
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

//#################################################################################################*/

#include <stdlib.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/pgmspace.h>
#include <util/delay.h>

#include "twislave.h"

#ifndef F_CPU
#define F_CPU 4000000UL
#endif

//###################### Slave-Adresse
#define SLAVE_ADRESSE 0x40 								// Slave-Adresse

//###################### Macros
#define uniq(LOW,HEIGHT)	((HEIGHT << 8)|LOW)			// 2x 8Bit 	--> 16Bit
#define LOW_BYTE(x)        	(x & 0xff)					// 16Bit 	--> 8Bit
#define HIGH_BYTE(x)       	((x >> 8) & 0xff)			// 16Bit 	--> 8Bit


#define sbi(ADDRESS,BIT) 	((ADDRESS) |= (1<<(BIT)))	// set Bit
#define cbi(ADDRESS,BIT) 	((ADDRESS) &= ~(1<<(BIT)))	// clear Bit
#define	toggle(ADDRESS,BIT)	((ADDRESS) ^= (1<<BIT))		// Bit umschalten

#define	bis(ADDRESS,BIT)	(ADDRESS & (1<<BIT))		// bit is set?
#define	bic(ADDRESS,BIT)	(!(ADDRESS & (1<<BIT)))		// bit is clear?

#define D_12V_RELAIS		(1 << 0)
#define D_LCD_ON		(1 << 1)
#define D_BTN_LCD		(1 << 2)
#define D_COUNT			(1 << 5)
#define D_LOVELY_RED_LIGHT	(1 << 6)


//###################### Variablen
	uint16_t 	Variable=2345;				//Zähler
	uint16_t	buffer;
	uint16_t	low, hight;
	char		temperatuur = 0;
	char		do_count = 0;
	char		showtemp = 0;



uint8_t i2cReadFromRegister(uint8_t reg)
{
	switch (reg)
	{
		case 0: // 5-position-button
			return ((PIND & (1 << 3)) >> 3) | ((PIND & (1 << 4)) >> 3) | ((PINB & (1 << 6)) >> 4) | ((PINB & (1 << 7)) >> 4);
			break;
		case 1:
			return temperatuur;
			break;
		default:
			return reg;
	}
}

// A callback triggered when the i2c master attempts to write to a register.
void i2cWriteToRegister(uint8_t reg, uint8_t value)
{
	switch (reg)
	{
		case 0: // tellen
			if(value == 1)
				do_count = 1;
			break;
		case 1: // lamp aan
			if(value)
				PORTD |= D_LOVELY_RED_LIGHT;
			else
				PORTD &= ~D_LOVELY_RED_LIGHT;
			break;
		case 2:
			showtemp = value;
	}
}



//################################################################################################### Initialisierung
void init_twi(void)
	{
	cli();
	//### PORTS	
	
	//### TWI 
//	init_twi_slave(SLAVE_ADRESSE);			//TWI als Slave mit Adresse slaveadr starten 
	genericTwiSlaveInit(SLAVE_ADRESSE, i2cReadFromRegister, i2cWriteToRegister);
	
	sei();
	}

//################################################################################################### Hauptprogramm

void init_pwm(void) {
	// init pwm
	TCCR1A = (1 << COM1A1) | (1 << COM1B1) | (1 << WGM10);
	TCCR1B = (1 << CS10) | (1 << WGM12);
	TCNT0 = 0;
	TCNT1 = 0;
}

static void adcInit3(void)
{
	ADCSRA = 0; // disable
	ADMUX = (1 << REFS0) | (1 << MUX1) | (1 << MUX0) | (1 << ADLAR);  // VCC = referentie, meet ADC3, left adjust

	ADCSRA = (1 << ADFR)|(1<<ADEN)|(1<<ADPS2)|(ADPS1)|(ADPS0); // enable, set prescaler, free running, 1/128
	
	// first conversion, discard result
	ADCSRA |= (1 << ADSC); // start conversion
//	while (ADCSRA & (1<<ADSC)); //wait for conversion to finish
}


uint16_t readADC(void)
{
	adcInit3();
	ADCSRA |= (1 << ADSC); // start conversion
	while (ADCSRA & (1<<ADSC)); //wait for conversion to finish
	return ADC; //read upper 8bits
} 

char btn_lcd_state = 0;
char v12_state = 0;

int main(void)
{	

	DDRB = 0;
	DDRD = 0;
	PORTD = 0;
	PORTB = 0;

	DDRB |= (1 << 2); // set PB2/OC1B as output (PWM output)
	DDRD |= D_12V_RELAIS | D_LCD_ON | D_COUNT | D_LOVELY_RED_LIGHT; // set as output
	PORTD |= D_BTN_LCD; // enable pull-up
	PORTD |= (1 << 3) | (1 << 4);
	PORTB |= (1 << 6) | (1 << 7);



	init_pwm();
	init_twi();
	adcInit3();
	if(PIND & D_BTN_LCD) {
		PORTD |= D_12V_RELAIS;
	}
	_delay_ms(500); // wait for 12V to come up

	while(1) {
		//############################ write Data in txbuffer


		temperatuur = .70 * (244-ADCH);

		
		if(showtemp || btn_lcd_state) // show temp on Voltmeter when told by uC to show it, or if screen is on
			OCR1BL = temperatuur * 2.5;
		else
			OCR1BL = 0;

		if(do_count) {
			do_count = 0;
			PORTD |= D_12V_RELAIS;
			PORTD |= D_COUNT;
			_delay_ms(200);
			PORTD &= ~D_COUNT;
			if(v12_state == 0) {
				PORTD &= ~D_12V_RELAIS;
			}
		}

		if(btn_lcd_state != (PIND & D_BTN_LCD)) {
			_delay_ms(20); // debounce
			btn_lcd_state = PIND & D_BTN_LCD;
			if(btn_lcd_state == 0) {
				v12_state = 0;
				PORTD &= ~D_12V_RELAIS;
				PORTD &= ~D_LCD_ON;
			}
			else {
				v12_state = 1;
				PORTD |= D_12V_RELAIS;
				PORTD |= D_LCD_ON;
				_delay_ms(500);
				PORTD &= ~D_LCD_ON;
			}
		}

	} //end.while
} //end.main



