/*
 * 	fonctions du chassis robot:
 * 	
 * 		Propulsion, tourelle, laser
 * 		
 * 		Propulsion:
 * 			compose d'un moteur droit et un gauche
 * 			ici les moteurs sont des servo a rotation continue.
 * 			les fonctions:
 * 			- avancer: marche(avant/arriere, nbre) - avance ou recul d'un nbre d'unite
 * 			- tourner: tourne(H/AH, degre) - tourne sens horaire ou anti-horaire d'autant de degre
 * 			- stop	 : stop() - stop avancer
 * 			- raz	 : raz() - remet a zero le compteur d'avance pour les deux moteur
 * 			les variables:
 * 			- compteur d'unite pour chaque moteur
 * 		Tourelle:
 * 			compose de deux servo, (y)vertical et (x)horizontal
 * 			les fonctions:
 * 			- regarde(x en degre,y en degre) - regarde a autant de degre sur l'axe x et y. prevoir une interpolation pour le mouvement
 * 			- position() - renvoi la position x,y en degre
 * 			les variables:
 * 			- x - position x actuel
 * 			- tox - position de deplacement vers x
 * 			- y - position y actuel
 * 			- toy - position de deplacement vers y
 * 			
 * 		Laser:
 * 			laser permettant le calcul de distance
 * 			les fonctions:
 * 			- laser(activer/desactiver) - active / desactive le laser
 * 			les variables:
 * 			- laserpos - position du laser actif ou non
 * 		Protocole:
 * 			protocole de communication i2c
 * 			requestEvent():
 * 			- I2C_Packet 12 bytes:
 * 				[0]-[3] = uint32_t compteur gauche
 * 				[4]-[7] = uint32_t compteur droite
 * 				[8]		= position actuelle x de 0 a 180
 * 				[9]	= position actuelle y de 0 a 180
 * 				[10]	= position laser on/off
 * 			receiveEvent(int bytesReceived):
 * 			-I2C_Command
 * 				[0]		= 	bit 0 - execute tourelle
 * 							bit 1 - }
 * 							bit 2 - }propulsion avant/arriere
 * 							bit 3 -	tourner on/off
 * 							bit 4 -	tourner gauche/droite
 * 							bit 5 - laser on/off
 * 							bit 6 -	compteur raz
 * 				[1]		=	bit 0 - demande compteur gauche
 * 							bit 1 - demande compteur droite

 * 				[2]		= position x
 * 				[3]		= position y
 * 				
 */
#include <Servo.h>
#include <Wire.h>
#include "StackArray.h"
#define RAF			0x00
#define TOUREXE		0x01
#define PROPAR		0x02
#define	PROPAV		0x03
#define	TOURNG		0x04
#define TOURND		0x05
#define LASERON		0x06
#define RAZ			0x07
#define DCG			0x08
#define DCD			0x09
#define NIVBATT		0x10

#define UNIT_MS	100
//definition des pins
#define	MOT_G		3	//moteur de propultion gauche
#define	MOT_D		6	//moteur de propultion droite
#define SRV_X		4	//servo tourelle rotation sur l'axe X
#define SRV_Y		5	//servo tourelle rotation sur l'axe Y
#define LAZ			52	//laser

// pile d'execution
StackArray <byte>  pile;
//creation des objet servo
Servo motG;
Servo motD;
Servo tourX;
Servo tourY;

uint32_t compteur_g;
uint32_t compteur_d;
//int8_t axe_x;
//int8_t axe_y;
bool laser_flag;

// déclaration des registres
byte regs[3];
int regIndex = 0; // Registre à lire ou à écrire.

byte bytesend[4];

// copie de la dernière instruction d execution écrite dans
// le registre reg0 pour le traitement asynchrone de
// requestEvent (demande de bytes)
byte lastExecReq = 0x00;

/* Coefficient diviseur du pont de résistance */
const float coeff_division = 3.28;
union u_tag {
  byte b[4];
  float fval;
} u;

void setup()
{
	//analogReference(INTERNAL2V56);
	// Initialisation des registres
	regs[0] = 0x00; // reg0 = registre d'exécution
	// valeur 0x00 = NOP - No Operation = rien à faire
	regs[1] = 0x00; // valeur 0x00 = NOP - No Operation = rien à faire
	regs[2] = 0x00;


	//propulsion
	motG.attach(MOT_G);
	pinMode(MOT_G, OUTPUT);
	motG.write(90);
	compteur_g = 0;
	motD.attach(MOT_D);
	pinMode(MOT_D, OUTPUT);
	motD.write(90);
	compteur_d = 0;
	//tourelle
	tourX.attach(SRV_X);
	pinMode(SRV_X, OUTPUT);
	tourX.write(90);
	//axe_x = 90;
	tourY.attach(SRV_Y);
	pinMode(SRV_Y, OUTPUT);
	tourY.write(90);
	//axe_y = 90;
	//laser
	pinMode(LAZ, OUTPUT);
	laser_flag = false;

	// Joindre le Bus I2C avec adresse #4
	Wire.begin(0x20);
	// enregistrer l'événement
	//    Lorsque des données sont écrites par le maitre et reçue par l'esclave
	Wire.onReceive(receiveEvent);
	// enregistrer l'événement
	//    Lorsque le Maitre demande de lecture de bytes
	Wire.onRequest(requestEvent);

	// Démarrer une communication série
	Serial.begin(19200);
	Serial.println( F("Bus I2C pret") );

}

