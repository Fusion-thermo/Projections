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


'''
coordonnées cartésiennes pour l'affichage sur l'écran 2D cartésien et pour les 2 translations
matrices de rotation pour les rotations
il manque une rotation autour de x mais elle n'a pas d'intérêt, et une translation selon x sans intérêt
https://www.youtube.com/watch?v=iGO12Z5Lw8s
une lumière 4D éclaire l'objet le projetant en 3D. Puis on projette ces coos 3D sur l'écran 2D.

bug avec la lumière en tant que var, celle du 120 cell à 3.0 au lieu de 1.5 casse tout, jsp pk.
donc j'ai dû faire un paramètre spécial pour les points, ce n'est pas terrible mais cela règle le problème...

'''

def radian(angle):
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
	def __init__(self,x,y,z,w=0,nom="",hecatonicosachore=False):
		self.hecatonicosachore=hecatonicosachore
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
		self.projections()


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
	def projections(self):
		#3D
		coos=np.array([[self.x],[self.y],[self.z],[self.w]])
		#coeff=1/(float(lumiere_w_var.get()) - self.w) #bug, jsp pk
		if self.hecatonicosachore:
			coeff=1/(3 - self.w)
		else:
			coeff=1/(1.5 - self.w)
		R=np.array([[coeff,0,0,0],[0,coeff,0,0],[0,0,coeff,0]])
		result=np.dot(R,coos)
		self.x3d=result[0][0]
		self.y3d=result[1][0]
		self.z3d=result[2][0]

		#2D
		#Perspective : fais comme si un caméra regarde un objet 3D et qu'il se projette sur un plan entre les deux, selon les lignes qui vont de la camera à chaque point.
		coeff1=(int(distance_plan_var.get()) - self.x3d)/(int(camera_x_var.get()) - self.x3d)
		self.y2d=coeff1 * (-self.y3d)#(objet.camera.y-self.y3d) --> y=0
		self.z2d=coeff1 * (-self.z3d)#(objet.camera.z-self.z3d) --> z=0

#lumiere=point(0,0,0,1.5)

class objet_4D:
	def __init__(self,points,longueur_arrete):
		self.points=points
		self.longueur_arrete=longueur_arrete
		self.arretes=[]
		for dot1 in self.points:
			for dot2 in self.points:
				length=sqrt((dot1.x-dot2.x)**2 + (dot1.y-dot2.y)**2 + (dot1.z-dot2.z)**2 + (dot1.w-dot2.w)**2)
				if round(length,2)==round(self.longueur_arrete,2) and (dot1,dot2) not in self.arretes and (dot2,dot1) not in self.arretes:
					self.arretes.append((dot1,dot2))
		#on cherche le point moyen le plus proche et celui le plus éloigné pour l'affichage de la largeur des lignes
		moyenne_largeur=[(dots[0].x3d+dots[1].x3d)/2 for dots in self.arretes]
		self.min_moyenne_largeur=min(moyenne_largeur)
		self.max_moyenne_largeur=max(moyenne_largeur)
		#on cherche le point le plus éloigné et le point le plus proche pour trouver le rayon des points
		position_points=[dots[0].x3d for dots in self.arretes] + [dots[1].x3d for dots in self.arretes]
		self.min_distance_point=min(position_points)
		self.max_distance_point=max(position_points)
		#print(self.min_moyenne_largeur,self.max_moyenne_largeur, moyenne_largeur)
				
		print("{} arrêtes".format(len(self.arretes)))

def rotation_Rxz(rien):
	global objet
	for dot in objet.points:
		dot.rotate_Rxz(radian(int(Rxz.get())))
	affichage_objet(objet)

def doublerotate(rien):
	global objet
	for dot in objet.points:
		dot.doublerotate(radian(int(Rw.get())))
	affichage_objet(objet)

def rotation_Rxy(rien):
	global objet
	for dot in objet.points:
		dot.rotate_Rxy(radian(int(Rxy.get())))
	affichage_objet(objet)

