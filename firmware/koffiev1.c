/* Bonus! :-) Ronald Teune's Coffee Machine v1 software/firmware */
/* Based on Till Harbaum's LCD2USB */
/* License: GPL */

#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/pgmspace.h>
#include <avr/wdt.h>
#include <avr/eeprom.h>
#include <util/delay.h>
#include <stdio.h>

#include <fb.h>
// #include <lcd_dummy.h>

#include "lcd.h"

#include "usbdrv/usbdrv.h"
#include "oddebug.h"

#define VERSION_MAJOR 1
#define VERSION_MINOR 8
#define VERSION_STR "1.08"

#ifndef EEMEM
#define EEMEM  __attribute__ ((section (".eeprom")))
#endif

#define UTIL_BIN4(x)        (unsigned char)((0##x & 01000)/64 + (0##x & 0100)/16 + (0##x & 010)/4 + (0##x & 1))
#define UTIL_BIN8(hi, lo)   (unsigned char)(UTIL_BIN4(hi) * 16 + UTIL_BIN4(lo))

#ifndef NULL
#define NULL    ((void *)0)
#endif

#define TEMP_BOILER_MAX 790
#define TEMP_BOILER_MIN 680

#define TEMP_POMP_START 750
#define TEMP_POMP_STOP 680

#define QWAIT 25

unsigned char opwarmen = 0;
unsigned char pompen = 0;
unsigned char malen = 0;

uint16_t ml_te_gaan = 0;
uint16_t ml_gedaan = 0;
uint16_t koffie_te_gaan = 0;
uint16_t adc_temp;
uint16_t adc_ml;

void set_contrast(uchar value) {
}

void set_brightness(uchar value) {
}


uint16_t readADC_temp(void); 
uint16_t readADC_ml(void); 
static void adcInit4(void);
static void adcInit5(void);

void boiler_aan() {
	PORTB |= _BV(1);
}
void boiler_uit() {
	PORTB &= ~_BV(1);
}


void pomp_aan() {
	PORTB |= _BV(2);
}
void pomp_uit() {
	PORTB &= ~_BV(2);
}

void koffiemolen_aan() {
	PORTB |= _BV(0);
}
void koffiemolen_uit() {
	PORTB &= ~_BV(0);
}

char water() {
	return (!(PINB & _BV(3)));
}

char start() {
	return (!(PINB & _BV(5)));
}

void drawstatus();
void initIO();
void debug_mode();

void zetkoffie(uint16_t aantalkoppen) {
		switch(aantalkoppen) {
			case 1:
				ml_te_gaan = 260; //270
				koffie_te_gaan = 95; // utz=110; //FT espresso = 95; //oud = 130;
				break;
			case 2:
				ml_te_gaan = 520; // 550
				koffie_te_gaan = 175; // utz=210; //175; //260;
				break;
			case 3:
				ml_te_gaan = 750; // 780
				koffie_te_gaan = 240; // utz=300; //240; //390;
				break;
			case 4:
				ml_te_gaan = 1000;
				koffie_te_gaan = 320; // utz=400; //320; //500;
				break;
			ml_gedaan = 0;
		}
}


