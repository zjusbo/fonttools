# -*- coding: utf-8 -*-
"""Calculate the perimeter of a glyph."""

from __future__ import print_function, division, absolute_import
from fontTools.misc.py23 import *
from fontTools.pens.basePen import BasePen
from fontTools.misc.bezierTools import splitQuadraticAtT, splitCubicAtT
import math


def _distance(p0, p1):
	return math.hypot(p0[0] - p1[0], p0[1] - p1[1])
def _dot(v1, v2):
    return (v1 * v2.conjugate()).real
def _intSecAtan(x):
	# In : sympy.integrate(sp.sec(sp.atan(x)))
	# Out: x*sqrt(x**2 + 1)/2 + asinh(x)/2
	return x * math.sqrt(x**2 + 1)/2 + math.asinh(x)/2

def _split_cubic_into_two(p0, p1, p2, p3):
    mid = (p0 + 3 * (p1 + p2) + p3) * .125
    deriv3 = (p3 + p2 - p1 - p0) * .125
    return ((p0, (p0 + p1) * .5, mid - deriv3, mid),
            (mid, mid + deriv3, (p2 + p3) * .5, p3))

class PerimeterPen(BasePen):

	def __init__(self, glyphset=None, tolerance=0.005):
		BasePen.__init__(self, glyphset)
		self.value = 0
		self._mult = 1.+1.5*tolerance # The 1.5 is a empirical hack; no math

		# Choose which algorithm to use for cubic. Recursive algorithm is
		# accurate to arbitrary tolerances whereas the Lobatto algorithm has
		# fixed error characteristics, but is faster.
		#
		# The 0.0015 cutoff has been empirically determined by measuring error
		# of the Lobatto approach on a realworld font.
		if tolerance < 0.0015:
			self._addCubic = self._addCubicRecursive
		else:
			self._addCubic = self._addCubicLobatto

	def _moveTo(self, p0):
		self.__startPoint = p0

	def _lineTo(self, p1):
		p0 = self._getCurrentPoint()
		self.value += _distance(p0, p1)

	def _qCurveToOne(self, p1, p2):
		# Analytical solution to the length of a quadratic bezier.
		# I'll explain how I arrived at this later.
		p0 = self._getCurrentPoint()
		_p1 = complex(*p1)
		d0 = _p1 - complex(*p0)
		d1 = complex(*p2) - _p1
		d = d1 - d0
		n = d * 1j
		scale = abs(n)
		if scale == 0.:
			self._lineTo(p2)
			return
		origDist = _dot(n,d0)
		if origDist == 0.:
			if _dot(d0,d1) >= 0:
				self._lineTo(p2)
				return
			assert 0 # TODO handle cusps
		x0 = _dot(d,d0) / origDist
		x1 = _dot(d,d1) / origDist
		Len = abs(2 * (_intSecAtan(x1) - _intSecAtan(x0)) * origDist / (scale * (x1 - x0)))
		self.value += Len

	def _addCubicRecursive(self, p0, p1, p2, p3):
		arch = abs(p0-p3)
		box = abs(p0-p1) + abs(p1-p2) + abs(p2-p3)
		if arch * self._mult >= box:
			self.value += (arch + box) * .5
		else:
			one,two = _split_cubic_into_two(p0,p1,p2,p3)
			self._addCubicRecursive(*one)
			self._addCubicRecursive(*two)

	def _addCubicLobatto(self, c0, c1, c2, c3, _q=(3/28)**.5):
		# Approximate length of cubic Bezier curve using Lobatto quadrature
		# with n=5 points: endpoints, midpoint, and at t=.5±sqrt(21)/14
		#
		# This, essentially, approximates the length-of-derivative function
		# to be integrated with the best-matching seventh-degree polynomial
		# approximation of it.
		#
		# https://en.wikipedia.org/wiki/Gaussian_quadrature#Gauss.E2.80.93Lobatto_rules

		v0 = abs(c1-c0)*3
		v4 = abs(c3-c2)*3
		v2 = abs(c3-c0+c2-c1)*.75

		# v1=(BezierCurveC[3].diff(t).subs({t:.5-_q}))
		# v3=(BezierCurveC[3].diff(t).subs({t:.5+_q}))
		# sp.cse([v1,v3], symbols=(sp.Symbol('r%d'%i) for i in count()))
		r0 = _q + 0.5
		r1 = 3*r0**2
		r2 = -_q + 0.5
		r3 = 3*r2**2
		r4 = 6*c2*r0*r2
		r5 = 3*c1
		r6 = 2*_q
		v1 = abs(-c0*r1 + c1*r1 - c2*r3 + c3*r3 + r2*r5*(-r6 - 1.0) + r4)
		v3 = abs(-c0*r3 + c1*r3 - c2*r1 + c3*r1 + r0*r5*(r6 - 1.0) + r4)

		self.value += (9*(v0+v4) + 64*v2 + 49*(v1+v3))/180

	def _curveToOne(self, p1, p2, p3):
		p0 = self._getCurrentPoint()
		self._addCubic(complex(*p0), complex(*p1), complex(*p2), complex(*p3))

	def _closePath(self):
		p0 = self._getCurrentPoint()
		if p0 != self.__startPoint:
			self.value += _distance(p0, self.__startPoint)