void marche(bool sens)
{
	if(sens){
		motG.write(180);
		motD.write(0);
		compteur_g += 1;
		compteur_d += 1;
	}
	else
	{
		motG.write(0);
		motD.write(180);
		compteur_g -= 1;
		compteur_d -= 1;
	}
	delay(UNIT_MS);
	motG.write(90);
	motD.write(90);
}

void tourner(bool sens)
{
	if(sens){
		motG.write(180);
		motD.write(180);
		compteur_g += 1;
		compteur_d -= 1;
	}
	else
	{
		motG.write(0);
		motD.write(0);
		compteur_g -= 1;
		compteur_d += 1;
	}
	delay(UNIT_MS);
	motG.write(90);
	motD.write(90);
}

void loop()
{
	// Si NOP alors rien à faire

	// Exécution de l'opération
	/* Serial.println( F("--- Traitement Requete ---") );
  Serial.print( F("reg0 = ") );
  Serial.println( regs[0], DEC );
  Serial.print( F("reg1 = ") );
  Serial.println( regs[1], DEC );
  Serial.print( F("reg2 = ") );
  Serial.println( regs[2], DEC );
	 */

  if(!pile.isEmpty()){
    regs[0] = pile.pop();
  }
 if(regs[0] != 0){
		switch( regs[0] ){
		case TOUREXE:
			tourX.write(regs[1]);
			tourY.write(regs[2]);
			break;
		case PROPAV:
			marche(true);
			break;
		case PROPAR:
			marche(false);
			break;
		case TOURND:
			tourner(true);
			break;
		case TOURNG:
			tourner(false);
			break;
		case LASERON:
			if(!laser_flag){
				digitalWrite(LAZ, true);
				laser_flag = true;
			}else{
				digitalWrite(LAZ, false);
				laser_flag = false;
			}

			break;
		case RAZ:
			compteur_d = 0;
			compteur_g = 0;
			break;
		case DCG : /* demande compteur gauche */
			bytesend[0] = (compteur_g >> 0)  & 0xFF;
			bytesend[1] = (compteur_g >> 8)  & 0xFF;
			bytesend[2] = (compteur_g >> 16) & 0xFF;
			bytesend[3] = (compteur_g >> 24) & 0xFF;
			break;
		case DCD : /* demande compteur droite */
			bytesend[0] = (compteur_d >> 0)  & 0xFF;
			bytesend[1] = (compteur_d >> 8)  & 0xFF;
			bytesend[2] = (compteur_d >> 16) & 0xFF;
			bytesend[3] = (compteur_d >> 24) & 0xFF;
			break;
		case NIVBATT: /* demande niveau batterie*/
			 unsigned int raw_bat = analogRead(A0);
			 u.fval = ((raw_bat * (5.0 / 1023)) * coeff_division);
			break;
		}
	}
	// reset to NOP
	regs[0] = 0x00;
}

// Fonction qui est exécutée lorsque des données sont envoyées par le Maître.
// Cette fonction est enregistrée comme une événement ("event" en anglais), voir la fonction setup()
void receiveEvent(int howMany)
{
	int byteCounter = 0;

	// Pour faire du debug... mais attention cela peut planter
	//    la réception!
	//
	//Serial.println(F("---- LECTURE ---"));
	//Serial.print(F("Numbre de Bytes: "));
	//Serial.println( howMany );

	// Lire tous les octets sauf le dernier
	while( byteCounter < howMany )
	{
		// lecture de l'octet
		byte b = Wire.read();
		byteCounter += 1;

		//Serial.println( b, DEC );

		if( byteCounter == 1 ){   // Byte #1 = Numéro de registre
			regIndex = b;
		}
		else {                    // Byte #2 = Valeur a stocker dans le registre
			switch(regIndex) {
			case 0:
				regs[0] = b;
				// maintenir une copie du dernier reg0 pour
				// traitement d'une réponse via requestEvent (demande de byte)
				lastExecReq = b;
                                pile.push(b);
				break;
			case 1:
				regs[1] = b;
				break;
			case 2:
				regs[2] = b;
				break;
			}
		}


	} // fin WHILE
}

// Fonction est activé lorsque le Maitre fait une demande de lecture.
//
void requestEvent()
{
	// Deboggage - Activer les lignes suivantes peut perturber fortement
	//    l'échange I2C... a utiliser avec circonspection.
	//
	//   Serial.print( "Lecture registre: " );
	//   Serial.println( regIndex );

	// Quel registre est-il lu???
	switch( regIndex ){

	case 0x00: // lecture registre 0
		// la réponse depend de la dernière opération d'exécution demandée
		//    par l'intermédiaire du registre d'exécution (reg 0x00).
		switch( lastExecReq ) {
		case DCG: /* demande compteur gauche */
			Wire.write( bytesend, 4 );
			break;

		case DCD: /* demande compteur droite */
			Wire.write( bytesend, 4 );
			break;
		case NIVBATT:
			Wire.write(u.b,4);
			break;
		default:
			Wire.write( 0xFF ); // ecrire 255 = il y a un problème!
		}
		break;

		default: // lecture autre registre
			Wire.write( 0xFF ); // ecrire 255 = il y a un problème
	}

}
