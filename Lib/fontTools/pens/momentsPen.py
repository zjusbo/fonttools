from __future__ import print_function, division, absolute_import
from fontTools.misc.py23 import *
from fontTools.pens.basePen import BasePen

class MomentsPen(BasePen):

	def __init__(self, glyphset=None):
		BasePen.__init__(self, glyphset)

		self.area = 0
		self.momentX = 0
		self.momentY = 0
		self.momentXX = 0
		self.momentXY = 0
		self.momentYY = 0

	def _moveTo(self, p0):
		self.__startPoint = p0

	def _closePath(self):
		p0 = self._getCurrentPoint()
		if p0 != self.__startPoint:
			self._lineTo(self.__startPoint)

	def _endPath(self):
		p0 = self._getCurrentPoint()
		if p0 != self.__startPoint:
			# Green theorem is not defined on open contours.
			raise NotImplementedError

	def _lineTo(self, p1):
		x0,y0 = self._getCurrentPoint()
		x1,y1 = p1

		r0 = x1*y0
		r1 = x1*y1
		r2 = x1**2
		r3 = x0**2
		r4 = 2*y0
		r5 = y0 - y1
		r6 = r5*x0
		r7 = y0**2
		r8 = y1**2
		r9 = x1**3
		r10 = r4*y1
		r11 = y0**3
		r12 = y1**3

		self.area += -r0/2 - r1/2 + x0*(y0 + y1)/2
		self.momentX += -r2*y0/6 - r2*y1/3 + r3*(r4 + y1)/6 - r6*x1/6
		self.momentY += -r0*y1/6 - r7*x1/6 - r8*x1/6 + x0*(r7 + r8 + y0*y1)/6
		self.momentXX += -r2*r6/12 - r3*r5*x1/12 - r9*y0/12 - r9*y1/4 + x0**3*(3*y0 + y1)/12
		self.momentXY += -r10*r2/24 - r2*r7/24 - r2*r8/8 + r3*(r10 + 3*r7 + r8)/24 - x0*x1*(r7 - r8)/12
		self.momentYY += -r0*r8/12 - r1*r7/12 - r11*x1/12 - r12*x1/12 + x0*(r11 + r12 + r7*y1 + r8*y0)/12

	def _qCurveToOne(self, p1, p2):
		x0,y0 = self._getCurrentPoint()
		x1,y1 = p1
		x2,y2 = p2

		r0 = 2*x1
		r1 = r0*y2
		r2 = 2*y1
		r3 = r2*x2
		r4 = 3*y2
		r5 = r4*x2
		r6 = 3*y0
		r7 = x1**2
		r8 = 2*y2
		r9 = x2**2
		r10 = 4*y1
		r11 = 10*y2
		r12 = r0*x2
		r13 = x0**2
		r14 = 10*y0
		r15 = x2*y2
		r16 = r0*y1 + r15
		r17 = 4*x1
		r18 = x2*y0
		r19 = r10*r15
		r20 = y1**2
		r21 = 2*r20
		r22 = y2**2
		r23 = r22*x2
		r24 = 5*r23
		r25 = y0**2
		r26 = y0*y2
		r27 = 5*r25
		r28 = 8*x1**3
		r29 = x2**3
		r30 = 30*y1
		r31 = 6*y1
		r32 = 10*r9*x1
		r33 = 4*r7
		r34 = 5*y2
		r35 = 12*r7
		r36 = r5 + 20*x1*y1
		r37 = 30*x1
		r38 = 12*x1
		r39 = 20*r7
		r40 = 8*r7*y1
		r41 = r34*r9
		r42 = 60*y1
		r43 = 20*r20
		r44 = 4*r20
		r45 = 15*r22
		r46 = r38*x2
		r47 = y1*y2
		r48 = 8*r20*x1 + r24
		r49 = 6*x1
		r50 = 8*y1**3
		r51 = y2**3
		r52 = y0**3
		r53 = 10*y1
		r54 = 12*y1
		r55 = 12*r20

		self.area += r1/6 - r3/6 - r5/6 + x0*(r2 + r6 + y2)/6 - y0*(r0 + x2)/6
		self.momentX += -r10*r9/30 - r11*r9/30 - r12*(-r8 + y1)/30 + r13*(r10 + r14 + y2)/30 + r7*r8/30 + x0*(r1 + r16 - r17*y0 - r18)/30 - y0*(r12 + 2*r7 + r9)/30
		self.momentY += r1*(r8 + y1)/30 - r19/30 - r21*x2/30 - r24/30 - r25*(r17 + x2)/30 + x0*(r10*y0 + r2*y2 + r21 + r22 + r26 + r27)/30 - y0*(r16 + r3)/30
		self.momentXX += r13*(r11*x1 - 5*r18 + r3 + r36 - r37*y0)/420 + r28*y2/420 - r29*r30/420 - r29*y2/4 - r32*(r2 - r4)/420 - r33*x2*(r2 - r34)/420 + x0**3*(r31 + 21*y0 + y2)/84 - x0*(-r15*r38 + r18*r38 + r2*r9 - r35*y2 + r39*y0 - r40 - r41 + r6*r9)/420 - y0*(r28 + 5*r29 + r32 + r35*x2)/420
		self.momentXY += r13*(r14*y2 + 3*r22 + 105*r25 + r42*y0 + r43 + 12*r47)/840 - r17*x2*(r44 - r45)/840 - r22*r9/8 - r25*(r39 + r46 + 3*r9)/840 + r33*y2*(r10 + r34)/840 - r42*r9*y2/840 - r43*r9/840 + x0*(-r10*r18 + r17*r26 + r19 + r22*r49 - r25*r37 - r27*x2 + r38*r47 + r48)/420 - y0*(r15*r17 + r31*r9 + r40 + r41 + r46*y1)/420
		self.momentYY += r1*(r11*y1 + r44 + r45)/420 - r15*r43/420 - r23*r30/420 - r25*(r1 + r36 + r53*x2)/420 - r50*x2/420 - r51*x2/12 - r52*(r49 + x2)/84 + x0*(r22*r53 + r22*r6 + r25*r30 + r25*r34 + r26*r54 + r43*y0 + r50 + 5*r51 + 35*r52 + r55*y2)/420 - y0*(-r0*r22 + r15*r54 + r48 + r55*x2)/420

	def _curveToOne(self, p1, p2, p3):
		x0,y0 = self._getCurrentPoint()
		x1,y1 = p1
		x2,y2 = p2
		x3,y3 = p3

		r0 = 6*x2
		r1 = r0*y3
		r2 = 6*y2
		r3 = 10*y3
		r4 = r3*x3
		r5 = 3*x1
		r6 = 3*y1
		r7 = 6*x1
		r8 = 3*x2
		r9 = 6*y1
		r10 = 3*y2
		r11 = x2**2
		r12 = r11*y3
		r13 = 45*r12
		r14 = x3**2
		r15 = r14*y2
		r16 = r14*y3
		r17 = x2*x3
		r18 = 15*r17
		r19 = 7*y3
		r20 = x1**2
		r21 = 9*r20
		r22 = x0**2
		r23 = 21*y1
		r24 = 9*r11
		r25 = 9*x2
		r26 = x2*y3
		r27 = 15*r26
		r28 = -r25*y1 + r27
		r29 = r25*y2
		r30 = r9*x3
		r31 = 45*x1
		r32 = x1*x3
		r33 = 45*r20
		r34 = 5*r14
		r35 = x2*y2
		r36 = 18*r35
		r37 = 5*x3
		r38 = r37*y3
		r39 = r31*y1 + r36 + r38
		r40 = x1*y0
		r41 = x1*y3
		r42 = x2*y0
		r43 = x3*y1
		r44 = r10*x3
		r45 = x3*y2*y3
		r46 = y2**2
		r47 = 45*r46
		r48 = r47*x3
		r49 = y3**2
		r50 = r49*x3
		r51 = y1**2
		r52 = 9*r51
		r53 = y0**2
		r54 = 21*x1
		r55 = x3*y2
		r56 = 15*r55
		r57 = 9*y2
		r58 = y2*y3
		r59 = 15*r58
		r60 = 9*r46
		r61 = 3*y3
		r62 = 45*y1
		r63 = r8*y3
		r64 = y0*y1
		r65 = y0*y2
		r66 = 30*r65
		r67 = 5*y3
		r68 = y1*y3
		r69 = 45*r51
		r70 = 5*r49
		r71 = x2**3
		r72 = x3**3
		r73 = 126*x3
		r74 = x1**3
		r75 = r14*x2
		r76 = 63*r11
		r77 = r76*x3
		r78 = 15*r35
		r79 = r19*x3
		r80 = x1*y1
		r81 = 63*r35
		r82 = r38 + 378*r80 + r81
		r83 = x1*y2
		r84 = x2*y1
		r85 = x3*y0
		r86 = x2*x3*y1
		r87 = x2*x3*y3
		r88 = r11*y2
		r89 = 27*r88
		r90 = 42*y3
		r91 = r14*r90
		r92 = 90*x1*x2
		r93 = 189*x2
		r94 = 30*x1*x3
		r95 = 14*r16 + 126*r20*y1 + 45*r88 + r94*y2
		r96 = x1*x2
		r97 = 252*r96
		r98 = x1*x2*y2
		r99 = 42*r32
		r100 = x1*x3*y1
		r101 = 30*r17
		r102 = 18*r17
		r103 = 378*r20
		r104 = 189*y2
		r105 = r20*y3
		r106 = r11*y1
		r107 = r14*y1
		r108 = 378*r46
		r109 = 252*y2
		r110 = y1*y2
		r111 = x2*x3*y2
		r112 = y0*y3
		r113 = 378*r51
		r114 = 63*r46
		r115 = 27*x2
		r116 = r115*r46 + 42*r50
		r117 = x2*y1*y3
		r118 = x3*y1*y2
		r119 = r49*x2
		r120 = r51*x3
		r121 = x3*y3
		r122 = 14*x3
		r123 = 30*r117 + r122*r49 + r47*x2 + 126*r51*x1
		r124 = x1*y1*y3
		r125 = x1*y2*y3
		r126 = x2*y1*y2
		r127 = 54*y3
		r128 = 21*r55
		r129 = 630*r53
		r130 = r46*x1
		r131 = r49*x1
		r132 = 126*r53
		r133 = y2**3
		r134 = y3**3
		r135 = 630*r49
		r136 = y1**3
		r137 = y0**3
		r138 = r114*y3 + r23*r49
		r139 = r49*y2

		self.area += r1/20 - r2*x3/20 - r4/20 + r5*(y2 + y3)/20 - r6*(x2 + x3)/20 + x0*(r10 + r9 + 10*y0 + y3)/20 - y0*(r7 + r8 + x3)/20
		self.momentX += r13/840 - r15/8 - r16/3 - r18*(r10 - r19)/840 + r21*(r10 + 2*y3)/840 + r22*(r2 + r23 + 56*y0 + y3)/168 + r5*(r28 + r29 - r30 + r4)/840 - r6*(10*r14 + r18 + r24)/840 + x0*(12*r26 + r31*y2 - r37*y0 + r39 - 105*r40 + 15*r41 - 30*r42 - 3*r43 + r44)/840 - y0*(18*r11 + r18 + r31*x2 + 12*r32 + r33 + r34)/840
		self.momentY += r27*(r10 + r19)/840 - r45/8 - r48/840 + r5*(10*r49 + r57*y1 + r59 + r60 + r9*y3)/840 - r50/6 - r52*(r8 + 2*x3)/840 - r53*(r0 + r54 + x3)/168 - r6*(r29 + r4 + r56)/840 + x0*(18*r46 + 140*r53 + r59 + r62*y2 + 105*r64 + r66 + r67*y0 + 12*r68 + r69 + r70)/840 - y0*(r39 + 15*r43 + 12*r55 - r61*x1 + r62*x2 + r63)/840
		self.momentXX += -r11*r73*(-r61 + y2)/9240 + r21*(r28 - r37*y1 + r44 + r78 + r79)/9240 + r22*(21*r26 - 630*r40 + 42*r41 - 126*r42 + r57*x3 + r82 + 210*r83 + 42*r84 - 14*r85)/9240 - r5*(r11*r62 + r14*r23 + 14*r15 - r76*y3 + 54*r86 - 84*r87 - r89 - r91)/9240 - r6*(27*r71 + 42*r72 + 70*r75 + r77)/9240 + 3*r71*y3/220 - 3*r72*y2/44 - r72*y3/4 + 3*r74*(r57 + r67)/3080 - r75*(378*y2 - 630*y3)/9240 + x0**3*(r57 + r62 + 165*y0 + y3)/660 + x0*(-18*r100 - r101*y0 - r101*y1 + r102*y2 - r103*y0 + r104*r20 + 63*r105 - 27*r106 - 9*r107 + r13 - r34*y0 - r76*y0 + 42*r87 + r92*y3 + r94*y3 + r95 - r97*y0 + 162*r98 - r99*y0)/9240 - y0*(135*r11*x1 + r14*r54 + r20*r93 + r33*x3 + 45*r71 + 14*r72 + 126*r74 + 42*r75 + r77 + r92*x3)/9240
		self.momentXY += -r108*r14/18480 + r12*(r109 + 378*y3)/18480 - r14*r49/8 - 3*r14*r58/44 - r17*(252*r46 - 1260*r49)/18480 + r21*(18*r110 + r3*y1 + 15*r46 + 7*r49 + 18*r58)/18480 + r22*(252*r110 + 28*r112 + r113 + r114 + 2310*r53 + 30*r58 + 1260*r64 + 252*r65 + 42*r68 + r70)/18480 - r52*(r102 + 15*r11 + 7*r14)/18480 - r53*(r101 + r103 + r34 + r76 + r97 + r99)/18480 + r7*(-r115*r51 + r116 + 18*r117 - 18*r118 + 42*r119 - 15*r120 + 28*r45 + r81*y3)/18480 - r9*(63*r111 + 42*r15 + 28*r87 + r89 + r91)/18480 + x0*(r1*y0 + r104*r80 + r112*r54 + 21*r119 - 9*r120 - r122*r53 + r123 + 54*r124 + 60*r125 + 54*r126 + r127*r35 + r128*y3 - r129*x1 + 81*r130 + 15*r131 - r132*x2 - r2*r85 - r23*r85 + r30*y3 + 84*r40*y2 - 84*r42*y1 + r60*x3)/9240 - y0*(54*r100 - 9*r105 + 81*r106 + 15*r107 + 54*r111 + r121*r7 + 21*r15 + r24*y3 + 60*r86 + 21*r87 + r95 + 189*r96*y1 + 54*r98)/9240
		self.momentYY += -r108*r121/9240 - r133*r73/9240 - r134*x3/12 - r135*r55/9240 - 3*r136*(r25 + r37)/3080 - r137*(r25 + r31 + x3)/660 + r26*(r135 + 126*r46 + 378*y2*y3)/9240 + r5*(r110*r127 + 27*r133 + 42*r134 + r138 + 70*r139 + r46*r62 + 27*r51*y2 + 15*r51*y3)/9240 - r52*(r56 + r63 + r78 + r79)/9240 - r53*(r128 + r25*y3 + 42*r43 + r82 + 42*r83 + 210*r84)/9240 - r6*(r114*x3 + r116 - 14*r119 + 84*r45)/9240 + x0*(r104*r51 + r109*r64 + 90*r110*y3 + r113*y0 + r114*y0 + r129*y1 + r132*y2 + 45*r133 + 14*r134 + 126*r136 + 770*r137 + r138 + 42*r139 + 135*r46*y1 + 14*r53*y3 + r64*r90 + r66*y3 + r69*y3 + r70*y0)/9240 - y0*(90*r118 + 63*r120 + r123 - 18*r124 - 30*r125 + 162*r126 - 27*r130 - 9*r131 + r36*y3 + 30*r43*y3 + 42*r45 + r48 + r51*r93)/9240

if __name__ == '__main__':
	from fontTools.misc.symfont import x, y, printGreenPen
	printGreenPen('MomentsPen', [
		      ('area', 1),
		      ('momentX', x),
		      ('momentY', y),
		      ('momentXX', x**2),
		      ('momentXY', x*y),
		      ('momentYY', y**2),
		     ])