uchar	usbFunctionSetup(uchar data[8]) {
  static uchar replyBuf[4];
  usbMsgPtr = replyBuf;
  uchar len = (data[1] & 3)+1;       // 1 .. 4 bytes 
  uchar target = (data[1] >> 3) & 3; // target 0 .. 3
  uchar i;

  // request byte:

  // 7 6 5 4 3 2 1 0
  // C C C T T R L L

  // TT = target bit map 
  // R = reserved for future use, set to 0
  // LL = number of bytes in transfer - 1 

  switch(data[1] >> 5) {

  case 0: // echo (for transfer reliability testing)
    replyBuf[0] = data[2];
    replyBuf[1] = data[3];
    return 2;
    break;
    
  case 1: // command
    target &= LCD_CTRL_0;  // mask installed controllers

    if(target) // at least one controller should be used ...
      for(i=0;i<len;i++)
	lcd_command(target, data[2+i]);
    break;

  case 2: // data
    target &= LCD_CTRL_0;  // mask installed controllers

    if(target) // at least one controller should be used ...
      for(i=0;i<len;i++)
	lcd_data(target, data[2+i]);
    break;

	case 3: // set
	switch(target) {

		case 0:  // ml_te_gaan
			if(data[2] > 0 && data[2] < 5) {
				if(ml_te_gaan == 0) {
					zetkoffie(data[2]);
				}
			}
			else {
				ml_te_gaan = 0;
				koffie_te_gaan = 0;
				koffiemolen_uit();
				pomp_uit();
				boiler_uit();
			}
			//set_contrast(data[2]);
			break;

		case 1:  // brightness
			set_brightness(data[2]);
			break;

		default:
			// must not happen ...
			break;      
	}
	break;

	case 4: // get
		switch(target) {
		case 0: // ml_te_gaan
			if(ml_te_gaan == 0) {
				replyBuf[0] = adc_ml & 0xff;
				replyBuf[1] = (adc_ml >> 8);
			}
			else {
				replyBuf[0] = ml_te_gaan & 0xff;
				replyBuf[1] = (ml_te_gaan >> 8);
			}
			return 2;
			break;
		case 1: // ml_gedaan
			replyBuf[0] = ml_gedaan & 0xff;
			replyBuf[1] = (ml_gedaan >> 8);
			return 2;
			break;
		case 2: // status
			replyBuf[0] = ((water()) | (opwarmen << 1) | (pompen << 2) | (malen << 3) | ((!(ml_te_gaan == 0)) << 4));
			replyBuf[1] = 0;
			return 2;
			break;
		case 3: // adc_temp
			replyBuf[0] = adc_temp & 0xff;
			replyBuf[1] = (adc_temp >> 8);
			return 2;
			break;
		default:
			// must not happen ...
			break;      
		}
	break;

  default:
    // must not happen ...
    break;
  }

  return 0;  // reply len
}

/* ------------------------------------------------------------------------- */

// from the slideshow presenter
static void hardwareInit(void)
{
    PORTD = 0xfa;   /* 1111 1010 bin: activate pull-ups except on USB lines */
    //DDRD = 0x07;    /* 0000 0111 bin: all pins input except USB (-> USB reset) */
    DDRD = ~(_BV(2) | _BV(0)); 
    /* USB Reset by device only required on Watchdog Reset */
    _delay_loop_2(40000); 
    /* delay >10ms for USB reset */
    DDRD = 0x02;    /* 0000 0010 bin: remove USB reset condition */
}

int	main3(void) {
  wdt_enable(WDTO_1S);

  /* let debug routines init the uart if they want to */
 odDebugInit();
  hardwareInit();

  /* all outputs except INT0 and RxD/TxD */
  //DDRD = ~(_BV(2) | _BV(1) | _BV(0));  
  //PORTD = 0;
//  PORTC = 0;		   /* no pullups on USB pins */
//  DDRC = ~0;		   /* output SE0 for USB reset */

  /* USB Reset by device only required on Watchdog Reset */
  //_delay_loop_2(40000);   // 10ms

//  DDRC = ~USBMASK;	   /* all outputs except USB data */
  usbInit();

  //pwm_init();

  
  //DDRC &= ~_BV(5);         /* input S1 */
  //PORTC |= _BV(5);         /* with pullup */
  //DDRB &= ~_BV(0);         /* input S2 */
  //PORTB |= _BV(0);         /* with pullup */

  /* try to init two controllers */
  if(lcdInit()) {
    lcd_puts(LCD_CTRL_0, "LCD2USB V" VERSION_STR);
  }
  
  sei();
  for(;;) {	/* main event loop */
    wdt_reset();
    usbPoll();
  }
  return 0;
}



