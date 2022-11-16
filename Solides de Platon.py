from tkinter import *
from math import sqrt, atan2, cos, sin, pi
import numpy as np
import itertools
import scipy.constants

g_ratio=scipy.constants.golden

hauteur=800
largeur=1100
origine_x=largeur//2
origine_y=hauteur//2
rayon_point=3
coeff_distance=2

'''
coordonnées cartésiennes pour l'affichage sur l'écran 2D cartésien et pour les 2 translations
matrices de rotation pour les rotations
il manque une rotation autour de x mais elle n'a pas d'intérêt, et une translation selon x sans intérêt
la camera regarde l'objet et l'objet est projeté sur un plan selon la position de la camera.

'''

def radians(angle):
	return angle*pi/180

def permutations(coos):
	permut=list(itertools.permutations(coos))
	retour=[]
	for i in permut:
		if i not in retour:
			retour.append(i)
	return retour

def permutations_cycliques(coos):
	retour=[]
	n = len(coos)
	permut = [[coos[i - j] for i in range(n)] for j in range(n)]
	for i in permut:
		if i not in retour:
			retour.append(i)
	return retour

class point:
	def __init__(self,x,y,z,nom=""):
		#coos cartésiennes
		self.x=x
		self.y=y
		self.z=z
		self.x_initial=x
		self.y_initial=y
		self.z_initial=z
		#Rz
		self.phi1=atan2(y,x)
		self.phi_initial1=self.phi1
		#Ry
		self.phi2=atan2(x,z)
		self.phi_initial2=self.phi2
		#point projeté
		self.y2d=0
		self.z2d=0

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
		self.x=result[0][0]
		self.y=result[1][0]

		self.phi2=atan2(self.x,self.z)
		self.phi_initial2=self.phi2 - radians(int(Ry.get()))
		self.y_initial=self.y+float(deplacement_y.get())

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
		self.z=result[2][0]

		self.phi1=atan2(self.y,self.x)
		self.phi_initial1=self.phi1 - radians(int(Rz.get()))
		self.z_initial=self.z+float(deplacement_z.get())

		if "(" in self.nom:
			self.nom=str((round(self.x,1),round(self.y,1),round(self.z,1)))

	def deplace_y(self,y):
		self.y=self.y_initial+y

		self.phi2=atan2(self.x,self.z)
		self.phi_initial2=self.phi2 - radians(int(Ry.get()))
	
		self.phi1=atan2(self.y,self.x)
		self.phi_initial1=self.phi1 - radians(int(Rz.get()))

	def deplace_z(self,z):
		self.z=self.z_initial+z

		self.phi2=atan2(self.x,self.z)
		self.phi_initial2=self.phi2 - radians(int(Ry.get()))
		
		self.phi1=atan2(self.y,self.x)
		self.phi_initial1=self.phi1 - radians(int(Rz.get()))

	def projections(self,objet):
		coeff=(objet.distance_plan - self.x)/(objet.camera.x - self.x)
		self.y2d=coeff * (objet.camera.y-self.y)
		self.z2d=coeff * (objet.camera.z-self.z)


class objet_3D:
	def __init__(self,points,longueur_arrete,unite,distance_plan,camera):
		self.points=points
		self.unite=unite
		self.longueur_arrete=longueur_arrete
		self.distance_plan=distance_plan
		self.camera=camera
		self.arretes=[]
		for dot1 in self.points:
			for dot2 in self.points:
				length=sqrt((dot1.x-dot2.x)**2 + (dot1.y-dot2.y)**2 + (dot1.z-dot2.z)**2)
				if round(length,2)==round(self.longueur_arrete,2) and (dot1,dot2) not in self.arretes and (dot2,dot1) not in self.arretes:
					self.arretes.append((dot1,dot2))


def rotation_Ry(rien):
	global objet
	for dot in objet.points:
		dot.rotate_Ry(radians(int(Ry.get())))
	affichage_objet(objet)

def rotation_Rz(rien):
	global objet
	for dot in objet.points:
		dot.rotate_Rz(radians(int(Rz.get())))
	affichage_objet(objet)

def deplace_y(rien):
	global objet
	for dot in objet.points:
		dot.deplace_y(-float(deplacement_y.get()))
	affichage_objet(objet)

def deplace_z(rien):
	global objet
	for dot in objet.points:
		dot.deplace_z(-float(deplacement_z.get()))
	affichage_objet(objet)