def rotation_Rzw(rien):
	global objet
	for dot in objet.points:
		dot.rotate_Rzw(radian(int(Rzw.get())))
	affichage_objet(objet)


def affichage_objet(objet):
	Canevas.delete(ALL)
	unite=int(unite_var.get())
	for dot in objet.points:
		dot.projections()
		rayon = 10 - 9 * (dot.x3d - objet.min_distance_point)/(objet.max_distance_point - objet.min_distance_point)
		if rayon<0:
			rayon=0
		elif rayon>10:
			rayon=10
		Canevas.create_oval(origine_x + dot.y2d * unite - rayon, origine_y - dot.z2d * unite - rayon, origine_x + dot.y2d * unite + rayon, origine_y - dot.z2d * unite + rayon,outline="red",width=2)
		#create_text pour avoir les coos à côté des points et create_oval pour avoir la distance des points par rapport au plan visualisé
		#Canevas.create_text(origine_x + dot.y2d* unite,origine_y - dot.z2d* unite,text=dot.nom)
	for dots in objet.arretes:
		moyenne=(dots[0].x3d+dots[1].x3d)/2
		#largeur comprise entre 1 et 2
		largeur_ligne=2 - (moyenne - objet.min_moyenne_largeur)/(objet.max_moyenne_largeur - objet.min_moyenne_largeur)
		if largeur_ligne<1:
			largeur_ligne=1
		elif largeur_ligne>2:
			largeur_ligne=2
		Canevas.create_line(origine_x + dots[0].y2d* unite,origine_y - dots[0].z2d* unite,origine_x + dots[1].y2d* unite,origine_y - dots[1].z2d* unite,fill="blue",width = largeur_ligne)

