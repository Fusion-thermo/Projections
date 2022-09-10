from tkinter import *
from math import sqrt, acos, atan2, cos, sin, pi
import numpy as np

hauteur=800
largeur=1100
origine_x=largeur//2
origine_y=hauteur//2
unite=100
rayon_point=1
coeff_distance=2

'''
coordonnées cartésiennes pour l'affichage sur l'écran 2D cartésien et pour les 2 translations
matrices de rotation pour les rotations
il manque une rotation autour de x mais elle n'a pas d'intérêt, et une translation selon x sans intérêt

'''



def radians(angle):
	return angle*pi/180

def degre(angle):
	return angle*180/pi


class point:
	def __init__(self,x,y,z,nom=""):
		#coos cartésiennes
		self.x=x
		self.y=y
		self.z=z
		#Rz
		self.phi1=atan2(y,x)
		self.phi_initial1=self.phi1
		#Ry
		self.phi2=atan2(x,z)
		self.phi_initial2=self.phi2
		#décalages précédents
		self.decalage_y_prec=0
		self.decalage_z_prec=0
		#point projeté
		self.px=0
		self.py=0
		self.pz=0


		if nom=="":
			self.nom=str((round(x,1),round(y,1),round(z,1)))
		else:
			self.nom=nom

	def rotate_Rz(self,phi1):
		'''
		seul phi1 bouge
		on recalcule x, y z
		problème : le décalage indiqué sur l'écran avec les curseurs ne correspond plus au décalage réel.
		pour corriger ça et donc avoir un décalage cohérent pour tous les points, c'est la valeur d'origine dans "décalage par rapport à la valeur d'origine" qu'il faut changer
		donc je recalcule la valeur d'origine
		'''
		theta=(phi1+self.phi_initial1)-self.phi1
		self.phi1=self.phi_initial1+phi1
		
		coos=np.array([[self.x],[self.y],[self.z]])
		Rz=np.array([[cos(theta),-sin(theta),0],[sin(theta),cos(theta),0],[0,0,1]])
		result=np.dot(Rz,coos)
		#print(coos,result)
		self.x=result[0][0]
		self.y=result[1][0]
		self.z=result[2][0]

		self.phi2=atan2(self.x,self.z)
		self.phi_initial2=self.phi2 - radians(int(Ry.get()))

		if "(" in self.nom:
			self.nom=str((round(self.x,1),round(self.y,1),round(self.z,1)))

	def rotate_Ry(self,phi2):
		'''
		même principe
		'''
		theta=(phi2+self.phi_initial2)-self.phi2
		self.phi2=self.phi_initial2+phi2

		coos=np.array([[self.x],[self.y],[self.z]])
		Ry=np.array([[cos(theta),0,sin(theta)],[0,1,0],[-sin(theta),0,cos(theta)]])
		result=np.dot(Ry,coos)
		self.x=result[0][0]
		self.y=result[1][0]
		self.z=result[2][0]

		self.phi1=atan2(self.y,self.x)
		self.phi_initial1=self.phi1 - radians(int(Rz.get()))

		if "(" in self.nom:
			self.nom=str((round(self.x,1),round(self.y,1),round(self.z,1)))

	def deplace_y(self,y):
		if y-self.decalage_y_prec>0:
			self.y-=0.5
		else:
			self.y+=0.5
		self.decalage_y_prec=y

		self.phi2=atan2(self.x,self.z)
		self.phi_initial2=self.phi2 - radians(int(Ry.get()))
	
		self.phi1=atan2(self.y,self.x)
		self.phi_initial1=self.phi1 - radians(int(Rz.get()))

	def deplace_z(self,z):
		if z-self.decalage_z_prec>0:
			self.z-=0.5
		else:
			self.z+=0.5
		self.decalage_z_prec=z

		self.phi2=atan2(self.x,self.z)
		self.phi_initial2=self.phi2 - radians(int(Ry.get()))
		
		self.phi1=atan2(self.y,self.x)
		self.phi_initial1=self.phi1 - radians(int(Rz.get()))



longueur_repere=5
u=3
repere=[point(0,0,0,"0"),point(0,longueur_repere,0,"y"),point(longueur_repere,0,0,"x"),point(0,0,longueur_repere,"z")]
carre=[point(-u,-u,-u),point(-u,u,-u),point(u,u,-u),point(u,-u,-u),point(-u,-u,u),point(-u,u,u),point(u,u,u),point(u,-u,u)]
#carre=[point(1,1,1)]
distance_plan=20
camera=point(50,0,0)

def rotation_Ry(rien,points=carre,points_repere=repere):
	for dot in points:
		dot.rotate_Ry(radians(int(Ry.get())))
	for dot in points_repere:
		dot.rotate_Ry(radians(int(Ry.get())))
	affichage_carre(points)
	affichage_repere(points_repere)

def rotation_Rz(rien,points=carre,points_repere=repere):
	for dot in points:
		dot.rotate_Rz(radians(int(Rz.get())))
	for dot in points_repere:
		dot.rotate_Rz(radians(int(Rz.get())))
	affichage_carre(points)
	affichage_repere(points_repere)

def deplace_y(rien,points=carre,points_repere=repere):
	for dot in points:
		dot.deplace_y(float(deplacement_y.get()))
	affichage_carre(points)
	affichage_repere(points_repere)

