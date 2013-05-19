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
 * 				[0]		= 	bit 0 - propulsion on/off
 * 							bit 1 - propulsion avant/arriere
 * 							bit 2 -	tourner on/off
 * 							bit 3 -	tourner gauche/droite
 * 							bit 4 - laser on/off
 * 							bit 5 -	compteur raz
 * 							bit 6 -
 * 							bit 7 -
 * 				[1]		= position x
 * 				[2]		= position y
 * 				
 */
#include <Servo.h>
#include <Wire.h>
#define	SLAVE_ADDRESS           0x29  //slave address,any number from 0x01 to 0x7F
#define UNIT_MS	100
//definition des pins
#define	MOT_G		3	//moteur de propultion gauche
#define	MOT_D		4	//moteur de propultion droite
#define SRV_X		5	//servo tourelle rotation sur l'axe X
#define SRV_Y		6	//servo tourelle rotation sur l'axe Y
#define LAZ			7	//laser

//creation des objet servo
Servo motG;
Servo motD;
Servo tourX;
Servo tourY;
//declaration tableau de byte
typedef struct Data_t{
	uint32_t comptG;
	uint32_t comptD;
	byte x;
	byte y;
	byte laser;
};
typedef union I2C_Packet_t{
	Data_t data;
	byte I2CPacket[sizeof(Data_t)];
};

#define PACKET_SIZE sizeof(Data_t)
I2C_Packet_t leakinfo; 
// leakinfo.data.comptG = valeur

void setup()
{
	//propulsion
	motG.attach(MOT_G);
	pinMode(MOT_G, OUTPUT);
	motG.write(90);
	leakinfo.data.comptG = 0;
	motD.attach(MOT_D);
	pinMode(MOT_D, OUTPUT);
	motD.write(90);
	leakinfo.data.comptD = 0;
	//tourelle
	tourX.attach(SRV_X);
	pinMode(SRV_X, OUTPUT);
	tourX.write(90);
	leakinfo.data.x = 90;
	tourY.attach(SRV_Y);
	pinMode(SRV_Y, OUTPUT);
	tourY.write(90);
	leakinfo.data.y = 90;
	//laser
	pinMode(LAZ, OUTPUT);
	bitWrite(leakinfo.data.laser,0,false);

	//i2c
	Wire.begin(SLAVE_ADDRESS); 
	Wire.onRequest(requestEvent);
	Wire.onReceive(receiveEvent);
}

void marche(bool sens)
{
	if(sens){
		motG.write(180);
		motD.write(0);
		leakinfo.data.comptG += 1;
		leakinfo.data.comptD += 1;
	}
	else
	{
		motG.write(0);
		motD.write(180);
		leakinfo.data.comptG -= 1;
		leakinfo.data.comptD -= 1;
	}
	delay(UNIT_MS);
	motG.write(90);
	motD.write(90);
}

void raz()
{
	leakinfo.data.comptG = 0;
	leakinfo.data.comptD = 0;
}

void tourner(bool sens)
{
	if(sens){
		motG.write(180);
		motD.write(180);
		leakinfo.data.comptG += 1;
		leakinfo.data.comptD -= 1;
	}
	else
	{
		motG.write(0);
		motD.write(0);
		leakinfo.data.comptG -= 1;
		leakinfo.data.comptD += 1;
	}
	delay(UNIT_MS);
	motG.write(90);
	motD.write(90);
}

void regarde(int axe_x, int axe_y )
{
	tourX.write(axe_x);
	leakinfo.data.x = axe_x;
	tourY.write(axe_y);
	leakinfo.data.y = axe_y;
	//bool flag_x = false;
	//bool flag_y = false;
	//int index = 0;
	//if(axe_x <= leakinfo.data.x){ flag_x = false; }else{ flag_x = true; }
	//if(axe_y <= leakinfo.data.y){ flag_y = false; }else{ flag_y = true; }
	//int diff_x, diff_y;
	//diff_x = abs(leakinfo.data.x - axe_x);
	//diff_y = abs(leakinfo.data.y - axe_y);
	//int arr_x[0];
	//int arr_y[0];
	//if(diff_x >= diff_y){
	//	int arr_x[diff_x];
	//	int arr_y[diff_x];
	//	if(leakinfo.data.x == axe_x){	}else if(flag_x == true){	}else{	}
	//	if(leakinfo.data.y == axe_y){	}else if(flag_y == true){	}else{	}
	//}
	//else
	//{
	//}
}

void laser(bool np)
{
	digitalWrite(LAZ, np);
	bitWrite(leakinfo.data.laser,0,np);

}

void loop()
{
}

void requestEvent()
{
	Wire.write(leakinfo.I2CPacket, PACKET_SIZE);  
}

void receiveEvent(int bytesReceived)
{
	byte comProp = Wire.read();
	int tmp_x = Wire.read();
	int tmp_y = Wire.read();
	if(tmp_x != 0){regarde(tmp_x, tmp_y);}
	if(bitRead(comProp, 0)){marche(bitRead(comProp,1));}
	if(bitRead(comProp, 2)){tourner(bitRead(comProp,3));}
	laser(bitRead(comProp,4));
	if(bitRead(comProp,5)){raz();}
}       