int main(void)
{
	char str[100];
	
	//wdt_enable(WDTO_1S);
	odDebugInit();
	hardwareInit();
	usbInit();
	wdt_enable(WDTO_1S);
	
	/* all outputs except INT0 and RxD/TxD and 7=switch */
	//DDRD = ~(_BV(2) | _BV(1) | _BV(0) | _BV(7)); 

	//DDRD |= ~(_BV(7));
	
	PORTD = 0;
	
	
//	PORTC = 0;		   /* no pullups on USB pins */
//	DDRC = ~0;		   /* output SE0 for USB reset */


	
	/* USB Reset by device only required on Watchdog Reset */
	// _delay_loop_2(40000);   // 10ms

	//DDRC = ~USBMASK;	   /* all outputs except USB data */
	//usbInit();


	DDRB = 0;         /* input all */
	DDRB |= _BV(0);	// output koffiemolen
	DDRB |= _BV(1);	// output boiler
	DDRB |= _BV(2);	// output pomp
	
	PORTB = ~(_BV(2) | _BV(1) | _BV(0));         /* alles behalve molen, boiler, pomp pullup */
	//PORTD |= _BV(7); // pull up on "prog" switch

	boiler_uit();
	pomp_uit();
	koffiemolen_uit();
	

	lcdInit();
	
	
	DDRC &= ~(_BV(4) | _BV(5));         /* ADC4 = PIN 27, ADC5 = PIN 28 (deze regel moet na de lcd_init!) */
	
	sei();
	
	clearBuf();
	bufPuts(0,0,"Koffiemolen beta 1.3");
	bufPuts(1,0,"(c)Ronald Teune 2012");
	buf2lcd();
	wdt_reset();
	_delay_ms(500);
	wdt_reset();
	_delay_ms(500);
	wdt_reset();
	_delay_ms(500);
	while(start());
	
	
	for(;;) {
		wdt_reset();
		usbPoll();
		clearBuf();
		adc_temp = readADC_temp(); // _delay_ms(QWAIT);
		adc_ml = readADC_ml(); // _delay_ms(QWAIT);
		adc_ml = adc_ml / 205;
		adc_ml = 5 - adc_ml;
		
		if(start()) {
			zetkoffie(adc_ml);
			wdt_reset();
			_delay_ms(100);
			while(start());
			wdt_reset();
		}

		if(water()) {
			if(ml_te_gaan > 0) {
				if(opwarmen == 1 && adc_temp > TEMP_BOILER_MAX && pompen == 0) {
					opwarmen = 0;
					boiler_uit();
				}
				if(opwarmen == 0 && adc_temp < TEMP_BOILER_MIN) {
					opwarmen = 1;
				}
				if(opwarmen == 1) {
					boiler_aan();
				}
				if(koffie_te_gaan > 0) {
					pompen = 0;
					opwarmen = 0;
					boiler_uit();
					pomp_uit();
					koffiemolen_aan();
					malen = 1;
					if(koffie_te_gaan >= 1)
						koffie_te_gaan -= 1;
				}
				else {
					malen = 0;
					koffiemolen_uit();
					if(pompen == 0 && (adc_temp > TEMP_POMP_START || (opwarmen == 0 && adc_temp > TEMP_POMP_STOP))) { // we komen vanuit een 'dorst' situatie
						pomp_aan();
						pompen = 1;
					}
					if(pompen == 1 && adc_temp < TEMP_POMP_STOP) {
						pomp_uit();
						pompen = 0;
					}
				}
				if(pompen) {
					if(ml_te_gaan > 1)
						ml_te_gaan -= 1;
					else
						ml_te_gaan = 0;
					ml_gedaan += 1;
				}
				if(start()) { // opnieuw startknop? Dan stoppen.
					ml_te_gaan = 0;
					boiler_uit();
					opwarmen = 0;
					koffiemolen_uit();
					malen = 0;
					pomp_uit();
					pompen = 0;
					wdt_reset();
					_delay_ms(100);
					while(start());
					wdt_reset();
				}
				
				//_delay_ms(QWAIT);
				sprintf (str, "%dml te gaan", ml_te_gaan);
				bufPuts(0,0,str);
				sprintf (str, "%d/%dml", ml_gedaan, ml_te_gaan);
				bufPuts(3,0,str);
				sprintf (str, "Temperatuur:%d/1024", adc_temp);
				bufPuts(1,0,str);
				drawstatus();
			}
			else { // geen ml te gaan
				boiler_uit();
				pomp_uit();
				pompen = 0;
				opwarmen = 0;
				/* put string to display (line 1) with linefeed */
				// _delay_ms(QWAIT);
				
				sprintf (str, "Temperatuur:%d/1024", adc_temp);
				bufPuts(1,0,str);
				drawstatus();
				
				sprintf (str, "%d kop(pen) koffie", adc_ml);		
				bufPuts(0,0,str);
				bufPuts(3,0,"<- start / stop");
			}
		}
		else { // geen water
			boiler_uit();
			pomp_uit();
			pompen = 0;
			opwarmen = 0;

			/*
			lcd_clrscr(LCD_CTRL_0);
			sprintf (str, "%d/%dml gedaan, %d te gaan", ml_gedaan, adc_ml, ml_te_gaan);
			lcd_puts(LCD_CTRL_0, str);
			sprintf (str, "adc4_read = %4d", adc_temp);
			lcd_puts(LCD_CTRL_0, str);
			_delay_ms(100);
			*/
			// _delay_ms(QWAIT);
			bufPuts(0,0,"Ik heb dorst! :-)");
			if(start()) {
				bufPuts(0,3,"* debug_mode *");
				buf2lcd();
				_delay_ms(500);
				debug_mode();
			}
		}
		buf2lcd();
		// _delay_ms(QWAIT);
	}
}

