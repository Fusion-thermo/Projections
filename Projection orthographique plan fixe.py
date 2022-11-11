from tkinter import *
from math import sqrt, acos, atan2, cos, sin, pi

hauteur=800
largeur=1100
origine_x=largeur//2
origine_y=hauteur//2
unite=50
rayon_point=1
distance_plan=20
coeff_distance=2

'''
coordonnées cartésiennes pour l'affichage sur l'écran 2D cartésien et pour les 2 translations
coordonnées sphériques pour le zoom (égal à une translation selon x si on était en perspective mais ce n'est pas le cas ici)
coos cylindriques ou sphériques pour les 2 rotations, peu importe lesquelles
il manque une rotation autour de x mais elle n'a pas d'intérêt, et une translation selon x sans intérêt avec cette projection

phi1 correspond au curseur phi et phi2 correspond au curseur theta
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
		#coos sphériques 1
		#avec ces notations : https://fr.wikipedia.org/wiki/Coordonn%C3%A9es_sph%C3%A9riques
		self.rho=sqrt(x**2 + y**2 + z**2)
		if self.rho!=0:
			self.theta1=acos(z/self.rho)
		else:
			self.theta1=0
		self.phi1=atan2(y,x)
		self.rho_initial=self.rho
		self.theta_initial1=self.theta1
		self.phi_initial1=self.phi1
		#coos sphériques 2
		#une sphère tournée de 90° autour de x : le z va vers le -y 
		if self.rho!=0:
			self.theta2=acos(-y/self.rho)
		else:
			self.theta2=0
		self.phi2=atan2(z,x)
		self.theta_initial2=self.theta2
		self.phi_initial2=self.phi2
		#décalages précédents
		self.decalage_y_prec=0
		self.decalage_z_prec=0


		if nom=="":
			self.nom=str((round(x,1),round(y,1),round(z,1)))
		else:
			self.nom=nom
	def zoom(self,rho):
		if self.rho_initial!=0:
			self.rho=self.rho_initial+rho
			self.x=self.rho*sin(self.theta1)*cos(self.phi1)
			self.y=self.rho*sin(self.theta1)*sin(self.phi1)
			self.z=self.rho*cos(self.theta1)
			if "(" in self.nom:
				self.nom=str((round(self.x,1),round(self.y,1),round(self.z,1)))

	def rotate_sphere1(self,phi):
		'''
		seul phi1 bouge
		on recalcule x, y z
		il faut donc recalculer theta2 et phi2
		problème : le décalage indiqué sur l'écran avec les curseurs ne correspond plus aud écalage réel.
		pour corriger ça et donc avoir un décalage cohérent pour tous les points, c'est la valeur d'origine dans "décalage par rapport à la valeur d'origine" qu'il faut changer
		donc je recalcule la valeur d'origine
		'''
		self.phi1=self.phi_initial1+phi
		self.x=self.rho*sin(self.theta1)*cos(self.phi1)
		self.y=self.rho*sin(self.theta1)*sin(self.phi1)
		self.z=self.rho*cos(self.theta1)

		if self.rho!=0:
			self.theta2=acos(-self.y/self.rho)
		else:
			self.theta2=0
		self.phi2=atan2(self.z,self.x)
		self.phi_initial2=self.phi2 - radians(int(theta.get()))

		if "(" in self.nom:
			self.nom=str((round(self.x,1),round(self.y,1),round(self.z,1)))
	
	def rotate_sphere2(self,phi2):
		'''
		sphère décalée de 90° par rapport à la première
		sinon même principe
		'''
		self.phi2=self.phi_initial2+phi2
		self.x=self.rho*sin(self.theta2)*cos(self.phi2)
		self.z=self.rho*sin(self.theta2)*sin(self.phi2)
		self.y=self.rho*-1*cos(self.theta2)

		if self.rho!=0:
			self.theta1=acos(self.z/self.rho)
		else:
			self.theta1=0
		self.phi1=atan2(self.y,self.x)
		self.phi_initial1=self.phi1 - radians(int(phi.get()))

		if "(" in self.nom:
			self.nom=str((round(self.x,1),round(self.y,1),round(self.z,1)))
	def deplace_y(self,y):
		#toutes les coos sphériques à recalculer
		if y-self.decalage_y_prec>0:
			self.y+=0.1
		else:
			self.y-=0.1
		self.decalage_y_prec=y

		self.rho=sqrt(self.x**2 + self.y**2 + self.z**2)
		self.rho_initial=self.rho-float(rho.get())
		if self.rho!=0:
			self.theta2=acos(-self.y/self.rho)
		else:
			self.theta2=0
		self.phi2=atan2(self.z,self.x)
		self.phi_initial2=self.phi2 - radians(int(theta.get()))
		if self.rho!=0:
			self.theta1=acos(self.z/self.rho)
		else:
			self.theta1=0
		self.phi1=atan2(self.y,self.x)
		self.phi_initial1=self.phi1 - radians(int(phi.get()))

	def deplace_z(self,z):
		if z-self.decalage_z_prec>0:
			self.z+=0.1
		else:
			self.z-=0.1
		self.decalage_z_prec=z

		self.rho=sqrt(self.x**2 + self.y**2 + self.z**2)
		self.rho_initial=self.rho-float(rho.get())
		if self.rho!=0:
			self.theta2=acos(-self.y/self.rho)
		else:
			self.theta2=0
		self.phi2=atan2(self.z,self.x)
		self.phi_initial2=self.phi2 - radians(int(theta.get()))
		if self.rho!=0:
			self.theta1=acos(self.z/self.rho)
		else:
			self.theta1=0
		self.phi1=atan2(self.y,self.x)
		self.phi_initial1=self.phi1 - radians(int(phi.get()))



longueur_repere=5
repere=[point(0,0,0,"0"),point(0,longueur_repere,0,"y"),point(longueur_repere,0,0,"x"),point(0,0,longueur_repere,"z")]
carre=[point(-1,-1,-1),point(-1,1,-1),point(1,1,-1),point(1,-1,-1),point(-1,-1,1),point(-1,1,1),point(1,1,1),point(1,-1,1)]
#carre=[point(1,1,1)]

def rotation_sphere1(rien,points=carre,points_repere=repere):
	for dot in points:
		dot.rotate_sphere1(radians(int(phi.get())))
	for dot in points_repere:
		dot.rotate_sphere1(radians(int(phi.get())))
	affichage_carre(points)
	affichage_repere(points_repere)

def rotation_sphere2(rien,points=carre,points_repere=repere):
	for dot in points:
		dot.rotate_sphere2(radians(int(theta.get())))
	for dot in points_repere:
		dot.rotate_sphere2(radians(int(theta.get())))
	affichage_carre(points)
	affichage_repere(points_repere)

def zoom(rien,points=carre,points_repere=repere):
	for dot in points:
		dot.zoom(float(rho.get()))
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
	#si on dit que le x des coos 3D est ramené à 0 alors tous les points sont sur un plan avec y et z comme coos en 2D : ombre du 3D sur un plan forme du 2D
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
				Canevas.create_line(origine_x + dot1.y* unite,origine_y - dot1.z* unite,origine_x + dot2.y* unite,origine_y - dot2.z* unite,fill="blue")
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

theta=StringVar()
theta.set(0)
angle_theta=Scale(fenetre,  orient='vertical',  from_=360,  to=0,  resolution=1,  tickinterval=120,  label='Theta',  variable=theta,  command=rotation_sphere2)
angle_theta.pack()

phi=StringVar()
phi.set(0)
angle_phi=Scale(fenetre,  orient='horizontal',  from_=0,  to=360,  resolution=1,  tickinterval=120,  label='Phi',  variable=phi,  command=rotation_sphere1)
angle_phi.pack()

rho=StringVar()
rho.set(0)
longueur_rho=Scale(fenetre,  orient='horizontal',  from_=0,  to=3,  resolution=0.1,  tickinterval=1,  label='Rho',  variable=rho,  command=zoom)
longueur_rho.pack()

deplacement_y=StringVar()
deplacement_y.set(0)
decalage_y=Scale(fenetre,  orient='horizontal',  from_=-3,  to=3,  resolution=0.1,  tickinterval=2,  label='y',  variable=deplacement_y,  command=deplace_y)
decalage_y.pack()

deplacement_z=StringVar()
deplacement_z.set(0)
decalage_z=Scale(fenetre,  orient='vertical',  from_=3,  to=-3,  resolution=0.1,  tickinterval=1,  label='z',  variable=deplacement_z,  command=deplace_z)
decalage_z.pack()

Bouton1 = Button(fenetre,  text = 'Quitter',  command = fenetre.destroy)
Bouton1.pack()

#Initiliase l'affichage

affichage_carre(carre)
affichage_repere(repere)

fenetre.mainloop()