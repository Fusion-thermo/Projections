from tkinter import *
import numpy as np

hauteur=800
largeur=1100
origine_x=largeur//2
origine_y=hauteur//2
unite=50
rayon_point=5
couleurs=["purple","red","cyan","blue","pink","green","orange","black"]


def affichage(points):


	for dot,couleur in zip(points,couleurs):
		Canevas.create_oval(origine_x + dot[0] * unite - rayon_point, origine_y - dot[1] * unite - rayon_point, origine_x + dot[0] * unite + rayon_point, origine_y - dot[1] * unite + rayon_point,fill=couleur,outline=couleur)


def milieu_solide(points):
	x=sum([i[0] for i in points])/len(points)
	y=sum([i[1] for i in points])/len(points)
	z=sum([i[2] for i in points])/len(points)
	return (x,y,z)

def reduire(vecteur):
	#Simplifie par -1 si c'est possible
	print(vecteur)
	negatif=0
	for i in vecteur:
		if i<0:
			negatif+=1
			
	if negatif==len(vecteur):
		for i in range(len(vecteur)):
			vecteur[i]*=-1
	print(",",vecteur)

	for i in range(100,1,-1):
		prec=vecteur[:]
		for j in range(len(vecteur)):
			vecteur[j]/=i
		different=False
		for j in range(len(vecteur)):
			if vecteur[j]!=round(vecteur[j],0):
				different=True
				break
		if different:
			vecteur=prec[:]

		print(i,vecteur)

	return [int(i) for i in vecteur]
#print(reduire([-25,-25,-25]))


class plan_projection:
	def __init__(self,points_plan,points_solide):
		#points A, B et C
		self.a=points_plan[0]
		self.b=points_plan[1]
		self.c=points_plan[2]
		#Calcul du coeff d, les coeff a,b et c sont les 3 coos de self.normale
		self.vecteur_directeur_1=[j-i for i,j in zip(self.a,self.b)]
		self.vecteur_directeur_2=[j-i for i,j in zip(self.a,self.c)]
		self.normale=reduire(np.cross(self.vecteur_directeur_1,self.vecteur_directeur_2))
		self.d=-sum([i*j for i,j in zip(self.normale,self.a)])

		print(self.normale,type(self.normale),self.d )

		point_milieu=milieu_solide(points_solide)
		self.x=projection_point(point_milieu,self)


def projection(points,plan):
	projetes=[]
	for dot in points:
		projetes.append(projection_point(dot,plan))
	return projetes


def projection_point(point, plan):
	# A=np.matrix([[i for i in points_plan[0]],[i for i in points_plan[1]],[i for i in points_plan[2]]])
	# liste=[]
	# coos=[points_plan[0],points_plan[1],points_plan[2]]

	# for dot in coos:
	# 	t=0
	# 	for i,j in zip(point,dot):
	# 		t+=i*j
	# 	t-=plan.d
	# 	liste.append([t])
	# B=np.matrix(liste)
	# X=np.dot(np.linalg.inv(A),B)
	# print("matrices\n",A,"\n",B,"\n",X,"\n",[float(i) for i in X])
	k=-(plan.normale[0]*point[0] + plan.normale[1]*point[1] + plan.normale[2]*point[2] + plan.d)/(plan.normale[0]**2 + plan.normale[1]**2 + plan.normale[2]**2)
	coos=[round(i+k,3) for i in point]
	print(plan.d, k, "coos",coos,"point",point)


	return coos

carre=[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]
#carre=[(-1,-1,-1),(1,-1,1),(1,1,-1),(-1,1,-1)]
points_plan=((1,5,1),(0,5,5),(5,5,0)) #de face
points_plan=((0,5,0),(5,0,0),(0,0,5)) #vue isométrique
plan=plan_projection(points_plan,carre)
print("plan",plan.a,plan.b,plan.c,plan.x, plan.normale, plan.d)
points_projetes=projection(carre,plan)
print(points_projetes)


# fenetre=Tk()
# fenetre.attributes('-fullscreen', True)
# Canevas=Canvas(fenetre,height=hauteur,width=largeur)
# Canevas.pack(side=LEFT)



# # angle=StringVar()
# # angle.set(45)
# # echelle_angle=Scale(fenetre,  orient='horizontal',  from_=90,  to=0,  resolution=1,  \
# # tickinterval=20,  label='Angle',  variable=angle,  command=demo_angle)
# # echelle_angle.pack()





# Bouton1 = Button(fenetre,  text = 'Quitter',  command = fenetre.destroy)
# Bouton1.pack()




# affichage(points_projetes)

# fenetre.mainloop()