void debug_mode() {
	_delay_ms(1000);
	while(!start()) {
		if(water()) {
			opwarmen=1;
			drawstatus();
			boiler_aan();
			_delay_ms(499);
			opwarmen=0;
			drawstatus();
			boiler_uit();
			_delay_ms(499);
			pompen=1;
			drawstatus();
			pomp_aan();
			_delay_ms(499);
			pompen=0;
			drawstatus();
			pomp_uit();
			_delay_ms(499);
			buf2lcd();
		}
	}
}


void drawstatus() {
	//lcd_gotoxy(LCD_CTRL_0,17,3);
	if(opwarmen == 0)
		bufPuts(3,17,"w");
	if(opwarmen == 1)
		bufPuts(3,17,"W");
	if(pompen == 0) {
		bufPuts(3,18,"p");
	}
	if(pompen == 1) {
		bufPuts(3,18,"P");
	}
	if(malen == 0) {
		bufPuts(3,19,"m");
	}
	if(malen == 1) {
		bufPuts(3,19,"M");
	}
	
}

uint16_t readADC_temp(void)
{
	adcInit4();
	ADCSRA |= (1 << ADSC); // start conversion
	while (ADCSRA & (1<<ADSC)); //wait for conversion to finish
	return ADC; //read upper 8bits
}

uint16_t readADC_ml(void)
{
	adcInit5();
	ADCSRA |= (1 << ADSC); // start conversion
	while (ADCSRA & (1<<ADSC)); //wait for conversion to finish
	return ADC; //read upper 8bits
} 

static void adcInit4(void)
{
	ADMUX = (1 << REFS0) | (1 << MUX2);  // interne 5V referentie, meet ADC4
	ADCSRA = UTIL_BIN8(1000, 0111); /* enable ADC, not free running, interrupt disable, rate = 1/128 */
	//ADCSRA = (1<<ADEN)|(1<<ADPS2)|(ADPS1)|(ADPS0); // moet gelijk zijn aan bovenstaand, maar dat vraag ik me af
    //ADMUX = UTIL_BIN8(1001, 0011);  /* Vref=2.56V, measure ADC0 */
    //ADCSRA = UTIL_BIN8(1000, 0111); /* enable ADC, not free running, interrupt disable, rate = 1/128 */
	
	// first conversion, discard result
	ADCSRA |= (1 << ADSC); // start conversion
	while (ADCSRA & (1<<ADSC)); //wait for conversion to finish
}


static void adcInit5(void)
{
	ADMUX = (1 << REFS0) | (1 << MUX2) | (1 << MUX0);  // interne 5V referentie, meet ADC4
	ADCSRA = UTIL_BIN8(1000, 0111); /* enable ADC, not free running, interrupt disable, rate = 1/128 */
	//ADCSRA = (1<<ADEN)|(1<<ADPS2)|(ADPS1)|(ADPS0); // moet gelijk zijn aan bovenstaand, maar dat vraag ik me af
    //ADMUX = UTIL_BIN8(1001, 0011);  /* Vref=2.56V, measure ADC0 */
    //ADCSRA = UTIL_BIN8(1000, 0111); /* enable ADC, not free running, interrupt disable, rate = 1/128 */
	
	// first conversion, discard result
	ADCSRA |= (1 << ADSC); // start conversion
	while (ADCSRA & (1<<ADSC)); //wait for conversion to finish
}