def deplace_z(rien,points=carre,points_repere=repere):
	for dot in points:
		dot.deplace_z(float(deplacement_z.get()))
	affichage_carre(points)
	affichage_repere(points_repere)


def affichage_carre(points):
	#debug(points)
	Canevas.delete(ALL)
	l=[]
	for dot1 in points:
		for dot2 in points:
			l.append(round(sqrt((dot1.x-dot2.x)**2 + (dot1.y-dot2.y)**2 + (dot1.z-dot2.z)**2),2))
	l.sort()
	while 0 in l:
		l.remove(0)
	mini=l[0]*1.05
	#Perspective : fais comme si un caméra regarde un objet 3D et qu'il se projette sur un plan entre les deux, selon les lignes qui vont de la camera à chaque point.

	for dot1 in points:
		coeff1=(distance_plan - dot1.x)/(camera.x - dot1.x)
		dot1.py=coeff1 * (camera.y-dot1.y)
		dot1.pz=coeff1 * (camera.z-dot1.z)
		for dot2 in points:
			coeff2=(distance_plan - dot2.x)/(camera.x - dot2.x)
			dot2.py=coeff2 * (camera.y-dot2.y)
			dot2.pz=coeff2 * (camera.z-dot2.z)
			if round(sqrt((dot1.x-dot2.x)**2 + (dot1.y-dot2.y)**2 + (dot1.z-dot2.z)**2),2)<= mini:
				Canevas.create_line(origine_x + dot1.py* unite,origine_y - dot1.pz* unite,origine_x + dot2.py* unite,origine_y - dot2.pz* unite,fill="blue")
		#create_text pour avoir les coos à côté des points et create_oval pour avoir la distance des points par rapport au plan visualisée (pour savoir s'il est avant ou après l'origine)
		#Canevas.create_text(origine_x + dot1.y* unite,origine_y - dot1.z* unite,text=dot1.nom)
		#Canevas.create_oval(origine_x + dot1.y * unite - rayon_point*(distance_plan+dot1.x*coeff_distance), origine_y - dot1.z * unite - rayon_point*(distance_plan+dot1.x*coeff_distance), origine_x + dot1.y * unite + rayon_point*(distance_plan+dot1.x*coeff_distance), origine_y - dot1.z * unite + rayon_point*(distance_plan+dot1.x*coeff_distance),outline="blue")

def affichage_repere(points):
	#debug(points)
	l=[]
	for dot1 in points:
		for dot2 in points:
			l.append(round(sqrt((dot1.x-dot2.x)**2 + (dot1.y-dot2.y)**2 + (dot1.z-dot2.z)**2),2))
	l.sort()
	while 0 in l:
		l.remove(0)
	mini=l[0]*1.05
	for dot1 in points:
		for dot2 in points:
			if round(sqrt((dot1.x-dot2.x)**2 + (dot1.y-dot2.y)**2 + (dot1.z-dot2.z)**2),2)<= mini:
				Canevas.create_line(origine_x + dot1.y* unite,origine_y - dot1.z* unite,origine_x + dot2.y* unite,origine_y - dot2.z* unite)
		Canevas.create_text(origine_x + dot1.y* unite,origine_y - dot1.z* unite,text=dot1.nom)
		#Canevas.create_oval(origine_x + dot1.y * unite - rayon_point*(distance_plan+dot1.x*coeff_distance), origine_y - dot1.z * unite - rayon_point*(distance_plan+dot1.x*coeff_distance), origine_x + dot1.y * unite + rayon_point*(distance_plan+dot1.x*coeff_distance), origine_y - dot1.z * unite + rayon_point*(distance_plan+dot1.x*coeff_distance),outline="blue")

def debug(points):
	print([vars(dot) for dot in points])




fenetre=Tk()
fenetre.attributes('-fullscreen', True)
Canevas=Canvas(fenetre,height=hauteur,width=largeur)
Canevas.pack(side=LEFT)



Ry=StringVar()
Ry.set(0)
angle_Ry=Scale(fenetre,  orient='vertical',  from_=360,  to=0,  resolution=1,  tickinterval=120,  label='Ry',  variable=Ry,  command=rotation_Ry)
angle_Ry.pack()

Rz=StringVar()
Rz.set(0)
angle_Rz=Scale(fenetre,  orient='horizontal',  from_=0,  to=360,  resolution=1,  tickinterval=120,  label='Rz',  variable=Rz,  command=rotation_Rz)
angle_Rz.pack()

deplacement_y=StringVar()
deplacement_y.set(0)
decalage_y=Scale(fenetre,  orient='horizontal',  from_=-3,  to=3,  resolution=0.1,  tickinterval=1,  label='y',  variable=deplacement_y,  command=deplace_y)
decalage_y.pack()

deplacement_z=StringVar()
deplacement_z.set(0)
decalage_z=Scale(fenetre,  orient='vertical',  from_=3,  to=-3,  resolution=0.1,  tickinterval=1,  label='z',  variable=deplacement_z,  command=deplace_z)
decalage_z.pack()



Bouton1 = Button(fenetre,  text = 'Quitter',  command = fenetre.destroy)
Bouton1.pack()




affichage_carre(carre)
affichage_repere(repere)

fenetre.mainloop()