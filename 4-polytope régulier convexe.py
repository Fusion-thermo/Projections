from tkinter import *
from math import sqrt, atan2, cos, sin, pi
import numpy as np
import itertools
from sympy.combinatorics import Permutation
import scipy.constants

g_ratio=scipy.constants.golden

hauteur=900
largeur=1150
origine_x=largeur//2
origine_y=hauteur//2
rayon_point=4
coeff_distance=2

'''
coordonnées cartésiennes pour l'affichage sur l'écran 2D cartésien et pour les 2 translations
matrices de rotation pour les rotations
il manque une rotation autour de x mais elle n'a pas d'intérêt, et une translation selon x sans intérêt
https://www.youtube.com/watch?v=iGO12Z5Lw8s
une lumière 4D éclaire l'objet le projetant en 3D. Puis on projette ces coos 3D sur l'écran 2D.

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
	def __init__(self,x,y,z,w=0,nom=""):
		#coos cartésiennes
		self.x=x
		self.y=y
		self.z=z
		self.w=w
		#Rxz
		self.phi2=atan2(x,z)
		self.phi_initial2=self.phi2
		#Rotations 4D
		self.db=0
		self.doublerotate_initial=0
		self.Rxy=0
		self.Rxy_initial=0
		self.Rzw=0
		self.Rzw_initial=0
		#point projeté en 3D
		self.x3d=0
		self.y3d=0
		self.z3d=0
		#point projeté en 2D
		self.y2d=0
		self.z2d=0


		if nom=="":
			self.nom=str((round(x,3),round(y,3),round(z,3)))
		else:
			self.nom=nom

	def rotate_Rxz(self,phi2):
		'''
		seul phi1 bouge
		on recalcule x, y z
		problème : le décalage indiqué sur l'écran avec les curseurs ne correspond plus au décalage réel.
		pour corriger ça et donc avoir un décalage cohérent pour tous les points, c'est la valeur d'origine dans "décalage par rapport à la valeur d'origine" qu'il faut changer
		donc je recalcule la valeur d'origine
		'''
		theta=(phi2+self.phi_initial2)-self.phi2
		self.phi2=self.phi_initial2+phi2

		coos=np.array([[self.x],[self.y],[self.z]])
		Rxz=np.array([[cos(theta),0,sin(theta)],[0,1,0],[-sin(theta),0,cos(theta)]])
		result=np.dot(Rxz,coos)
		self.x=result[0][0]
		self.y=result[1][0]
		self.z=result[2][0]

		if "(" in self.nom:
			self.nom=str((round(self.x,3),round(self.y,3),round(self.z,3)))

	def doublerotate(self,db):
		'''
		même principe, axe de la 4D mais avec 2 rotations en même temps
		'''
		theta=(db+self.doublerotate_initial)-self.db
		self.db=self.doublerotate_initial+db

		coos=np.array([[self.x],[self.y],[self.z],[self.w]])
		R=np.array([[cos(theta),-sin(theta),0,0],[sin(theta),cos(theta),0,0],[0,0,cos(theta),-sin(theta)],[0,0,sin(theta),cos(theta)]])
		result=np.dot(R,coos)
		self.x=result[0][0]
		self.y=result[1][0]
		self.z=result[2][0]
		self.w=result[3][0]

		if "(" in self.nom:
			self.nom=str((round(self.x,3),round(self.y,3),round(self.z,3)))

	def rotate_Rxy(self,Rxy):
		theta=(Rxy+self.Rxy_initial)-self.Rxy
		self.Rxy=self.Rxy_initial+Rxy

		coos=np.array([[self.x],[self.y],[self.z],[self.w]])
		R=np.array([[cos(theta),-sin(theta),0,0],[sin(theta),cos(theta),0,0],[0,0,1,0],[0,0,0,1]])
		result=np.dot(R,coos)
		self.x=result[0][0]
		self.y=result[1][0]
		self.z=result[2][0]
		self.w=result[3][0]

		if "(" in self.nom:
			self.nom=str((round(self.x,3),round(self.y,3),round(self.z,3)))

	def rotate_Rzw(self,Rzw):
		theta=(Rzw+self.Rzw_initial)-self.Rzw
		self.Rzw=self.Rzw_initial+Rzw

		coos=np.array([[self.x],[self.y],[self.z],[self.w]])
		R=np.array([[1,0,0,0],[0,1,0,0],[0,0,cos(theta),-sin(theta)],[0,0,sin(theta),cos(theta)]])
		result=np.dot(R,coos)
		self.x=result[0][0]
		self.y=result[1][0]
		self.z=result[2][0]
		self.w=result[3][0]

		if "(" in self.nom:
			self.nom=str((round(self.x,3),round(self.y,3),round(self.z,3)))
	def projections(self,objet):
		#3D
		coos=np.array([[self.x],[self.y],[self.z],[self.w]])
		coeff=1/(lumiere.w - self.w)
		R=np.array([[coeff,0,0,0],[0,coeff,0,0],[0,0,coeff,0]])
		result=np.dot(R,coos)
		self.x3d=result[0][0]
		self.y3d=result[1][0]
		self.z3d=result[2][0]

		#2D
		#Perspective : fais comme si un caméra regarde un objet 3D et qu'il se projette sur un plan entre les deux, selon les lignes qui vont de la camera à chaque point.
		coeff1=(objet.distance_plan - self.x3d)/(objet.camera.x - self.x3d)
		self.y2d=coeff1 * (objet.camera.y-self.y3d)
		self.z2d=coeff1 * (objet.camera.z-self.z3d)

lumiere=point(0,0,0,1.5)

class objet_4D:
	def __init__(self,points,longueur_arrete,unite,distance_plan,camera):
		self.points=points
		self.unite=unite
		self.longueur_arrete=longueur_arrete
		self.distance_plan=distance_plan
		self.camera=camera
		self.arretes=[]
		for dot1 in self.points:
			for dot2 in self.points:
				length=sqrt((dot1.x-dot2.x)**2 + (dot1.y-dot2.y)**2 + (dot1.z-dot2.z)**2 + (dot1.w-dot2.w)**2)
				if round(length,2)==round(self.longueur_arrete,2) and (dot1,dot2) not in self.arretes and (dot2,dot1) not in self.arretes:
					self.arretes.append((dot1,dot2))
		print("{} arrêtes".format(len(self.arretes)))

def rotation_Rxz(rien):
	global objet
	for dot in objet.points:
		dot.rotate_Rxz(radians(int(Rxz.get())))
	affichage_objet(objet)

def doublerotate(rien):
	global objet
	for dot in objet.points:
		dot.doublerotate(radians(int(Rw.get())))
	affichage_objet(objet)

def rotation_Rxy(rien):
	global objet
	for dot in objet.points:
		dot.rotate_Rxy(radians(int(Rxy.get())))
	affichage_objet(objet)

def rotation_Rzw(rien):
	global objet
	for dot in objet.points:
		dot.rotate_Rzw(radians(int(Rzw.get())))
	affichage_objet(objet)


def affichage_objet(objet):
	Canevas.delete(ALL)
	for dot in objet.points:
		dot.projections(objet)
		rayon=rayon_point*(objet.distance_plan-dot.x3d*coeff_distance)*(objet.distance_plan/objet.camera.x)
		Canevas.create_oval(origine_x + dot.y2d * objet.unite - rayon, origine_y - dot.z2d * objet.unite - rayon, origine_x + dot.y2d * objet.unite + rayon, origine_y - dot.z2d * objet.unite + rayon,outline="red",width=2)
		#create_text pour avoir les coos à côté des points et create_oval pour avoir la distance des points par rapport au plan visualisée (pour savoir s'il est avant ou après l'origine)
		#Canevas.create_text(origine_x + dot.y2d* objet.unite,origine_y - dot.z2d* objet.unite,text=dot.nom)
	for dots in objet.arretes:
		moyenne=(dots[0].x3d+dots[1].x3d)/2
		Canevas.create_line(origine_x + dots[0].y2d* objet.unite,origine_y - dots[0].z2d* objet.unite,origine_x + dots[1].y2d* objet.unite,origine_y - dots[1].z2d* objet.unite,fill="blue",width=(objet.distance_plan-moyenne)*(objet.distance_plan/objet.camera.x))


def initialisation():
	#all 6 convex regular 4-polytope = 4-polytope régulier convexe
	global objet
	choix=value.get()
	Rxz.set(0)
	Rw.set(0)
	Rxy.set(0)
	Rzw.set(0)

	if choix=="1":
		#5-cell
		coos=[point(1,1,1,-1/sqrt(5)),point(1,-1,-1,-1/sqrt(5)),point(-1,1,-1,-1/sqrt(5)),point(-1,-1,1,-1/sqrt(5)),point(0,0,0,4/sqrt(5))]
		longueur_arrete=2*sqrt(2)
		objet=objet_4D(coos,longueur_arrete,400,3,point(5,0,0))
	elif choix=="2":
		#8-cell
		coos_tesseract=permutations((0.5,0.5,0.5,0.5))[:]+permutations((-0.5,0.5,0.5,0.5))[:]+permutations((-0.5,-0.5,0.5,0.5))[:]+permutations((-0.5,-0.5,-0.5,0.5))[:]+permutations((-0.5,-0.5,-0.5,-0.5))[:]
		coos=[point(i[0],i[1],i[2],i[3]) for i in coos_tesseract]
		longueur_arrete=1
		objet=objet_4D(coos,longueur_arrete,880,3,point(5,0,0))
	elif choix=="3":
		#16 cell
		coos_hexadecachore=permutations((1,0,0,0))[:]+permutations((-1,0,0,0))[:]
		coos=[point(i[0],i[1],i[2],i[3]) for i in coos_hexadecachore]
		longueur_arrete=sqrt(2)
		objet=objet_4D(coos,longueur_arrete,700,3,point(5,0,0))
	elif choix=="4":
		#24-cell
		coos_icositetrachore=permutations((1,1,0,0))[:]+permutations((1,-1,0,0))[:]+permutations((-1,-1,0,0))[:]
		coos=[point(i[0],i[1],i[2],i[3]) for i in coos_icositetrachore]
		longueur_arrete=sqrt(2)
		objet=objet_4D(coos,longueur_arrete,300,3,point(5,0,0))
	elif choix=="5":
		#120-cell
		coos_hecatonicosachore=permutations((0,0,2,2))[:]+permutations((0,0,-2,2))[:]+permutations((0,0,-2,-2))[:]
		a=len(coos_hecatonicosachore)
		#print(a)
		coos_hecatonicosachore+=permutations((1,1,1,sqrt(5)))[:]+permutations((-1,1,1,sqrt(5)))[:]+permutations((-1,-1,1,sqrt(5)))[:]+permutations((-1,-1,-1,sqrt(5)))[:] + permutations((1,1,1,-sqrt(5)))[:]+permutations((-1,1,1,-sqrt(5)))[:]+permutations((-1,-1,1,-sqrt(5)))[:]+permutations((-1,-1,-1,-sqrt(5)))[:]
		b=len(coos_hecatonicosachore)
		#print(b-a)
		coos_hecatonicosachore+=permutations((g_ratio,g_ratio,g_ratio,1/g_ratio**2))[:]+permutations((-g_ratio,g_ratio,g_ratio,1/g_ratio**2))[:]+permutations((-g_ratio,-g_ratio,g_ratio,1/g_ratio**2))[:]+permutations((-g_ratio,-g_ratio,-g_ratio,1/g_ratio**2))[:] + permutations((g_ratio,g_ratio,g_ratio,-1/g_ratio**2))[:]+permutations((-g_ratio,g_ratio,g_ratio,-1/g_ratio**2))[:]+permutations((-g_ratio,-g_ratio,g_ratio,-1/g_ratio**2))[:]+permutations((-g_ratio,-g_ratio,-g_ratio,-1/g_ratio**2))[:]
		c=len(coos_hecatonicosachore)
		#print(c-b)
		coos_hecatonicosachore+=permutations((1/g_ratio,1/g_ratio,1/g_ratio,g_ratio**2))[:]+permutations((-1/g_ratio,1/g_ratio,1/g_ratio,g_ratio**2))[:]+permutations((-1/g_ratio,-1/g_ratio,1/g_ratio,g_ratio**2))[:]+permutations((-1/g_ratio,-1/g_ratio,-1/g_ratio,g_ratio**2))[:] + permutations((1/g_ratio,1/g_ratio,1/g_ratio,-g_ratio**2))[:]+permutations((-1/g_ratio,1/g_ratio,1/g_ratio,-g_ratio**2))[:]+permutations((-1/g_ratio,-1/g_ratio,1/g_ratio,-g_ratio**2))[:]+permutations((-1/g_ratio,-1/g_ratio,-1/g_ratio,-g_ratio**2))[:]
		d=len(coos_hecatonicosachore)
		#print(d-c)
		#print(a,b,c,d)

		permut=permutations((0,1,2,3))[:]
		parite_paire=[]
		for coos in permut:
			p=Permutation(coos)
			if p.parity()==1:
				parite_paire.append(coos)
		#print("paires",len(parite_paire))

		permut_coos1=[(0,1/g_ratio**2,1,g_ratio**2),(0,-1/g_ratio**2,1,g_ratio**2),(0,1/g_ratio**2,-1,g_ratio**2),(0,1/g_ratio**2,1,-g_ratio**2),(0,-1/g_ratio**2,-1,g_ratio**2),(0,1/g_ratio**2,-1,-g_ratio**2),(0,-1/g_ratio**2,1,-g_ratio**2),(0,-1/g_ratio**2,-1,-g_ratio**2)]
		#print(len(permut_coos1),len(parite_paire)*len(permut_coos1))
		permut_coos2=[(0,1/g_ratio,g_ratio,sqrt(5)),(0,-1/g_ratio,g_ratio,sqrt(5)),(0,1/g_ratio,-g_ratio,sqrt(5)),(0,1/g_ratio,g_ratio,-sqrt(5)),(0,-1/g_ratio,-g_ratio,sqrt(5)),(0,1/g_ratio,-g_ratio,-sqrt(5)),(0,-1/g_ratio,g_ratio,-sqrt(5)),(0,-1/g_ratio,-g_ratio,-sqrt(5))]
		#print(len(permut_coos2),len(parite_paire)*len(permut_coos2))
		permut_coos3=[(1/g_ratio,1,g_ratio,2),(-1/g_ratio,1,g_ratio,2),(1/g_ratio,-1,g_ratio,2),(1/g_ratio,1,-g_ratio,2),(1/g_ratio,1,g_ratio,-2),(-1/g_ratio,-1,g_ratio,2),(1/g_ratio,-1,-g_ratio,2),(1/g_ratio,1,-g_ratio,-2),(-1/g_ratio,1,g_ratio,-2),(-1/g_ratio,-1,-g_ratio,2),(1/g_ratio,-1,-g_ratio,-2),(-1/g_ratio,1,-g_ratio,-2),(-1/g_ratio,-1,g_ratio,-2),(-1/g_ratio,-1,-g_ratio,-2),(-1/g_ratio,1,-g_ratio,2),(1/g_ratio,-1,g_ratio,-2)]
		#print(len(permut_coos3),len(parite_paire)*len(permut_coos3))

		for paire in parite_paire:
			for coordonnes in permut_coos1:
				coos_hecatonicosachore.append((coordonnes[paire[0]],coordonnes[paire[1]],coordonnes[paire[2]],coordonnes[paire[3]]))
			for coordonnes in permut_coos2:
				coos_hecatonicosachore.append((coordonnes[paire[0]],coordonnes[paire[1]],coordonnes[paire[2]],coordonnes[paire[3]]))
			for coordonnes in permut_coos3:
				coos_hecatonicosachore.append((coordonnes[paire[0]],coordonnes[paire[1]],coordonnes[paire[2]],coordonnes[paire[3]]))

		coos=[point(i[0],i[1],i[2],i[3]) for i in coos_hecatonicosachore]
		#print(len(coos))
		longueur_arrete=2/g_ratio**2
		#print(longueur_arrete)
		objet=objet_4D(coos,longueur_arrete,700,30,point(1000,0,0))
	else:
		#600-cell
		coos_hexacosichore=permutations((1,0,0,0))[:]+permutations((-1,0,0,0))[:]
		a=len(coos_hexacosichore)
		#print(a)
		coos_hexacosichore+=permutations((0.5,0.5,0.5,0.5))[:]+permutations((-0.5,0.5,0.5,0.5))[:]+permutations((-0.5,-0.5,0.5,0.5))[:]+permutations((-0.5,-0.5,-0.5,0.5))[:]+permutations((-0.5,-0.5,-0.5,-0.5))[:]
		b=len(coos_hexacosichore)
		#print(b-a)
		permut=permutations((0,1,2,3))[:]
		parite_paire=[]
		for coos in permut:
			p=Permutation(coos)
			if p.parity()==1:
				parite_paire.append(coos)
		#print("paires",len(parite_paire))

		permut_coos=[(g_ratio/2, 0.5, 1/(g_ratio*2),0), (-g_ratio/2, 0.5, 1/(g_ratio*2),0), (g_ratio/2, -0.5, 1/(g_ratio*2),0), (g_ratio/2, 0.5, -1/(g_ratio*2),0), (-g_ratio/2, -0.5, 1/(g_ratio*2),0), (g_ratio/2, -0.5, -1/(g_ratio*2),0), (-g_ratio/2, 0.5, -1/(g_ratio*2),0), (-g_ratio/2, -0.5, -1/(g_ratio*2),0)]
		#print(len(permut_coos),len(parite_paire)*len(permut_coos))

		for paire in parite_paire:
			for coordonnes in permut_coos:
				coos_hexacosichore.append((coordonnes[paire[0]],coordonnes[paire[1]],coordonnes[paire[2]],coordonnes[paire[3]]))
		coos=[point(i[0],i[1],i[2],i[3]) for i in coos_hexacosichore]
		#print(len(coos))
		longueur_arrete=1/g_ratio
		objet=objet_4D(coos,longueur_arrete,700,3,point(5,0,0))

	affichage_objet(objet)


fenetre=Tk()
fenetre.attributes('-fullscreen', True)
Canevas=Canvas(fenetre,height=hauteur,width=largeur)
Canevas.pack(side=LEFT)


Rxz=StringVar()
Rxz.set(0)
angle_Rxz=Scale(fenetre,  orient='vertical',  from_=360,  to=0,  resolution=1,  tickinterval=120,  label='Rotation XZ',  variable=Rxz,  command=rotation_Rxz)
angle_Rxz.pack()

Rxy=StringVar()
Rxy.set(0)
angle_Rxy=Scale(fenetre,  orient='horizontal',  from_=0,  to=360,  resolution=1,  tickinterval=120,  label='Rotation XY',  variable=Rxy,  command=rotation_Rxy)
angle_Rxy.pack()

Rzw=StringVar()
Rzw.set(0)
angle_Rzw=Scale(fenetre,  orient='horizontal',  from_=0,  to=360,  resolution=1,  tickinterval=120,  label='Rotation ZW',  variable=Rzw,  command=rotation_Rzw)
angle_Rzw.pack()

Rw=StringVar()
Rw.set(0)
angle_Rw=Scale(fenetre,  orient='horizontal',  from_=0,  to=360,  resolution=1,  tickinterval=120,  label='Double rotation',  variable=Rw,  command=doublerotate)
angle_Rw.pack()

demarrer = Button(fenetre,  text = 'Start',  command = initialisation)
demarrer.pack()

value=StringVar()
value.set(2)
Choix1=Radiobutton(fenetre, text="Pentachore - 5 cell",variable=value, value=1)
Choix2=Radiobutton(fenetre, text="Tesseract - 8 cell",variable=value, value=2)
Choix3=Radiobutton(fenetre, text="Hexadécachore - 16 cell",variable=value, value=3)
Choix4=Radiobutton(fenetre, text="Icositétrachore - 24 cell",variable=value, value=4)
Choix5=Radiobutton(fenetre, text="Hécatonicosachore - 120 cell",variable=value, value=5)
Choix6=Radiobutton(fenetre, text="Hexacosichore - 600 cell",variable=value, value=6)
Choix1.pack()
Choix2.pack()
Choix3.pack()
Choix4.pack()
Choix5.pack()
Choix6.pack()

Bouton1 = Button(fenetre,  text = 'Quitter - Close',  command = fenetre.destroy)
Bouton1.pack()

fenetre.mainloop()