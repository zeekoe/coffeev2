import pygame
class KProgressBar:
	def __init__(self,scherm1,x,y,w,h,maxval):
		self.scherm = scherm1
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.maxval = maxval
		self.col1 = (0,0,255)
		self.col2 = (255,255,255)
	def update(self,value):
		curh = self.h - int(1.0 * value / self.maxval * self.h)
		pygame.draw.rect(self.scherm, self.col2, (self.x,self.y+self.h,self.w,-self.h),0)
		pygame.draw.rect(self.scherm, self.col1, (self.x,self.y+self.h,self.w,-curh),0)
	def setMaxval(self,maxval):
		self.maxval = maxval
	def setColors(self,col1,col2):
		self.col1 = col1
		self.col2 = col2
		