def sign_change(coos):
	#attention : mets bien toutes les combinaisons de changement de signe, mais si 2 combinaisons sont des permutations alors elles ne sont pas ajoutées (puisqu'il va y avoir une permutation en sortie)
	#ex : comparer (1,1,1,1) et (3,4,5,6)
	signes=[(1,1,1,1),(-1,1,1,1),(-1,-1,1,1),(-1,-1,-1,1),(-1,-1,-1,-1)]
	sol=[]
	base_permut=[]
	for j in signes:
		for p in permutations(j):
			a=[]
			for i in range(4):
				a.append(p[i]*coos[i])
			b=a[:]
			b.sort()
			if (a[:]) not in sol and (b[:]) not in base_permut:
				sol.append((a[:]))
				base_permut.append((b[:]))
			
	return sol

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
		objet=objet_4D(coos,longueur_arrete)
		unite_var.set(400)
		distance_plan_var.set(3)
		camera_x_var.set(5)
		lumiere_w_var.set(1.5)
		vitesse_revolution.set(10)
	elif choix=="2":
		#8-cell
		coos_tesseract=[]
		for i in sign_change((0.5,0.5,0.5,0.5)):
			coos_tesseract+=permutations(i)[:]
		coos=[point(i[0],i[1],i[2],i[3]) for i in coos_tesseract]
		longueur_arrete=1
		objet=objet_4D(coos,longueur_arrete)
		unite_var.set(880)
		distance_plan_var.set(3)
		camera_x_var.set(5)
		lumiere_w_var.set(1.5)
		vitesse_revolution.set(10)
	elif choix=="3":
		#16 cell
		coos_hexadecachore=permutations((1,0,0,0))[:]+permutations((-1,0,0,0))[:]
		coos=[point(i[0],i[1],i[2],i[3]) for i in coos_hexadecachore]
		longueur_arrete=sqrt(2)
		objet=objet_4D(coos,longueur_arrete)
		unite_var.set(700)
		distance_plan_var.set(3)
		camera_x_var.set(5)
		lumiere_w_var.set(1.5)
		vitesse_revolution.set(10)
	elif choix=="4":
		#24-cell
		coos_icositetrachore=permutations((1,1,0,0))[:]+permutations((1,-1,0,0))[:]+permutations((-1,-1,0,0))[:]
		coos=[point(i[0],i[1],i[2],i[3]) for i in coos_icositetrachore]
		longueur_arrete=sqrt(2)
		objet=objet_4D(coos,longueur_arrete)
		unite_var.set(300)
		distance_plan_var.set(3)
		camera_x_var.set(5)
		lumiere_w_var.set(1.5)
		vitesse_revolution.set(10)
	elif choix=="5":
		#120-cell
		coos_hecatonicosachore=[]
		for i in sign_change((0,0,2,2)):
			coos_hecatonicosachore+=permutations(i)[:]
		for i in sign_change((1,1,1,sqrt(5))):
			coos_hecatonicosachore+=permutations(i)[:]
		for i in sign_change((g_ratio,g_ratio,g_ratio,1/g_ratio**2)):
			coos_hecatonicosachore+=permutations(i)[:]
		for i in sign_change((1/g_ratio,1/g_ratio,1/g_ratio,g_ratio**2)):
			coos_hecatonicosachore+=permutations(i)[:]

		permut=permutations((0,1,2,3))[:]
		parite_paire=[]
		for coos in permut:
			p=Permutation(coos)
			if p.parity():
				parite_paire.append(coos)

		permut_coos1=sign_change((0,1/g_ratio**2,1,g_ratio**2))
		permut_coos2=sign_change((0,1/g_ratio,g_ratio,sqrt(5)))
		permut_coos3=sign_change((1/g_ratio,1,g_ratio,2))

		for paire in parite_paire:
			for coordonnes in permut_coos1:
				coos_hecatonicosachore.append((coordonnes[paire[0]],coordonnes[paire[1]],coordonnes[paire[2]],coordonnes[paire[3]]))
			for coordonnes in permut_coos2:
				coos_hecatonicosachore.append((coordonnes[paire[0]],coordonnes[paire[1]],coordonnes[paire[2]],coordonnes[paire[3]]))
			for coordonnes in permut_coos3:
				coos_hecatonicosachore.append((coordonnes[paire[0]],coordonnes[paire[1]],coordonnes[paire[2]],coordonnes[paire[3]]))

		coos=[point(i[0],i[1],i[2],i[3],hecatonicosachore=True) for i in coos_hecatonicosachore]
		longueur_arrete=2/g_ratio**2
		objet=objet_4D(coos,longueur_arrete)
		unite_var.set(1000)
		distance_plan_var.set(400)
		camera_x_var.set(2700)
		lumiere_w_var.set(3.0)#bug avec cette valeur : si ce n'est pas 1.5 et qu'on passe du 120 au 600, les valeurs min et max des points sont incorrectes, ce qui perturbe la largeur des lignes et le rayon des cercles. 
		vitesse_revolution.set(50)
	elif choix=="6":
		#600-cell
		coos_hexacosichore=permutations((2,0,0,0))[:]+permutations((-2,0,0,0))[:]
		for i in sign_change((1,1,1,1)):
			coos_hexacosichore+=permutations(i)

		permut=permutations((0,1,2,3))[:]
		parite_paire=[]
		for coos in permut:
			p=Permutation(coos)
			if p.parity():
				parite_paire.append(coos)

		permut_coos=sign_change((g_ratio, 1, 1/(g_ratio),0))
		for paire in parite_paire:
			for coordonnes in permut_coos:
				coos_hexacosichore.append((coordonnes[paire[0]],coordonnes[paire[1]],coordonnes[paire[2]],coordonnes[paire[3]]))
		coos=[point(i[0],i[1],i[2],i[3]) for i in coos_hexacosichore]
		longueur_arrete=2/g_ratio
		objet=objet_4D(coos,longueur_arrete)
		unite_var.set(210)
		distance_plan_var.set(100)
		camera_x_var.set(500)
		lumiere_w_var.set(1.5)
		vitesse_revolution.set(30)

	#preuve du bug :
	# print(objet.max_distance_point, objet.min_distance_point,objet.min_moyenne_largeur,objet.max_moyenne_largeur)
	affichage_objet(objet)