def affichage_objet(objet):
	Canevas.delete(ALL)
	#Perspective : fais comme si un caméra regarde un objet 3D et qu'il se projette sur un plan entre les deux, selon les lignes qui vont de la camera à chaque point.

	for dot in objet.points:
		dot.projections(objet)
		rayon=rayon_point*(objet.distance_plan-dot.x*coeff_distance)*(objet.distance_plan/objet.camera.x)
		Canevas.create_oval(origine_x + dot.y2d * objet.unite - rayon, origine_y - dot.z2d * objet.unite - rayon, origine_x + dot.y2d * objet.unite + rayon, origine_y - dot.z2d * objet.unite + rayon,fill="red",width=2,outline="red")
		#create_text pour avoir les coos à côté des points et create_oval pour avoir la distance des points par rapport au plan visualisée (pour savoir s'il est avant ou après l'origine)
		#Canevas.create_text(origine_x + dot.y2d* objet.unite,origine_y - dot.z2d* objet.unite,text=dot.nom)
	for dots in objet.arretes:
		moyenne=(dots[0].x+dots[1].x)/2
		Canevas.create_line(origine_x + dots[0].y2d* objet.unite,origine_y - dots[0].z2d* objet.unite,origine_x + dots[1].y2d* objet.unite,origine_y - dots[1].z2d* objet.unite,fill="blue",width=(objet.distance_plan-moyenne)*(objet.distance_plan/objet.camera.x))

def initialisation():
	#all 6 convex regular 4-polytope = 4-polytope régulier convexe
	global objet
	choix=value.get()
	Ry.set(0)
	Rz.set(0)
	deplacement_y.set(0)
	deplacement_z.set(0)

	if choix=="1":
		#Tetraedre
		coos=[point(1,0,-1/sqrt(2)),point(-1,0,-1/sqrt(2)),point(0,1,1/sqrt(2)),point(0,-1,1/sqrt(2))]
		longueur_arrete=2
		objet=objet_3D(coos,longueur_arrete,600,5,point(10,0,0))
	elif choix=="2":
		#cube
		coos_cube=permutations((0.5,0.5,0.5))[:]+permutations((-0.5,0.5,0.5))[:]+permutations((-0.5,-0.5,0.5))[:]+permutations((-0.5,-0.5,-0.5))[:]
		coos=[point(i[0],i[1],i[2]) for i in coos_cube]
		longueur_arrete=1
		objet=objet_3D(coos,longueur_arrete,800,5,point(10,0,0))
	elif choix=="3":
		#Octaedre
		coos_octaedre=permutations((1,0,0))[:]+permutations((-1,0,0))[:]
		coos=[point(i[0],i[1],i[2]) for i in coos_octaedre]
		longueur_arrete=sqrt(2)
		objet=objet_3D(coos,longueur_arrete,700,5,point(10,0,0))
	elif choix=="4":
		#Dodecaedre
		coos_dodecaedre=permutations((1,1,1))[:]+permutations((-1,1,1))[:]+permutations((-1,-1,1))[:]+permutations((-1,-1,-1))[:]
		coos_dodecaedre+=permutations_cycliques((0,g_ratio,1/g_ratio))[:]+permutations_cycliques((0,-g_ratio,1/g_ratio))[:]+permutations_cycliques((0,g_ratio,-1/g_ratio))[:]+permutations_cycliques((0,-g_ratio,-1/g_ratio))[:]
		coos=[point(i[0],i[1],i[2]) for i in coos_dodecaedre]
		longueur_arrete=2/g_ratio
		objet=objet_3D(coos,longueur_arrete,400,5,point(10,0,0))
	else:
		#Icosaedre
		coos_icosaedre=permutations_cycliques((0,1,g_ratio))[:]+permutations_cycliques((0,-1,g_ratio))[:]+permutations_cycliques((0,1,-g_ratio))[:]+permutations_cycliques((0,-1,-g_ratio))[:]
		coos=[point(i[0],i[1],i[2]) for i in coos_icosaedre]	
		longueur_arrete=2
		objet=objet_3D(coos,longueur_arrete,400,5,point(10,0,0))

	affichage_objet(objet)


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

demarrer = Button(fenetre,  text = 'Start',  command = initialisation)
demarrer.pack()

value=StringVar()
value.set(2)
Choix1=Radiobutton(fenetre, text="Tetraèdre",variable=value, value=1)
Choix2=Radiobutton(fenetre, text="Cube",variable=value, value=2)
Choix3=Radiobutton(fenetre, text="Octaèdre",variable=value, value=3)
Choix4=Radiobutton(fenetre, text="Dodécaèdre",variable=value, value=4)
Choix5=Radiobutton(fenetre, text="Icosaèdre",variable=value, value=5)
Choix1.pack()
Choix2.pack()
Choix3.pack()
Choix4.pack()
Choix5.pack()

Bouton1 = Button(fenetre,  text = 'Quitter - Close',  command = fenetre.destroy)
Bouton1.pack()

fenetre.mainloop()