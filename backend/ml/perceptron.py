# -*- coding: utf-8 -*-
"""Perceptrón binario en NumPy, con sesgo incluido en el vector de pesos."""
import numpy as np
class Perceptron:
    def __init__(self, eta=0.1, max_epocas=1000, semilla=42): self.eta=eta; self.max_epocas=max_epocas; self.semilla=semilla
    def fit(self,X,y):
        rng=np.random.default_rng(self.semilla); X=np.asarray(X,float); y=np.asarray(y,int); Xb=np.c_[np.ones(len(X)),X]
        self.coef_=rng.normal(0,.01,Xb.shape[1]); self.errores_=[]; self.convergio_=False
        for _ in range(self.max_epocas):
            errores=0
            for xi,yi in zip(Xb,y):
                pred=int(np.dot(self.coef_,xi)>=0)
                if pred!=yi: self.coef_+=self.eta*(yi-pred)*xi; errores+=1
            self.errores_.append(errores)
            if errores==0: self.convergio_=True; break
        return self
    def decision_function(self,X): return np.c_[np.ones(len(X)),np.asarray(X,float)]@self.coef_
    def predict(self,X): return (self.decision_function(X)>=0).astype(int)
    def predict_proba(self,X):
        z=np.clip(self.decision_function(X),-30,30); p=1/(1+np.exp(-z)); return np.c_[1-p,p]