revolution=0
revolution_angle_init=0
def revolution_xz():
	recursif = fenetre.after(int(vitesse_revolution.get()),revolution_xz)
	global objet, revolution, revolution_angle_init
	if revolution==0:
		revolution+=1
		revolution_angle_init=int(Rxz.get())
	elif revolution<360:
		revolution+=1
		teta=(revolution_angle_init+revolution)%360
		Rxz.set(teta)
		rotation_Rxz("")
	else:
		revolution=0
		fenetre.after_cancel(recursif)

def revolution_xy():
	recursif = fenetre.after(int(vitesse_revolution.get()),revolution_xy)
	global objet, revolution, revolution_angle_init
	if revolution==0:
		revolution+=1
		revolution_angle_init=int(Rxy.get())
	elif revolution<360:
		revolution+=1
		teta=(revolution_angle_init+revolution)%360
		Rxy.set(teta)
		rotation_Rxy("")
	else:
		revolution=0
		fenetre.after_cancel(recursif)

def revolution_zw():
	recursif = fenetre.after(int(vitesse_revolution.get()),revolution_zw)
	global objet, revolution, revolution_angle_init
	if revolution==0:
		revolution+=1
		revolution_angle_init=int(Rzw.get())
	elif revolution<360:
		revolution+=1
		teta=(revolution_angle_init+revolution)%360
		Rzw.set(teta)
		rotation_Rzw("")
	else:
		revolution=0
		fenetre.after_cancel(recursif)

def revolution_w():
	recursif = fenetre.after(int(vitesse_revolution.get()),revolution_w)
	global objet, revolution, revolution_angle_init
	if revolution==0:
		revolution+=1
		revolution_angle_init=int(Rw.get())
	elif revolution<360:
		revolution+=1
		teta=(revolution_angle_init+revolution)%360
		Rw.set(teta)
		doublerotate("")
	else:
		revolution=0
		fenetre.after_cancel(recursif)

def tester_parametres(rien):
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

Bouton1 = Button(fenetre,  text = 'Quitter - Close',  command = fenetre.destroy)
Bouton1.pack()

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

Revolution_xz = Button(fenetre,  text = 'Revolution xz',  command = revolution_xz)
Revolution_xz.pack()
Revolution_xy = Button(fenetre,  text = 'Revolution xy',  command = revolution_xy)
Revolution_xy.pack()
Revolution_zw = Button(fenetre,  text = 'Revolution zw',  command = revolution_zw)
Revolution_zw.pack()
Revolution_w = Button(fenetre,  text = 'Revolution w',  command = revolution_w)
Revolution_w.pack()



#Sliders pour trouver la meilleure visualisation de chaque objet
unite_var=StringVar()
unite_var.set(0)
#unite_scale=Scale(fenetre,  orient='horizontal',  from_=1,  to=1000,  resolution=1,  tickinterval=300,  label='Unité = zoom',  variable=unite_var, command=tester_parametres)
#unite_scale.pack()

distance_plan_var=StringVar()
distance_plan_var.set(0)
#distance_plan_scale=Scale(fenetre,  orient='horizontal',  from_=0,  to=500,  resolution=1,  tickinterval=250,  label='Distance du plan de projection',  variable=distance_plan_var, command=tester_parametres)
#distance_plan_scale.pack()

camera_x_var=StringVar()
camera_x_var.set(0)
#camera_x_scale=Scale(fenetre,  orient='horizontal',  from_=1,  to=3001,  resolution=1,  tickinterval=1500,  label='Distance de la caméra',  variable=camera_x_var, command=tester_parametres)
#camera_x_scale.pack()

lumiere_w_var=StringVar()
lumiere_w_var.set(0)
#lumiere_w_scale=Scale(fenetre,  orient='horizontal',  from_=0.1,  to=5,  resolution=0.1,  tickinterval=1,  label='Lumière',  variable=lumiere_w_var, command=tester_parametres)
#lumiere_w_scale.pack()

vitesse_revolution=StringVar()

fenetre.mainloop()