from tkinter import *
from math import sqrt, acos, atan2, cos, sin, pi
import numpy as np

hauteur=800
largeur=1100
origine_x=largeur//2
origine_y=hauteur//2
unite=700
rayon_point=4
coeff_distance=2

'''
coordonnées cartésiennes pour l'affichage sur l'écran 2D cartésien et pour les 2 translations
matrices de rotation pour les rotations
il manque une rotation autour de x mais elle n'a pas d'intérêt, et une translation selon x sans intérêt
https://www.youtube.com/watch?v=iGO12Z5Lw8s
une lumière 4D éclaire le tesseract le projetant en 3D. Puis on projette ces coos 3D sur l'écran 2D.

'''

def radians(angle):
	return angle*pi/180

def degre(angle):
	return angle*180/pi


class point:
	def __init__(self,x,y,z,w=0,nom=""):
		#coos cartésiennes
		self.x=x
		self.y=y
		self.z=z
		self.w=w
		#Ry
		self.phi2=atan2(x,z)
		self.phi_initial2=self.phi2
		#Rotations 4D
		self.db=0
		self.doublerotate_initial=0
		self.Rxy=0
		self.Rxy_initial=0
		self.Rzw=0
		self.Rzw_initial=0
		#décalages précédents
		self.decalage_y_prec=0
		self.decalage_z_prec=0
		#point projeté en 3D
		self.x3d=0
		self.y3d=0
		self.z3d=0
		#point projeté en 2D
		self.y2d=0
		self.z2d=0


		if nom=="":
			self.nom=str((round(x,1),round(y,1),round(z,1)))
		else:
			self.nom=nom

	def rotate_Ry(self,phi2):
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
		Ry=np.array([[cos(theta),0,sin(theta)],[0,1,0],[-sin(theta),0,cos(theta)]])
		result=np.dot(Ry,coos)
		self.x=result[0][0]
		self.y=result[1][0]
		self.z=result[2][0]

		if "(" in self.nom:
			self.nom=str((round(self.x,1),round(self.y,1),round(self.z,1)))

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
			self.nom=str((round(self.x,1),round(self.y,1),round(self.z,1)))

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
			self.nom=str((round(self.x,1),round(self.y,1),round(self.z,1)))

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
			self.nom=str((round(self.x,1),round(self.y,1),round(self.z,1)))
	def projections(self):
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
		coeff1=(distance_plan - self.x3d)/(camera.x - self.x3d)
		self.y2d=coeff1 * (camera.y-self.y3d)
		self.z2d=coeff1 * (camera.z-self.z3d)


u=0.5 #0.5 pour un tesseract de côté 1
tesseract=[point(-u,-u,-u,u),point(-u,u,-u,u),point(u,u,-u,u),point(u,-u,-u,u),point(-u,-u,u,u),point(-u,u,u,u),point(u,u,u,u),point(u,-u,u,u),point(-u,-u,-u,-u),point(-u,u,-u,-u),point(u,u,-u,-u),point(u,-u,-u,-u),point(-u,-u,u,-u),point(-u,u,u,-u),point(u,u,u,-u),point(u,-u,u,-u)]
arretes=[]
for dot1 in tesseract:
	for dot2 in tesseract:
		if round(sqrt((dot1.x-dot2.x)**2 + (dot1.y-dot2.y)**2 + (dot1.z-dot2.z)**2 + (dot1.w-dot2.w)**2),2)==1 and (dot1,dot2) not in arretes and (dot2,dot1) not in arretes:
			arretes.append((dot1,dot2))
distance_plan=3
camera=point(5,0,0)
lumiere=point(0,0,0,1.5)

def rotation_Ry(rien,points=tesseract):
	for dot in points:
		dot.rotate_Ry(radians(int(Ry.get())))
	affichage_tesseract(points)

def doublerotate(rien,points=tesseract):
	for dot in points:
		dot.doublerotate(radians(int(Rw.get())))
	affichage_tesseract(points)

def rotation_Rxy(rien,points=tesseract):
	for dot in points:
		dot.rotate_Rxy(radians(int(Rxy.get())))
	affichage_tesseract(points)

def rotation_Rzw(rien,points=tesseract):
	for dot in points:
		dot.rotate_Rzw(radians(int(Rzw.get())))
	affichage_tesseract(points)


def affichage_tesseract(points):
	Canevas.delete(ALL)
	for dot in points:
		dot.projections()
		Canevas.create_oval(origine_x + dot.y2d * unite - rayon_point*(distance_plan-dot.x3d*coeff_distance), origine_y - dot.z2d * unite - rayon_point*(distance_plan-dot.x3d*coeff_distance), origine_x + dot.y2d * unite + rayon_point*(distance_plan-dot.x3d*coeff_distance), origine_y - dot.z2d * unite + rayon_point*(distance_plan-dot.x3d*coeff_distance),outline="red",width=2)
		#Canevas.create_text(origine_x + dot.y2d* unite,origine_y - dot.z2d* unite,text=dot.nom)
	for dots in arretes:
		moyenne=(dots[0].x3d+dots[1].x3d)/2
		Canevas.create_line(origine_x + dots[0].y2d* unite,origine_y - dots[0].z2d* unite,origine_x + dots[1].y2d* unite,origine_y - dots[1].z2d* unite,fill="blue",width=2.71**(distance_plan - moyenne)/5)




fenetre=Tk()
fenetre.attributes('-fullscreen', True)
Canevas=Canvas(fenetre,height=hauteur,width=largeur)
Canevas.pack(side=LEFT)



Ry=StringVar()
Ry.set(0)
angle_Ry=Scale(fenetre,  orient='vertical',  from_=360,  to=0,  resolution=1,  tickinterval=120,  label='Ry',  variable=Ry,  command=rotation_Ry)
angle_Ry.pack()

Rw=StringVar()
Rw.set(0)
angle_Rw=Scale(fenetre,  orient='horizontal',  from_=0,  to=360,  resolution=1,  tickinterval=120,  label='Rxy + Rzw',  variable=Rw,  command=doublerotate)
angle_Rw.pack()

Rxy=StringVar()
Rxy.set(0)
angle_Rxy=Scale(fenetre,  orient='horizontal',  from_=0,  to=360,  resolution=1,  tickinterval=120,  label='Rxy',  variable=Rxy,  command=rotation_Rxy)
angle_Rxy.pack()

Rzw=StringVar()
Rzw.set(0)
angle_Rzw=Scale(fenetre,  orient='horizontal',  from_=0,  to=360,  resolution=1,  tickinterval=120,  label='Rzw',  variable=Rzw,  command=rotation_Rzw)
angle_Rzw.pack()



Bouton1 = Button(fenetre,  text = 'Quitter',  command = fenetre.destroy)
Bouton1.pack()


affichage_tesseract(tesseract)

fenetre.mainloop()